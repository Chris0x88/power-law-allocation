# Thesis: Why This Model

## The Bitcoin investing problem

Bitcoin's defining feature is also its greatest challenge: cycles of 10–20×
gains followed by 70–85% drawdowns, repeated consistently across 15 years of
history.

Investors respond in one of two ways:

- **Panic sell** at the bottom and crystallise losses.
- **HODL** through every drawdown and accept full exposure to the next one.

Both work, after a fashion. Both are psychologically brutal. And both leave
money on the table.

There is a third path: **mechanical rebalancing guided by a model that knows
where we are in the cycle.**

The Heartbeat Model does not predict the future. It answers a simpler,
tractable question:

> **Is Bitcoin cheap or expensive right now, relative to its historical structure?**

If cheap → hold more Bitcoin.
If expensive → hold less.
Rebalance only when the gap between where you are and where you should be
becomes material.

This is the logic of value investing, applied to a well-defined structural
framework. It is not new in principle. What is new is Bitcoin itself being
stable enough, for long enough, to make the framework work.

---

## Why a power law

When Bitcoin's price is plotted on log-price vs log-time axes, the data
traces a near-linear path. This is the signature of a power law:

$$P_{\text{floor}}(d) = 10^{A} \cdot d^{B}$$

with $d$ = days since Bitcoin genesis (January 3, 2009), $A = -17.0$, and
$B = 5.73$.

In plain terms: **the floor grows ~40% per year**, decelerating slowly.

Conceptually, the floor represents the **minimum-energy equilibrium** of the
Bitcoin network — where price converges when both speculative excess and fear
drain away. Price has touched this line multiple times (2012, 2015, 2018–19,
briefly in 2022) but has never sustained below it for long.

The exponent 5.73 is steeper than simple Metcalfe's law network effects
(~2.0), reflecting something deeper — possibly the compounding of adoption,
security, and energy anchoring. It is best understood as an empirical
constant that fits the data across 15+ years.

### Why a power law and not an exponential?

An exponential model (constant % growth per year) implies Bitcoin compounds
forever at some fixed rate. That is extraordinary and historically rare.

A power law implies that **growth decelerates** — it is fast now, and will be
slower later. That is consistent with adoption curves, network maturity, and
every other large-scale technology adoption pattern we have data for.

Over the model horizon, this matters: a power law predicts a $1M Bitcoin
somewhere around 2035. An exponential predicts $1M by 2028 and $100M by 2035.
One of these is plausible. The other is not.

---

## Why a cycle ceiling

The floor answers *where does Bitcoin want to be?* The ceiling answers
*how high can the speculative bubble reach in this era?*

Historical Bitcoin cycles exhibit a clear pattern: **each successive peak is
dramatically less extreme, relative to the floor, than the prior one.**

| Cycle | Peak year | Peak / Floor ratio |
|-------|-----------|--------------------|
| 2     | 2013      | ~30×               |
| 3     | 2017      | ~15×               |
| 4     | 2021      | ~6×                |
| 5     | 2025(?)   | ~3× (predicted)    |

This is modelled using **Kleiber's Law** — a biological scaling principle
where metabolic efficiency scales with organism size at a 3/4 power. Applied
to Bitcoin: as the market matures and grows, the speculative "metabolism"
per unit of market cap decreases.

As a portfolio allocator, you don't need to believe this literally. You need
to believe the empirical fact: **spikes are getting smaller.** That is
visible in the price history without any appeal to scaling laws.

---

## Why a heartbeat

The floor gives us the bottom. The ceiling gives us the top.
The heartbeat tells us **where, within a cycle, we should expect price to be.**

Historical peaks in 2013, 2017, and 2021 all occurred roughly **1/3 of the
way into each halving cycle.** That is the peak of the heartbeat pulse.

The pulse is asymmetric — slow build-up, fast crash — because bull markets
are gradual ("up the escalator") and bear markets are sudden
("down the elevator"). Anyone who lived through 2018 or 2022 knows this.

Combining floor + ceiling + heartbeat gives us a fair-value track through
each cycle. Price oscillates above and below this track. The model's job is
to lean against those oscillations — sell into ceiling-hugging euphoria, buy
into floor-hugging despair.

---

## Why not more complex?

We deliberately resisted adding:

- **Machine learning.** Overfits. Opaque. Adds no proven alpha on a
  time series with fewer than a dozen major turning points.
- **On-chain signals.** Noisy. Change meaning across cycles. Correlated with
  price but not clearly causal.
- **Macro overlays** (rates, DXY, liquidity). Interesting, but add variance
  without obvious robustness.
- **Sentiment indexes.** Trail price. Useful for narrative, not allocation.

The model has **five calibrated constants and one ceiling formula.** That is
enough. It is locked. See [CONSTANTS.md](CONSTANTS.md).

---

## Expected lifespan — and the eventual end of this model

**The power-law framework will eventually break, on purpose, and that is
not a bug.**

