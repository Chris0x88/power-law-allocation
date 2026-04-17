"""
═══════════════════════════════════════════════════════════════════════════════
                  THE BITCOIN POWER-LAW ALLOCATION MODEL
                 Power-Law Floor + Halving Spikes + Heartbeat
═══════════════════════════════════════════════════════════════════════════════

Single task: for a given DATE and BTC PRICE, tell us what % of a portfolio
"should" be in Bitcoin right now.

Core ideas:
  FLOOR     = physics-style equilibrium (where price wants to be)
  CEILING   = cycle-dependent upside potential (decays by Kleiber's Law)
  HEARTBEAT = where we are in the current halving cycle
  SIGNAL    = how much BTC to hold (0-100%)

This module is deterministic, stateless, and self-contained:
  - Pure Python + numpy/pandas
  - Requires only a date and a price — no database, no history feed
  - No environment-specific paths or config
  - Freely portable into any app or backend

───────────────────────────────────────────────────────────────────────────────
CRITICAL: THIS MODEL IS LOCKED.
The constants below (FLOOR_A, FLOOR_B, SPIKE_A, KLEIBER, HALVING_BASE) were
calibrated to 15+ years of Bitcoin history. Do not change them without
re-running the full backtest. See docs/MODEL.md for derivation.
───────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


# ============================================================================
# CONSTANTS & HALVING SCHEDULE
# ============================================================================

GENESIS = datetime(2009, 1, 3)

# Power-law floor: log10(Floor) = FLOOR_A + FLOOR_B * log10(days_since_genesis)
FLOOR_A = -17.0       # log10 intercept, calibrated to full BTC history
FLOOR_B = 5.73        # power-law exponent (network / energy scaling)

# Spike envelope: max multiple above floor for a given halving cycle
#   Spike_max(cycle) = 1 + SPIKE_A * cycle^(-KLEIBER) * HALVING_BASE^(cycle-2)
SPIKE_A: float = 40.0       # initial spike amplitude (calibrated to early cycles)
KLEIBER: float = 0.75       # 3/4 scaling law (biological / fractal efficiency)
HALVING_BASE: float = 0.5   # impact of halvings decays geometrically

# Actual halving dates. Future halvings are projected from DAYS_PER_CYCLE.
HALVINGS = [
    datetime(2012, 11, 28),  # Halving 1
    datetime(2016, 7, 9),    # Halving 2
    datetime(2020, 5, 11),   # Halving 3
    datetime(2024, 4, 20),   # Halving 4
]
DAYS_PER_CYCLE = 1461  # ~4 years


def get_halving_date(n: int) -> datetime:
    """Return the date of the nth halving (1-indexed). Projects forward after halving 4."""
    if n < 1:
        raise ValueError("Halving number must be >= 1")
    if n <= len(HALVINGS):
        return HALVINGS[n - 1]
    last_known = HALVINGS[-1]
    cycles_ahead = n - len(HALVINGS)
    return last_known + timedelta(days=cycles_ahead * DAYS_PER_CYCLE)


# ============================================================================
# CORE MODEL FUNCTIONS (LOCKED)
# ============================================================================

def days_since_genesis(date: datetime) -> int:
    return max(1, (date - GENESIS).days)


def floor_price(date: datetime) -> float:
    """Power-law floor: where Bitcoin 'wants' to be in equilibrium."""
    d = days_since_genesis(date)
    return 10 ** (FLOOR_A + FLOOR_B * math.log10(d))


def cycle_index(date: datetime) -> int:
    """Halving cycle index. Cycle 1 = pre-first-halving, Cycle 5 = current (post-2024)."""
    for i, h in enumerate(HALVINGS):
        if date < h:
            return i + 1
    last_halving = HALVINGS[-1]
    days_since_last = (date - last_halving).days
    return len(HALVINGS) + 1 + int(days_since_last / DAYS_PER_CYCLE)


def spike_max(c: float) -> float:
    """Max spike multiple above floor for a given (continuous) cycle index."""
    kleiber_term = c ** (-KLEIBER)
    halving_term = HALVING_BASE ** (c - 2)
    return 1 + SPIKE_A * kleiber_term * halving_term


def cycle_progress_raw(date: datetime) -> float:
    """Raw cycle progress (0.0 to 1.0) within the current halving cycle."""
    c = cycle_index(date)

    if c <= len(HALVINGS):
        cycle_start = GENESIS if c == 1 else HALVINGS[c - 2]
        cycle_end = HALVINGS[c - 1]
    else:
        cycle_start = get_halving_date(c - 1) if c > 1 else GENESIS
        cycle_end = get_halving_date(c)

    cycle_length = (cycle_end - cycle_start).days
    days_in = (date - cycle_start).days

    if cycle_length <= 0:
        return 0.0
    return min(1.0, max(0.0, days_in / cycle_length))


def cycle_progress(date: datetime) -> float:
    return cycle_progress_raw(date)


def ceiling_price(date: datetime) -> float:
    """Continuous cycle ceiling that intersects speculative peaks at 33% cycle progress.

    Uses a peak-centred effective cycle index c_peak = c + (p - 0.33) so the
    envelope is smooth across halving boundaries and lands on the integer cycle
    value at the expected peak.
    """
    c = cycle_index(date)
    p = cycle_progress_raw(date)
    c_peak = c + (p - 0.33)
    return floor_price(date) * spike_max(c_peak)


def heartbeat_pulse(progress: float, cycle: int = 5) -> float:
    """Asymmetric 'Up the Escalator, Down the Elevator' pulse.

    - w_up = 0.18: slow multi-year build to peak (escalator)
    - w_down = 0.08 + 0.01·cycle: sharper crash, slightly widens with maturity
    - Peak at progress = 0.33
    - Boundary-pinned so the pulse equals 0 at progress = 0 and progress = 1
    """
    peak = 0.33
    w_up = 0.18
    w_down = 0.08 + (cycle * 0.01)

    if progress < peak:
        val = math.exp(-((progress - peak) ** 2) / (2 * w_up ** 2))
    else:
        val = math.exp(-((progress - peak) ** 2) / (2 * w_down ** 2))

    v0 = math.exp(-((-peak) ** 2) / (2 * w_up ** 2))
    v1 = math.exp(-((1 - peak) ** 2) / (2 * w_down ** 2))
    offset = v0 * (1 - progress) + v1 * progress
    return max(0.0, val - offset)


def model_price(date: datetime) -> float:
    """Model fair value: floor + heartbeat * (ceiling - floor)."""
    fl = floor_price(date)
    ceil = ceiling_price(date)
    p = cycle_progress(date)
    c = cycle_index(date)
    hb = heartbeat_pulse(p, c)
    return fl + (ceil - fl) * hb


def position_score(date: datetime, price: float) -> float:
    """Normalised position of price between floor and ceiling. 0 = floor, 1 = ceiling."""
    fl = floor_price(date)
    ceil = ceiling_price(date)
    if price <= fl:
        return 0.0
    if price >= ceil:
        return 1.0
    return (price - fl) / (ceil - fl)


def shifted_heartbeat(date: datetime, shift_days: int = 90) -> float:
    """Heartbeat value shift_days in the future — used as a momentum indicator."""
    future_date = date + timedelta(days=shift_days)
    return heartbeat_pulse(cycle_progress(future_date), cycle_index(future_date))


def allocation_signal(date: datetime, price: float, shift_days: int = 90) -> float:
    """Recommended BTC allocation (0.0 – 1.0).

    Composed of:
      1. Value component: sigmoid on position-in-band (aggressive at extremes)
      2. Cycle phase penalty: 0-50% haircut between 35%-85% cycle progress
         (avoid catching falling knives in post-peak bear markets)
      3. Momentum tilt: ± up to 10% based on 90-day forward heartbeat change
      4. Floor boost: up to +30% when in the deepest value zone (position < 15%)

    Core principle: 'Is Bitcoin cheap or expensive right now?'
    """
    pos = position_score(date, price)
    prog = cycle_progress(date)

    # 1. Value: sigmoid on position-equivalent z-score
    z_equiv = (pos - 0.5) * 4  # 0 → -2, 0.5 → 0, 1 → +2
    value_alloc = 1.0 / (1.0 + math.exp(z_equiv * 2.0))

    # 2. Phase penalty (post-peak cooldown)
    phase_penalty = 0.0
    if 0.35 <= prog <= 0.85:
        if prog <= 0.55:
            phase_penalty = (prog - 0.35) / 0.20 * 0.50
        elif prog <= 0.70:
            phase_penalty = 0.50
        else:
            phase_penalty = (0.85 - prog) / 0.15 * 0.50

    # 3. Momentum tilt
    c = cycle_index(date)
    hb_now = heartbeat_pulse(prog, c)
    hb_future = shifted_heartbeat(date, shift_days)
    momentum_delta = max(-0.10, min(0.10, (hb_future - hb_now) * 0.3))

    raw_alloc = value_alloc - phase_penalty + momentum_delta

    # 4. Floor boost (scaled inversely with phase penalty — no catching knives)
    FLOOR_BOOST = 0.30
    DEEP_VALUE_THRESHOLD = 0.15
    VALUE_THRESHOLD = 0.30
    boost_scale = max(0.0, 1.0 - phase_penalty * 2)

    if pos < DEEP_VALUE_THRESHOLD:
        boost_factor = (DEEP_VALUE_THRESHOLD - pos) / DEEP_VALUE_THRESHOLD
        raw_alloc += FLOOR_BOOST * boost_factor * boost_scale
    elif pos < VALUE_THRESHOLD:
        boost_factor = (VALUE_THRESHOLD - pos) / (VALUE_THRESHOLD - DEEP_VALUE_THRESHOLD)
        raw_alloc += FLOOR_BOOST * 0.5 * boost_factor * boost_scale

    return max(0.0, min(1.0, raw_alloc))


# ============================================================================
# LABELS & HUMAN-READABLE SIGNAL
# ============================================================================

def sentiment_tags(date: datetime, price: float) -> Dict[str, object]:
    c = cycle_index(date)
    prog = cycle_progress(date)
    pos = position_score(date, price)
    alloc = allocation_signal(date, price)

    if prog < 0.15:
        phase = "early_cycle_reset"
    elif prog < 0.35:
        phase = "pre_peak_build_up"
    elif prog < 0.55:
        phase = "late_cycle_peak_zone"
    elif prog < 0.8:
        phase = "post_peak_cooldown"
    else:
        phase = "late_cycle_washout"

    if pos < 0.2:
        valuation = "deep_value"
    elif pos < 0.4:
        valuation = "undervalued"
    elif pos < 0.6:
        valuation = "mid_band"
    elif pos < 0.8:
        valuation = "overvalued"
    else:
        valuation = "euphoria"

    if alloc > 0.8:
        stance = "max_accumulate"
    elif alloc > 0.6:
        stance = "accumulate"
    elif alloc > 0.4:
        stance = "balanced"
    elif alloc > 0.2:
        stance = "trim_exposure"
    else:
        stance = "capital_protection"

    return {
        "cycle_phase": phase,
        "valuation_state": valuation,
        "allocation_stance": stance,
        "cycle_index": c,
        "cycle_progress_pct": round(prog * 100, 1),
        "position_pct": round(pos * 100, 1),
        "allocation_pct": round(alloc * 100, 1),
    }


def generate_tagline(date: datetime, price: float) -> str:
    tags = sentiment_tags(date, price)
    alloc = tags["allocation_pct"]
    pos = tags["position_pct"]
    prog = tags["cycle_progress_pct"]
    phase = tags["cycle_phase"].replace("_", " ").title()
    valuation = tags["valuation_state"].replace("_", " ")
    c = tags["cycle_index"]

    if alloc >= 70:
        action = "Strong accumulation"
    elif alloc >= 50:
        action = "Favorable accumulation"
    elif alloc >= 35:
        action = "Neutral positioning"
    elif alloc >= 20:
        action = "Reduce exposure"
    else:
        action = "Capital protection"

    return (
        f"Cycle {c} | {prog:.0f}% through cycle | {phase} | "
        f"Price at {pos:.0f}% of range ({valuation}) | "
        f"{action}: {alloc:.0f}% BTC"
    )


def get_daily_signal(date: datetime, price: float) -> Dict:
    """Primary API. Returns the full signal package for a given date and price."""
    alloc = allocation_signal(date, price)
    tags = sentiment_tags(date, price)
    return {
        "date": date.strftime("%Y-%m-%d"),
        "price": price,
        "allocation_pct": round(alloc * 100, 1),
        "floor": round(floor_price(date), 2),
        "ceiling": round(ceiling_price(date), 2),
        "model_price": round(model_price(date), 2),
        "position_in_band_pct": tags["position_pct"],
        "cycle": tags["cycle_index"],
        "cycle_progress_pct": tags["cycle_progress_pct"],
        "phase": tags["cycle_phase"],
        "valuation": tags["valuation_state"],
        "stance": tags["allocation_stance"],
        "tagline": generate_tagline(date, price),
    }


def get_future_projections(date: datetime, current_price: float) -> Dict:
    """Project floor, fair value, and allocation for 1M–36M out.

    Allocation assumes the current price persists — shows how the model's view
    of today's price evolves as time alone passes.
    """
    periods = [
        ("1M", 30), ("3M", 91), ("6M", 182),
        ("12M", 365), ("24M", 730), ("36M", 1095),
    ]
    projections = []
    for label, days in periods:
        future_date = date + timedelta(days=days)
        projections.append({
            "period": label,
            "days_out": days,
            "date": future_date.strftime("%Y-%m-%d"),
            "floor": round(floor_price(future_date), 0),
            "model_price": round(model_price(future_date), 0),
            "ceiling": round(ceiling_price(future_date), 0),
            "allocation_pct": round(allocation_signal(future_date, current_price) * 100, 0),
        })
    return {
        "as_of": date.strftime("%Y-%m-%d"),
        "current_price": current_price,
        "projections": projections,
    }


# ============================================================================
# PORTFOLIO / BACKTEST SUPPORT
# ============================================================================

@dataclass
class PortfolioState:
    btc: float
    usd: float

    def total_value(self, price: float) -> float:
        return self.btc * price + self.usd


def rebalance_to_target(
    state: PortfolioState,
    price: float,
    target_alloc: float,
    fee_rate: float = 0.003,
) -> PortfolioState:
    """Rebalance to target BTC fraction, applying a proportional fee on traded notional."""
    total = state.total_value(price)
    if total <= 0:
        return state

    target_btc = (total * target_alloc) / price
    target_usd = total * (1.0 - target_alloc)

    trade_notional = abs(target_btc - state.btc) * price
    fee = trade_notional * fee_rate

    return PortfolioState(btc=target_btc, usd=target_usd - fee)


def _normalise_price_data(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    if "date" not in data.columns:
        raise ValueError("DataFrame must contain a 'date' column")
    price_col = "close" if "close" in data.columns else "price"
    if price_col not in data.columns:
        raise ValueError("DataFrame must contain a 'close' or 'price' column")
    data["date"] = pd.to_datetime(data["date"])
    data = data.sort_values("date").reset_index(drop=True)
    data["price"] = data[price_col].astype(float)
    return data


def backtest(
    df: pd.DataFrame,
    start_date: Optional[datetime] = None,
    fee_rate: float = 0.003,
    rebalance_days: int = 30,
    threshold_pct: float = 0.0,
) -> Dict[str, float]:
    """Backtest the strategy against buy-and-hold on a daily BTC price series.

    Args:
        df: DataFrame with columns ['date', 'close' or 'price'].
        start_date: Optional start filter.
        fee_rate: Fee per trade as a fraction (0.003 = 0.30%).
        rebalance_days: Minimum days between forced rebalances.
        threshold_pct: If > 0, rebalance early when |current_alloc - target_alloc|
                       exceeds this fraction (e.g. 0.22 = 22% threshold).

    Returns a dict of performance metrics vs HODL.
    """
    data = _normalise_price_data(df)
    if start_date is not None:
        data = data[data["date"] >= start_date].reset_index(drop=True)
    if len(data) < rebalance_days + 5:
        raise ValueError("Not enough data for backtest")

    initial_price = float(data["price"].iloc[0])
    initial_capital = 100.0

    state = PortfolioState(btc=0.0, usd=initial_capital)
    bh_fee = initial_capital * fee_rate
    bh = PortfolioState(btc=(initial_capital - bh_fee) / initial_price, usd=0.0)

    last_rebalance_idx = 0
    trade_count = 0
    pv, bv = [initial_capital], [initial_capital]

    for i, row in data.iterrows():
        if i == 0:
            continue
        dt = row["date"].to_pydatetime()
        price = float(row["price"])

        days_since = i - last_rebalance_idx
        target = allocation_signal(dt, price)
        current = (state.btc * price) / state.total_value(price) if state.total_value(price) > 0 else 0
        deviation = abs(current - target)

        should_rebalance = False
        if days_since >= rebalance_days and (threshold_pct == 0.0 or deviation >= threshold_pct):
            should_rebalance = True
        elif threshold_pct > 0 and deviation >= threshold_pct:
            should_rebalance = True

        if should_rebalance:
            state = rebalance_to_target(state, price, target, fee_rate)
            last_rebalance_idx = i
            trade_count += 1

        pv.append(state.total_value(price))
        bv.append(bh.total_value(price))

    final_price = float(data["price"].iloc[-1])
    strat_final = state.total_value(final_price)
    bh_final = bh.total_value(final_price)
    years = len(data) / 365.0

    pv_arr, bv_arr = np.array(pv), np.array(bv)
    strat_dd = float(np.min((pv_arr - np.maximum.accumulate(pv_arr)) / np.maximum.accumulate(pv_arr)))
    bh_dd = float(np.min((bv_arr - np.maximum.accumulate(bv_arr)) / np.maximum.accumulate(bv_arr)))
    strat_returns = np.diff(pv_arr) / pv_arr[:-1]
    sharpe = float(np.mean(strat_returns) / np.std(strat_returns) * np.sqrt(365)) if np.std(strat_returns) > 0 else 0

    return {
        "trade_count": trade_count,
        "trades_per_year": round(trade_count / years, 1) if years > 0 else 0,
        "strategy_final": round(strat_final, 2),
        "buy_and_hold_final": round(bh_final, 2),
        "strategy_vs_hodl_ratio": round(strat_final / bh_final, 3) if bh_final > 0 else float("nan"),
        "strategy_cagr_pct": round(((strat_final / initial_capital) ** (1 / years) - 1) * 100, 1) if years > 0 else 0,
        "hodl_cagr_pct": round(((bh_final / initial_capital) ** (1 / years) - 1) * 100, 1) if years > 0 else 0,
        "strategy_max_dd_pct": round(strat_dd * 100, 1),
        "hodl_max_dd_pct": round(bh_dd * 100, 1),
        "strategy_sharpe": round(sharpe, 2),
    }
