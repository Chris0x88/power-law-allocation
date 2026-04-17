# Constants — the locked calibration

These five numbers define the model. They are hardcoded in
[src/power_law/model.py](../src/power_law/model.py) and must not be
changed without re-running the full 2014–2026 backtest.

---

| Symbol | Name | Value | Source |
|--------|------|-------|--------|
| `FLOOR_A` | Power-law log-intercept | **-17.0** | Calibrated to full BTC history on log-log axes |
| `FLOOR_B` | Power-law exponent | **5.73** | Steeper than Metcalfe (~2.0); empirical fit |
| `SPIKE_A` | Initial spike amplitude | **40.0** | Calibrated to Cycle 2 (2013) blow-off |
| `KLEIBER` | Cycle-maturity scaling exponent | **0.75** | Kleiber's Law (biological 3/4 scaling) |
| `HALVING_BASE` | Per-halving geometric decay | **0.5** | Each cycle, spike potential halves |

---

## Pulse parameters

| Symbol | Value | Meaning |
|--------|-------|---------|
| Peak location | **0.33** | Cycle progress at which the pulse peaks (historical peaks in 2013, 2017, 2021 all ~1/3 into each cycle) |
| `w_up` | **0.18** | Build-up Gaussian width — slow multi-year escalator |
| `w_down` | **0.08 + 0.01·cycle** | Contraction width — sharp elevator, slightly widens as cycles mature |

## Allocation parameters

| Symbol | Value | Meaning |
|--------|-------|---------|
| Sigmoid steepness | **2.0** | Controls how aggressive the value signal is at extremes |
| Phase penalty window | **0.35–0.85** | Cycle progress range where the "post-peak cooldown" haircut applies |
| Max phase penalty | **0.50** | Up to 50% allocation reduction during deep bear |
| Floor boost | **0.30** | Up to +30% allocation when in deep-value zone |
| Deep-value threshold | **0.15** | Position-in-band below which full boost applies |
| Value threshold | **0.30** | Position-in-band below which half boost applies |
| Momentum weight | **0.3** | Multiplier on 90d heartbeat delta |
| Momentum cap | **±0.10** | Max momentum contribution to allocation |

## Rebalancer defaults

| Symbol | Value | Meaning |
|--------|-------|---------|
| `threshold_pct` | **0.22** | Allocation deviation needed to trigger a rebalance |
| `extreme_threshold_pct` | **0.05** | Force rebalance on sudden large moves |
| `min_trade_usd` | **1.0** | Dust filter |

---

## Why they're locked

The point of the model is to make an honest claim about Bitcoin's structure
that can be falsified by time. If we re-tune the constants every time the
market surprises us, we are:

1. **Overfitting.** Bitcoin has fewer than a dozen meaningful turning
   points in its entire history. Tuning five constants against a dozen
   events is not data science; it's curve-fitting to noise.
2. **Defeating the thesis.** The thesis is "Bitcoin has a stable power-law
   structure." If we are constantly changing what we think that structure
   is, we don't have a thesis anymore — we have a moving target.
3. **Creating version drift.** Every user of the model would need to
   re-audit the backtest every time constants change. That destroys
   the "drop-in, portable, deterministic" property.

---

## When would a re-calibration be justified?

Only if one of the following happens:

1. **A full cycle (4+ years) completes with prices sustained materially
   outside the floor/ceiling band** — not a brief overshoot, but persistent
   violation.
2. **The cycle structure itself breaks** — halvings stop producing the
   expected pattern, e.g. two consecutive cycles without a speculative peak.
3. **A clearly better theoretical foundation emerges** — e.g. a model that
   derives the exponent from first principles rather than fitting it.

None of these have happened as of this writing. Until they do, the
constants are frozen.

If re-calibration becomes necessary, the right answer is **a new model with
a new version number**, not a silent parameter change to this one.
