# Rebalancer

The model emits a target BTC allocation (0–100%). The rebalancer turns that
signal into trades.

This document describes the policy, the research behind the threshold
choice, and the reference implementation shipped in this repo.

---

## 1. The core loop

On every tick (hourly, daily, weekly — your choice):

1. Fetch the current BTC price and portfolio state.
2. Compute the **target allocation** from the model: `target = allocation_signal(now, price)`.
3. Compute the **current allocation**: `current = btc_value / total_value`.
4. Compute the **deviation**: `|current - target|`.
5. If `deviation >= threshold`, execute a trade that moves the portfolio to `target`.
6. Otherwise, do nothing.

That's it. The magic is in the threshold.

---

## 2. The threshold question

Every trade costs money: fees, slippage, and (in taxable accounts) realised
gains. Every trade you *don't* make costs opportunity: drift away from the
model's view.

There is a sweet spot. It is **not** at zero.

### Backtest: 2014–2026, 0.3% fees

| Threshold | Trades | Trades/year | Final ($1k start) | vs HODL |
|-----------|--------|-------------|-------------------|---------|
| 1%        | 1,123  | ~94         | $385,612          | 1.84×   |
| 5%        | 200+   | ~17         | —                 | 0.90×   |
| 10%       | 145    | ~12         | —                 | 1.20×   |
| 15%       | 70     | ~6          | $273,037          | 1.31×   |
| **22%**   | **48** | **~4**      | **$532,683**      | **2.55×** |
| 30%       | 28     | ~2.3        | —                 | 2.20×   |

**Finding:** tight thresholds (1–10%) chase noise. Wide thresholds (30%+)
miss meaningful shifts. **22% is the empirical sweet spot.**

### Why 22% works

- **Signal over noise.** Bitcoin's intraday and weekly moves are enormous.
  A 22% deviation in *allocation* (not price) only occurs after a
  meaningful multi-month structural shift in position-in-band.
- **Fee amortisation.** At ~4 trades/year and 0.3% fees, total fee drag
  is ~1.2%/year — trivial next to volatility.
- **Tax efficiency.** In most jurisdictions, fewer trades = fewer taxable
  events = larger compounding base.
- **Psychological coherence.** Four trades a year is something a human can
  actually execute without second-guessing.

See [BACKTEST.md](BACKTEST.md) for the fee-sensitivity matrix and walk-forward
validation.

---

## 3. Policy knobs

The reference rebalancer ([src/power_law/rebalancer.py](../src/power_law/rebalancer.py))
exposes these settings via `RebalancerConfig`:

| Knob | Default | Role |
|------|---------|------|
| `threshold_pct` | **0.22** | Min allocation deviation to trigger a trade |
| `extreme_threshold_pct` | 0.05 | Force rebalance on large sudden moves |
| `min_trade_usd` | 1.0 | Dust filter — skip trades smaller than this |
| `fee_rate` | 0.003 | Informational; the venue actually charges the fee |

You can run tighter (15%) if you have very low fees and no tax drag.
You can run wider (30%) if you're in a high-tax regime and want minimum churn.

**Do not run below 10%.** The backtest shows this is a losing proposition
across every fee regime.

---

## 4. Tick cadence

The tick cadence (hourly, daily, weekly) is **not the same thing as** the
rebalance frequency.

- **Tick cadence** = how often the rebalancer *checks*.
- **Rebalance frequency** = how often it *acts*, which is gated by the threshold.

At a 22% threshold, you can tick hourly and still only trade ~4 times a year.
Ticking more often just means you react faster when a threshold breach
actually happens.

Recommended cadence:
- **Hourly** for deployed bots (cheap, responsive, threshold does the filtering)
- **Daily** for manual review (enough for a human)
- **Weekly** if you have absolutely no infrastructure and just want to
  check the signal on Sundays

---

## 5. Venue-agnostic design

The rebalancer does not know or care what venue it's trading on. It calls a
`Venue` protocol:

```python
class Venue(Protocol):
    def get_price(self) -> float: ...
    def get_portfolio(self) -> Portfolio: ...
    def execute_trade(self, side: Side, notional_usd: float) -> TradeResult: ...
```

Any CEX, DEX, or custodian can satisfy this interface with a thin adapter.
A paper-trade venue is included for testing.

See [VENUES.md](VENUES.md) for the case for SaucerSwap specifically.

---

## 6. Failure modes to handle

Any production rebalancer needs to handle:

1. **Partial fills.** The target might not execute in one shot on a thin
   DEX. Re-check portfolio and re-target on the next tick.
2. **Slippage.** If the quoted price deviates from the effective fill price
   by more than a pre-set tolerance, abort. The reference implementation
   doesn't do this — your venue adapter should.
3. **Stale prices.** Reject trades against price data older than N seconds.
4. **Gas failures.** Retries with backoff. Don't re-enter the loop until
   the venue confirms state.
5. **Wedged allocations.** If a venue cannot hit the target for structural
   reasons (e.g. liquidity), log and hold rather than spiralling.

All of these belong in the venue adapter, not the rebalancer.

---

## 7. Capital protection, not alpha maximisation

The rebalancer's primary job is **capital protection**, not beating HODL in
a straight line.

In 2017–2025:

| Metric | HODL | Model (22%) |
|--------|------|-------------|
| Return | 21.3× | 32.2× |
| Max drawdown | **-83.4%** | **-49.9%** |
| Sharpe | 0.76 | 1.12 |
| Trades/year | 0 | ~6 |

The drawdown number is the one that matters. HODL demands that you sit
through 83% drawdowns without flinching. Most people can't. The model's
22% threshold + phase penalty mechanically gets you out of the way during
post-peak cooldowns, and back in when the floor approaches.

**The alpha vs HODL is a happy by-product. The drawdown reduction is the
actual point.**