The entire model rests on one assumption: Bitcoin is still in its youth.
It is small relative to global wealth, it is volatile, and its price is
dominated by reflexive cycles of adoption and speculation. Those three
conditions are what produce a power-law floor with repeated Kleiber-decaying
spikes above it. Take any of them away, and the model stops describing the
asset.

We expect all three to go away — slowly, over many years, in the same
order.

### Where this is going

Every major financial asset class that has reached maturity — gold,
broad equities, sovereign debt — trades in an **exponential** growth
regime, not a power-law regime. Volatility compresses. Cycles smooth.
Price becomes a function of the money supply and a modest real return,
rather than of speculative flows.

We expect Bitcoin to make exactly this transition, once it has absorbed a
critical mass of global wealth into its orbit. The mechanism is
straightforward:

1. As a larger fraction of wealth lives in BTC, marginal flows produce
   smaller percentage moves. Volatility decays mechanically.
2. Holders with longer time horizons replace speculators on the margin.
   Leverage and perpetual funding become a smaller share of turnover.
3. The asset starts to function as a settlement layer and collateral
   base, not a bet. Its job changes.
4. At that point the four-year halving rhythm stops mattering. There is
   no "cycle" to heartbeat against — just a slow, steady, exponential
   repricing against fiat debasement.

The endgame, as we read it, is one of two scenarios:

- **Recapitalisation.** Bitcoin anchors the dollar. The USD remains the
  medium of exchange; BTC becomes the reserve underneath it, the way
  gold once did. This is the less disruptive path.
- **Transition.** Sovereign and corporate balance sheets migrate off
  USD-denominated debt onto BTC-denominated rails. The USD survives as
  a transactional layer; the store-of-value function decouples entirely.

Either scenario produces the same allocation implication: **at some
point in the next decade, a constant 80–100% BTC allocation becomes the
right answer, and rebalancing stops adding value.** The model will quietly
tell you this — the floor and the price will converge, position-in-band
will sit at zero, and allocation will pin at 100%.

### Our horizon for this model

- **Five years at minimum** (through ~2030–2031). Cycle 5 (the current
  cycle, post-2024 halving) should behave roughly like prior cycles,
  with a visibly compressed ceiling consistent with Kleiber decay. The
  model is calibrated for this.
- **Five to ten years** (~2030–2035). We expect cycle amplitude to
  continue compressing. The phase penalty becomes less important; the
  floor boost does more of the work. The strategy should still win, by
  a smaller margin.
- **Beyond ten years.** Probabilistically, the cycle structure breaks.
  Volatility drops below what the model was calibrated on. At that point,
  this framework retires.

**The right response when this model stops working is not to re-tune it.**
The constants are locked precisely so we notice when it breaks rather than
patching it into uselessness. When it breaks, a successor framework with a
different thesis (probably: constant allocation, tuned to fiat debasement
and real yields) will take over.

---

## Other known failure modes

The model is an empirical framework, not a theorem. It can also fail in
ways unrelated to the long-run exponential transition above.

1. **Regime change.** A regulatory shock, protocol failure, or mass exit
   would break the power-law floor in the short term. The model has no
   opinion on these events.
2. **Crowded trade.** If enough capital adopts this or similar models,
   the reflexive accumulation at the floor and de-risking at the ceiling
   will *become* the cycle, and the historical amplitude will compress
   faster than predicted. That is survivable — the model still
   outperforms — but the 2.55× backtest edge will shrink.
3. **Persistent overshoot.** Nothing prevents price from spending multiple
   years above the ceiling. The model would sit in capital-protection mode
   during that period and under-allocate.

If any of these happen, the right response is **not** to re-tune the
constants. It is to publish a successor model with a different thesis.

---

## The investment discipline

The model is only useful if you run it honestly. In practice that means:

- **Rebalance when the signal says to**, not when it feels comfortable.
  The model will tell you to sell on the way up, when it feels wrong. It
  will tell you to buy on the way down, when it feels terrifying.
- **Rebalance rarely.** The research-optimal threshold is 22%. Tighter
  thresholds chase noise and destroy returns through fees and tax.
- **Don't move the goalposts.** The model's worst quarters will coincide
  with your strongest urge to override it. That is when the edge is
  actually being earned.

> The model's job is not to make you feel smart. Its job is to take the
> decision out of your hands at the moments where you are most likely to
> make it badly.

---

## Further reading

- [MODEL.md](MODEL.md) — the equations in full
- [REBALANCER.md](REBALANCER.md) — rebalancing policy and threshold research
- [BACKTEST.md](BACKTEST.md) — performance across fee regimes and windows
- [VENUES.md](VENUES.md) — where to execute the strategy in practice
- [papers/thermal_stability.md](../papers/thermal_stability.md) — the formal working paper
- [papers/heartbeat_v3.2_paper.md](../papers/heartbeat_v3.2_paper.md) — earlier internal paper
