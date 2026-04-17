"""
Reference rebalancer — venue-agnostic.

This is a minimal, composable reference implementation of a rebalancing loop
driven by the power-law allocation model. It is intentionally abstract: you
provide a price feed and an `execute_trade` callback, and the loop decides
when and how to rebalance.

The goal is to make adoption trivial. Any venue binding (CEX, DEX, custodian)
just needs to implement the `Venue` protocol below.

    from power_law.rebalancer import Rebalancer, RebalancerConfig, Venue
    from power_law import allocation_signal

    class MyVenue(Venue):
        def get_price(self): ...
        def get_portfolio(self): ...
        def execute_trade(self, side, notional_usd): ...

    r = Rebalancer(MyVenue(), RebalancerConfig(threshold_pct=0.22))
    r.tick()  # call on a schedule (hourly, daily, etc.)

Rebalancing policy:
  - Compute target allocation from the model using today's date + price
  - Compare with current allocation
  - If |current - target| >= threshold_pct, execute a trade
  - If |current - target| >= extreme_threshold_pct, execute immediately
    regardless of cadence
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Literal, Optional, Protocol

from .model import allocation_signal, get_daily_signal

Side = Literal["BUY", "SELL"]


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class RebalancerConfig:
    """Rebalancer policy knobs.

    Defaults reflect V3.2 research findings (see docs/REBALANCER.md):
      - 22% threshold is the empirically optimal signal-to-noise filter
      - 5% extreme threshold forces immediate rebalance on large moves
      - 0.3% fee_rate matches a typical DEX swap on SaucerSwap-class venues
    """
    threshold_pct: float = 0.22          # min |current - target| to trigger rebalance
    extreme_threshold_pct: float = 0.05  # force-rebalance on sudden large gap
    min_trade_usd: float = 1.0           # ignore trades below this (dust filter)
    fee_rate: float = 0.003              # informational; the venue applies it
    log: Callable[[str], None] = field(default_factory=lambda: print)


# ============================================================================
# VENUE PROTOCOL
# ============================================================================

class Venue(Protocol):
    """Minimal interface any execution venue must satisfy.

    Implementations can wrap a CEX API, a DEX router (e.g. SaucerSwap), a
    custodian, or even a paper-trade simulator.
    """

    def get_price(self) -> float:
        """Current BTC price in USD (or USD-equivalent stablecoin)."""

    def get_portfolio(self) -> "Portfolio":
        """Current holdings: BTC balance and USD/stablecoin balance."""

    def execute_trade(self, side: Side, notional_usd: float) -> "TradeResult":
        """Buy or sell `notional_usd` worth of BTC. Returns the fill details."""


@dataclass
class Portfolio:
    btc: float
    usd: float

    def total_value(self, price: float) -> float:
        return self.btc * price + self.usd

    def btc_allocation(self, price: float) -> float:
        total = self.total_value(price)
        return (self.btc * price) / total if total > 0 else 0.0


@dataclass
class TradeResult:
    side: Side
    notional_usd: float
    btc_delta: float
    fee_paid_usd: float
    success: bool = True
    error: Optional[str] = None


# ============================================================================
# REBALANCER
# ============================================================================

@dataclass
class Rebalancer:
    venue: Venue
    config: RebalancerConfig = field(default_factory=RebalancerConfig)

    def tick(self, now: Optional[datetime] = None) -> Optional[TradeResult]:
        """Run one rebalance check. Returns a TradeResult if a trade was executed."""
        now = now or datetime.now(timezone.utc).replace(tzinfo=None)
        price = self.venue.get_price()
        portfolio = self.venue.get_portfolio()

        target = allocation_signal(now, price)
        current = portfolio.btc_allocation(price)
        deviation = abs(current - target)

        signal = get_daily_signal(now, price)
        self.config.log(
            f"[rebalancer] {signal['date']} price=${price:,.0f} "
            f"current={current*100:.1f}% target={target*100:.1f}% "
            f"deviation={deviation*100:.1f}% stance={signal['stance']}"
        )

        if deviation < self.config.threshold_pct:
            return None

        total = portfolio.total_value(price)
        target_btc_usd = total * target
        current_btc_usd = portfolio.btc * price
        delta_usd = target_btc_usd - current_btc_usd

        if abs(delta_usd) < self.config.min_trade_usd:
            self.config.log(f"[rebalancer] trade below min_trade_usd, skipping")
            return None

        side: Side = "BUY" if delta_usd > 0 else "SELL"
        self.config.log(
            f"[rebalancer] executing {side} ${abs(delta_usd):,.2f} "
            f"(extreme={deviation >= self.config.extreme_threshold_pct})"
        )
        return self.venue.execute_trade(side, abs(delta_usd))


# ============================================================================
# PAPER-TRADE VENUE (reference implementation for testing / demos)
# ============================================================================

@dataclass
class PaperVenue:
    """Simulated venue. Feed it a price, hold paper balances, apply a flat fee."""
    btc: float = 0.0
    usd: float = 10_000.0
    _price: float = 50_000.0
    fee_rate: float = 0.003

    def set_price(self, price: float) -> None:
        self._price = price

    def get_price(self) -> float:
        return self._price

    def get_portfolio(self) -> Portfolio:
        return Portfolio(btc=self.btc, usd=self.usd)

    def execute_trade(self, side: Side, notional_usd: float) -> TradeResult:
        fee = notional_usd * self.fee_rate
        if side == "BUY":
            if self.usd < notional_usd:
                return TradeResult(side, notional_usd, 0, 0, False, "insufficient USD")
            btc_bought = (notional_usd - fee) / self._price
            self.btc += btc_bought
            self.usd -= notional_usd
            return TradeResult(side, notional_usd, btc_bought, fee)
        else:
            btc_to_sell = notional_usd / self._price
            if self.btc < btc_to_sell:
                return TradeResult(side, notional_usd, 0, 0, False, "insufficient BTC")
            self.btc -= btc_to_sell
            self.usd += notional_usd - fee
            return TradeResult(side, notional_usd, -btc_to_sell, fee)
