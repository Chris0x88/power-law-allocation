# The Model

The full math of the Power-Law Allocation Model — floor, ceiling, heartbeat,
and the final allocation signal.

All of this is implemented in [src/power_law/model.py](../src/power_law/model.py)
in under 400 lines of stateless Python.

---

## 1. Inputs

The model takes exactly two inputs:

- **`date`** — today's date (or any date you want to evaluate)
- **`price`** — Bitcoin's USD price at that date

That's it. No database, no historical feed, no warm-up period.

---

## 2. Layer 1: The Power-Law Floor

**Equation:**

$$P_{\text{floor}}(d) = 10^{A} \cdot d^{B}$$

where:
- $d$ = days since Bitcoin genesis (Jan 3, 2009)
- $A = -17.0$ — log-intercept, calibrated to full history
- $B = 5.73$ — power-law exponent

**Interpretation:** The floor grows approximately 40% per year, decelerating
slowly over time. It represents the minimum-energy equilibrium of the
Bitcoin network — where price converges when both speculative excess and
fear drain away.

**Empirically:** Price has touched the floor multiple times (2012, 2015,
2018–19, briefly 2022). It has never sustained materially below it.

**Implementation:**

```python
def floor_price(date: datetime) -> float:
    d = max(1, (date - GENESIS).days)
    return 10 ** (FLOOR_A + FLOOR_B * math.log10(d))
```

---

## 3. Layer 2: The Cycle Ceiling

Historical Bitcoin cycles exhibit a clear decay: each peak is a smaller
multiple above the floor than the last.

**Spike envelope** (max multiple above floor for a given cycle):

$$S_{\max}(c) = 1 + S_A \cdot c^{-K} \cdot H_B^{(c-2)}$$

where:
- $c$ = halving cycle index (Cycle 2 = 2012 halving, Cycle 5 = current)
- $S_A = 40.0$ — initial spike amplitude (calibrated to Cycle 2 blow-off)
- $K = 0.75$ — Kleiber's Law exponent (biological 3/4 scaling)
- $H_B = 0.5$ — geometric decay per halving

**Ceiling price:**

$$P_{\text{ceiling}}(t) = P_{\text{floor}}(t) \cdot S_{\max}(c_{\text{peak}})$$

### V3.2 refinement: continuous ceiling

To eliminate discontinuous "jumps" at halving boundaries, we index the
spike amplitude to a **peak-centred effective cycle index**:

$$c_{\text{peak}} = c + (p - 0.33)$$

where $p$ is raw cycle progress (0.0 to 1.0). This makes the ceiling
continuously interpolate between adjacent cycles, landing exactly on the
integer cycle value at the expected peak (33% cycle progress) and smoothly
crossing halving boundaries.

**Implementation:**

```python
def ceiling_price(date: datetime) -> float:
    c = cycle_index(date)
    p = cycle_progress_raw(date)
    c_peak = c + (p - 0.33)
    return floor_price(date) * spike_max(c_peak)
```

---

## 4. Layer 3: The Heartbeat Pulse

The pulse tells us **where, within a cycle, price should be.**

It peaks at 33% cycle progress, matching historical peaks in 2013, 2017, and
2021. It is asymmetric — slow build-up, sharp crash — because bull markets
are gradual and bear markets are sudden.

**Asymmetric Gaussian:**

$$H(p, c) = \begin{cases}
\exp\left(-\frac{(p - 0.33)^2}{2 w_{\text{up}}^2}\right) & p < 0.33 \\
\exp\left(-\frac{(p - 0.33)^2}{2 w_{\text{down}}^2}\right) & p \ge 0.33
\end{cases}$$

where:
- $w_{\text{up}} = 0.18$ — build-up width (escalator)
- $w_{\text{down}} = 0.08 + 0.01 \cdot c$ — contraction width, matures with each cycle

The pulse is then **boundary-pinned** so it equals exactly 0 at $p = 0$ and
$p = 1$ (halving boundaries). This eliminates any "bumps" between cycles.

**Model fair value:**

$$P_{\text{model}}(t) = P_{\text{floor}}(t) + (P_{\text{ceiling}}(t) - P_{\text{floor}}(t)) \cdot H(p, c)$$

---

## 5. The Allocation Signal

Given `date` and `price`, the allocation is composed of four terms:

### 5.1 Value component (sigmoid on position)

Position in band:

$$\text{pos} = \frac{P - P_{\text{floor}}}{P_{\text{ceiling}}-P_{\text{floor}}}, \quad 0 = \text{at floor}, \; 1 = \text{at ceiling}$$

Sigmoid on a z-score equivalent:

$$z = (\text{pos} - 0.5) \cdot 4$$

$$\text{value\_alloc} = \frac{1}{1 + e^{2z}}$$

This gives:
- pos = 0% → ~98% BTC
- pos = 50% → 50% BTC
- pos = 100% → ~2% BTC

### 5.2 Cycle phase penalty (the secret sauce)

When cycle progress is between 35% and 85%, apply a large haircut — even
if price looks cheap, we are in the post-peak bear phase:

```
if 0.35 ≤ p ≤ 0.55:  penalty = (p - 0.35)/0.20 * 0.50   (ramps 0% → 50%)
if 0.55 ≤ p ≤ 0.70:  penalty = 0.50                    (max penalty)
if 0.70 ≤ p ≤ 0.85:  penalty = (0.85 - p)/0.15 * 0.50  (ramps 50% → 0%)
```

**Why this matters:** Bitcoin's bear markets are prolonged. Buying "cheap"
at 50% down often leads to another 50% drop. The phase penalty prevents
catching falling knives. In backtesting, this is the single largest
contributor to avoiding drawdowns.

### 5.3 Momentum tilt

A small (±10%) adjustment based on the 90-day-forward heartbeat:

$$\text{momentum} = \text{clip}\left((H_{t+90d} - H_t) \cdot 0.3, -0.10, +0.10\right)$$

If the heartbeat is still climbing → lean in. If it's topping → lean back.

### 5.4 Floor boost

When position is very low (deep-value zone), add up to +30%:

- pos < 15% → full boost (up to +30%)
- pos < 30% → half boost (up to +15%)

**Critically**, this boost is scaled inversely with the phase penalty:
$\text{boost\_scale} = \max(0, 1 - 2 \cdot \text{penalty})$. During the
deepest bear (penalty = 0.50), the boost is disabled — we don't catch
falling knives just because they look cheap.

### 5.5 Final allocation

$$\text{alloc} = \text{clip}\big(\text{value\_alloc} - \text{penalty} + \text{momentum} + \text{boost},\; 0,\; 1\big)$$

---

## 6. Derived labels

Plain-English tags for humans and LLMs:

**Cycle phase** (by progress):
- 0–15% → `early_cycle_reset`
- 15–35% → `pre_peak_build_up`
- 35–55% → `late_cycle_peak_zone`
- 55–80% → `post_peak_cooldown`
- 80–100% → `late_cycle_washout`

**Valuation** (by position in band):
- 0–20% → `deep_value`
- 20–40% → `undervalued`
- 40–60% → `mid_band`
- 60–80% → `overvalued`
- 80–100% → `euphoria`

**Stance** (by allocation):
- \>80% → `max_accumulate`
- 60–80% → `accumulate`
- 40–60% → `balanced`
- 20–40% → `trim_exposure`
- 0–20% → `capital_protection`

---

## 7. The five locked constants

| Symbol | Value | What it is |
|--------|-------|------------|
| $A$ | $-17.0$ | Power-law log-intercept |
| $B$ | $5.73$ | Power-law exponent |
| $S_A$ | $40.0$ | Initial spike amplitude |
| $K$ | $0.75$ | Kleiber's Law exponent |
| $H_B$ | $0.5$ | Per-halving geometric decay |

Plus the pulse widths ($w_{\text{up}} = 0.18$, $w_{\text{down}} = 0.08 + 0.01c$),
the peak location (33%), and the sigmoid steepness (2.0).

**These are locked.** They were calibrated once to Bitcoin's full history and
must not be changed without re-running the full backtest. See
[CONSTANTS.md](CONSTANTS.md).

---

## 8. Verification

Against 2014–2026 BTC price history, the model's floor/ceiling band
contains **~95% of days**, with:

- ~3% of days below floor (capitulation zones)
- ~2% of days above ceiling (blow-off tops)

Position distribution across history:

| Position band | % of days | Label |
|---------------|-----------|-------|
| 0–20% | ~58% | VERY CHEAP |
| 20–40% | ~18% | CHEAP |
| 40–60% | ~11% | FAIR |
| 60–80% | ~8% | EXPENSIVE |
| 80–100% | ~5% | VERY EXPENSIVE |

**Bitcoin spends 76% of its time near the floor.** The model's job is to
tell you when today is one of the rare 13% of days where you should be
trimming or de-risking.
