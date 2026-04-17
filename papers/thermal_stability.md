---
title: "Bitcoin's Journey Toward Thermal Stability: A Phenomenological Framework for Cycle-Aware Portfolio Allocation"
author: "Chris Imgraben"
affiliation: "Independent researcher"
date: "April 2026"
version: "2.0"
keywords: "Bitcoin, power law, portfolio allocation, rebalancing, Kleiber's Law, cycle analysis, cryptocurrency valuation"
---

# Bitcoin's Journey Toward Thermal Stability

### A Phenomenological Framework for Cycle-Aware Portfolio Allocation

**Chris Imgraben** — Independent researcher
**Version 2.0 · April 2026**

---

## Abstract

We present a deterministic, stateless framework for Bitcoin portfolio
allocation that requires only a calendar date and the current spot price
as inputs. The framework decomposes observed price into three layers: a
**power-law equilibrium floor** calibrated to the full post-genesis price
history, a **speculative envelope** whose amplitude decays geometrically
with successive halving epochs following a Kleiber-like
three-quarter-power scaling, and an **intra-cycle heartbeat pulse**
modelled as a boundary-pinned asymmetric Gaussian peaking at
one-third of each halving cycle. From these references we derive a
position-in-band score, a cycle-phase penalty, and a bounded allocation
signal in $[0, 1]$. On daily BTC/USD data from August 2011 through April
2026 the framework captures approximately 95% of observations within its
band and, at a 22% allocation-deviation rebalancing threshold, produces
a strategy-to-HODL wealth ratio of 2.55$\times$ over the 2014--2026 window
while reducing maximum drawdown from $-83\%$ to approximately $-50\%$. We
stress that the framework is phenomenological, not first-principles: the
physical and biological analogies are heuristic motivations for functional
form, not derivations. We forecast that the power-law regime itself is
time-limited and will transition to a logistic (S-curve) regime as
Bitcoin's market capitalisation approaches planetary-scale boundaries
such as the global monetary base or gold market capitalisation, with the
expected transition window of 2029--2035.

**Keywords:** Bitcoin, power law, portfolio allocation, rebalancing,
Kleiber's Law, scaling, cycle analysis.

---

## 1. Introduction

Bitcoin's price history presents two empirical facts that any valuation
framework must confront simultaneously.

First, plotted on log--log axes (price against days since genesis),
the price series is remarkably close to linear. This has been observed
repeatedly in the grey literature [@burger2019; @santostasi2024] and is
consistent with a power-law growth process
$P(t) \propto t^{B}$. The exponent, empirically, is substantially
larger than the classical Metcalfe's Law exponent of 2 — consistent with
Bitcoin being more than a simple communication network.

Second, price oscillates around this trend with very large amplitude,
with historical drawdowns repeatedly exceeding 80% from prior peaks.
Those oscillations have so far displayed a regular four-year rhythm
aligned with the block-reward halving schedule, and each successive cycle
peak has been progressively less extreme, relative to the trend, than
the one before.

A framework that is useful for allocation decisions must therefore do
three things. It must **identify the trend** (so that "cheap" and
"expensive" are well-defined). It must **bound the speculative range**
(so that over- and under-extension can be measured). And it must
**localise the investor within the cycle** (so that recommendations
account for where the cycle is, not only where price is).

This paper formalises that decomposition into a single deterministic
function, calibrates it on 15 years of daily data, and derives an
allocation rule that turns the resulting signal into trades. We also
address the question every framework of this type should be asked but
typically is not: when and why will it stop working?

### Contributions

1. A single stateless function $\alpha(t, P)$ mapping a date and a price
   to a recommended Bitcoin portfolio allocation in $[0, 1]$, requiring
   no historical data, database, or warm-up period.
2. A V3.2 refinement of the halving-cycle ceiling that removes prior
   piecewise discontinuities by indexing the spike amplitude to a
   peak-centred effective cycle index.
3. An empirically-grounded rebalancing threshold (22% allocation
   deviation) derived from a 12-year threshold sweep.
4. A formal discussion of the finite-size limit: the conditions under
   which the power-law regime is expected to yield to logistic
   saturation, and the consequent retirement of this framework.

---

## 2. Related Work

**Network-value scaling.** Metcalfe's Law [@metcalfe1995]
postulates $V \propto n^{2}$ for telecommunication networks. Empirical
work on Bitcoin [@burger2019; @santostasi2024] has found substantially
steeper scaling, typically $P \propto t^{B}$ with $B$ in the range
$5$--$6$ when $t$ is taken as days since genesis. This is consistent
with a value function cubic in users ($V \propto n^{3}$) under the
approximation $n \propto t^{2}$, though we treat this dimensional
argument as an analogy rather than a theorem.

**Kleiber's Law.** In biology, Kleiber's Law [@kleiber1932] states that
basal metabolic rate scales as body mass to the three-quarter power.
Similar three-quarter-power scaling recurs in network biology
[@west1999] and, we argue, provides a useful functional form for the
decay of speculative amplitude as the Bitcoin market matures — without
implying any literal metabolic content.

**Bitcoin cycle analysis.** The association between the four-year
halving cycle and peak timing has been widely observed in practitioner
literature; a concise summary is given in Burniske and Tatar
[@burniske2018]. Our treatment formalises peak location at approximately
33% cycle progress and models boundary-pinned asymmetric pulses within
cycles.

**Allocation frameworks.** Kelly-style sizing
[@kelly1956; @maclean2010] motivates our use of a sigmoid allocation
function and provides the conceptual backdrop for the deviation-gated
rebalancing rule. Classical rebalancing-threshold analysis is found in
Sun et al. [@sun2006]; the core insight that rebalancing frequency has
a concave relationship with realised returns, due to compounding of
transaction costs, is well established.

---

## 3. Phenomenological Framework

We adopt the following notation throughout. Let $t$ denote calendar time;
$d(t)$ denote days since Bitcoin genesis on 3 January 2009; and $P(t)$
denote the observed USD spot price.

### 3.1 The Equilibrium Floor

We define the floor price $P_{\text{floor}}(t)$ as the power law

$$
\log_{10} P_{\text{floor}}(t) = A + B \log_{10} d(t),
\qquad P_{\text{floor}}(t) = 10^{A} \cdot d(t)^{B}. \tag{1}
$$

Calibration on the full daily price record (Section 4.2) yields
$A = -17.0$ and $B = 5.73$. The floor grows monotonically with time at a
slowly decelerating rate, corresponding to an approximate +40% annual
growth rate at present and smaller relative growth at longer horizons.

**Interpretation.** We interpret $P_{\text{floor}}$ as a capital-flow
equilibrium: the price level that, in the absence of speculative excess
and fear, the network gravitates toward. Empirically the observed price
has touched or crossed below this level during each major bear market
(2012, 2015, 2018--19, briefly 2022) but has not sustained materially
below it. The exponent $B = 5.73$, being substantially steeper than
Metcalfe's exponent of $2$, is consistent with the network providing
more than connection value: a plausible heuristic is that coins held
over time occupy "volume" in the network, producing
$V \propto n^{3} \propto t^{6}$. We stress that this is a
dimensional analogy, not a derivation.

### 3.2 The Speculative Envelope

Above the floor we define a cycle-dependent ceiling

$$
P_{\text{ceiling}}(t) = P_{\text{floor}}(t) \cdot S_{\max}\left(c_{\text{peak}}(t)\right), \tag{2}
$$

where the amplitude function

$$
S_{\max}(c) = 1 + \alpha \cdot c^{-k} \cdot \delta^{c-2} \tag{3}
$$

combines two decay mechanisms: a three-quarter-power scaling term
$c^{-k}$ with $k = 0.75$, and a geometric per-halving decay $\delta^{c-2}$
with $\delta = 0.5$. The initial-amplitude coefficient
$\alpha = 40$ is calibrated to the Cycle-2 peak (2013). $c$ denotes a
(real-valued) halving-cycle index.

**Continuity at halving boundaries.** A naïve piecewise definition of
$c$ produces unphysical discontinuities at each halving. We eliminate
this by indexing the amplitude to a **peak-centred effective cycle
index**

$$
c_{\text{peak}}(t) = c_{\text{int}}(t) + \bigl(p(t) - 0.33\bigr), \tag{4}
$$

where $c_{\text{int}}(t)$ is the integer halving-cycle index at time $t$
and $p(t) \in [0, 1]$ is raw cycle progress. Under this definition,
$c_{\text{peak}}$ takes the integer value of the current cycle exactly
when $p = 0.33$, matching the empirical peak. The envelope is then
smooth across halving boundaries.

**Justification.** The three-quarter-power scaling is motivated by
analogy with Kleiber's Law. The geometric halving decay reflects the
progressively smaller relative shock of each halving on circulating
supply growth. We label both motivations as heuristic; the empirical
case for $(k, \delta) = (0.75, 0.5)$ is their fit to historical peak
amplitudes, not a first-principles derivation.

### 3.3 The Heartbeat Pulse

Within each cycle we model intra-cycle structure using an asymmetric
boundary-pinned Gaussian pulse

$$
H_{\text{raw}}(p, c) = \begin{cases}
\exp\!\left(-\dfrac{(p - \mu)^{2}}{2 \sigma_{\text{up}}^{2}}\right) & p < \mu, \\
\exp\!\left(-\dfrac{(p - \mu)^{2}}{2 \sigma_{\text{down}}(c)^{2}}\right) & p \ge \mu,
\end{cases} \tag{5}
$$

with $\mu = 0.33$, $\sigma_{\text{up}} = 0.18$ and
$\sigma_{\text{down}}(c) = 0.08 + 0.01 c$. The asymmetry encodes the
empirical observation that Bitcoin bull markets build gradually but
correct rapidly — the "up the escalator, down the elevator" pattern
[@miller2010].

To enforce exact continuity across halving boundaries we define the
**boundary-pinned pulse**

$$
H(p, c) = \max\!\bigl(0, H_{\text{raw}}(p, c) - \eta(p, c)\bigr), \tag{6}
$$

where
$\eta(p, c) = H_{\text{raw}}(0, c)(1-p) + H_{\text{raw}}(1, c) \cdot p$
is a linear correction that makes $H(0, c) = H(1, c) = 0$. This
eliminates pulse residuals that would otherwise introduce small
artefacts at every halving.

### 3.4 Composite Fair-Value Function

The model fair-value price within a cycle is the heartbeat-modulated
interpolation between floor and ceiling:

$$
P_{\text{fair}}(t) = P_{\text{floor}}(t) + \bigl(P_{\text{ceiling}}(t) - P_{\text{floor}}(t)\bigr) \cdot H\!\bigl(p(t), c_{\text{int}}(t)\bigr). \tag{7}
$$

$P_{\text{fair}}$ is continuous across halving boundaries and
monotonically increasing in $t$ except for small intra-cycle
oscillations driven by $H$.

---

## 4. Calibration and Empirical Fit

### 4.1 Data

Daily BTC/USD closing prices are taken from Bitstamp (18 August 2011 to
16 August 2017) and from Binance BTCUSDT (17 August 2017 to the present).
The two series are temporally contiguous and exhibit negligible
cross-venue bias at the close. Pre-2011 prices are omitted from
calibration due to the extreme thinness of exchange-traded markets and
the known price-discovery anomalies of that era.

### 4.2 Floor Calibration

The intercept $A$ and exponent $B$ in (1) are fit by ordinary least
squares on $\log_{10} P$ against $\log_{10} d$ over the full daily
record from 18 August 2011 to the present. The resulting fit
$(A, B) = (-17.0, 5.73)$ has $R^{2} \approx 0.95$ in log--log space
and is stable under substantial perturbations of the window: removing
the first two years, or the last two years, or the 2017 bull market,
changes $B$ by less than 0.05.

### 4.3 Envelope Calibration

The envelope parameters $(\alpha, k, \delta)$ in (3) are calibrated to
the observed cycle peaks of 2011, 2013, 2017, and 2021. We fix
$k = 0.75$ on theoretical grounds (three-quarter-power biological
scaling) and $\delta = 0.5$ on structural grounds (geometric halving
decay). The only free parameter is $\alpha$, which we fit by matching
$S_{\max}$ to the Cycle-2 (2013) peak ratio of approximately
30$\times$ over the floor, yielding $\alpha = 40.0$. With these three
constants fixed, the envelope retrodicts the 2017 and 2021 peaks to
within 20% without further tuning.

### 4.4 Goodness of Fit and Coverage

Over the full daily record, the observed price lies between floor and
ceiling on approximately 95% of trading days:

| Position in band | % of days |
|:---|---:|
| Below floor | $\approx 3\%$ |
| In band | $\approx 95\%$ |
| Above ceiling | $\approx 2\%$ |

The empirical distribution of position-in-band is right-tailed, with
approximately 58% of days at position $<20\%$ (near the floor) and
approximately 5% at position $>80\%$ (near the ceiling). This asymmetry
is consistent with the strategy's central empirical claim: Bitcoin
spends most of its time near its equilibrium and only rarely near its
maximum-excitation state. It also underpins why **restraint** —
doing nothing most of the time — is the dominant behaviour demanded
by the model.

---

## 5. Derived Metrics and the Allocation Signal

### 5.1 Position Score

Given observed price $P(t)$, we define the **position score**

$$
Z(t) = \text{clip}\!\left(\frac{P(t) - P_{\text{floor}}(t)}{P_{\text{ceiling}}(t) - P_{\text{floor}}(t)}, \; 0, \; 1\right). \tag{8}
$$

$Z = 0$ corresponds to price at or below the floor; $Z = 1$ to price at
or above the ceiling.

### 5.2 Valuation Zones

We label five non-overlapping zones by position:

| Position $Z$ | Zone | State |
|:---|:---|:---|
| $[0.0, 0.2)$ | Deep value | Ground state |
| $[0.2, 0.4)$ | Undervalued | Low energy |
| $[0.4, 0.6)$ | Mid-band | Equilibrium |
| $[0.6, 0.8)$ | Overvalued | High stress |
| $[0.8, 1.0]$ | Euphoria | Criticality |

### 5.3 Allocation Function

The core allocation function is a steep sigmoid centred at $Z = 0.5$:

$$
\alpha_{\text{value}}(Z) = \frac{1}{1 + \exp\!\bigl(2 \cdot (Z - 0.5) \cdot 4\bigr)}. \tag{9}
$$

This produces approximately 98% allocation at the floor, 50% at
mid-band, and approximately 2% at the ceiling. The steepness coefficient
$2$ is calibrated for desired aggressiveness at the extremes and is
insensitive to small changes: a coefficient in $[1.5, 2.5]$ yields
qualitatively similar behaviour.

### 5.4 Cycle-Phase Penalty

A pure-value allocation ignores the timing problem that ruined many
fundamental-value strategies in prior cycles: a rapid drawdown produces
a seemingly attractive position score while the cycle is still
structurally bearish, inviting early re-entry and further drawdown —
the "catching falling knives" failure mode. We address this with a
cycle-phase penalty

$$
\pi(p) = \begin{cases}
0 & p < 0.35, \\
\dfrac{p - 0.35}{0.20} \cdot 0.50 & 0.35 \le p \le 0.55, \\
0.50 & 0.55 < p \le 0.70, \\
\dfrac{0.85 - p}{0.15} \cdot 0.50 & 0.70 < p \le 0.85, \\
0 & p > 0.85,
\end{cases} \tag{10}
$$

which applies an allocation haircut of up to 50 percentage points over
the post-peak cooldown window. The penalty is zero outside
$[0.35, 0.85]$ cycle progress.

### 5.5 Floor Boost and Momentum Adjustment

Two smaller modifications complete the allocation function. A floor
boost adds up to $+30$ percentage points when $Z < 0.15$, scaled
inversely with the phase penalty so that it vanishes in the deepest
bear:

$$
\beta(Z, p) = 0.30 \cdot \max(0, 1 - 2\pi(p)) \cdot \max\!\left(0, \frac{0.15 - Z}{0.15}\right) \cdot \mathbb{1}_{Z < 0.15}. \tag{11}
$$

A momentum adjustment uses the 90-day-forward change in the heartbeat
pulse:

$$
\gamma(t) = \text{clip}\!\bigl(0.3 \cdot (H(p(t + 90d), c) - H(p(t), c)), \; -0.10, \; 0.10\bigr). \tag{12}
$$

### 5.6 Final Allocation

The recommended allocation is

$$
\alpha(t, P) = \text{clip}\bigl(\alpha_{\text{value}}(Z) - \pi(p) + \gamma(t) + \beta(Z, p), \; 0, \; 1\bigr). \tag{13}
$$

All components are bounded and deterministic given $(t, P)$. The
function has no hidden state, no stochastic component, and no
dependency on historical price beyond the floor and ceiling derivations,
which in turn depend only on $t$.

---

## 6. Operational Framework

### 6.1 The Role of the Model

We emphasise that the framework is **not designed to maximise realised
return relative to buy-and-hold**. Passive holding of a monotonically
appreciating asset is difficult to outperform [@sharpe1991], and brief
absences from the position during parabolic phases are costly. Our
objective is different.

The framework functions as a **psychological governor and volatility
damper**:

1. It prevents all-in commitments at criticality (high $Z$, post-peak
   phase), where historical drawdowns have exceeded 80%.
2. It provides objective permission to accumulate at ground-state
   (low $Z$, post-bear phase), when sentiment is typically worst.
3. It converts a continuous portfolio decision into a handful of
   discrete decisions per year, reducing cognitive load to a level
   that a human can execute without timing-based second-guessing.

### 6.2 Rebalancing Policy

Given a target $\alpha(t, P)$ and a current allocation
$\alpha_{\text{curr}}(t)$, we trigger a rebalance when

$$
\lvert \alpha(t, P) - \alpha_{\text{curr}}(t) \rvert \ge \tau, \tag{14}
$$

with threshold $\tau = 0.22$ as the default. Derivation: a sweep over
$\tau \in \{0.01, 0.05, 0.10, 0.15, 0.22, 0.30\}$ on the 2014--2026
window demonstrates a concave relationship between rebalancing
intensity and realised return (Table 1). The optimum sits near
$\tau = 0.22$; tighter thresholds pay excessive transaction costs,
looser thresholds miss structural shifts.

**Table 1.** Threshold sweep, 2014--2026, fee rate $0.3\%$, $\$1{,}000$ initial capital.

| Threshold $\tau$ | Trades | Final value | Strategy / HODL |
|:---:|---:|---:|---:|
| $0.01$ | $1{,}123$ | $\$385{,}612$ | $1.84\times$ |
| $0.15$ | $70$ | $\$273{,}037$ | $1.31\times$ |
| **$0.22$** | **$48$** | **$\$532{,}683$** | **$2.55\times$** |
| $0.30$ | $28$ | — | $\approx 2.20\times$ |

**Principal finding.** **Fewer, bigger moves dominate.** A threshold of
$\tau = 0.22$ produces approximately 4 to 8 trades per year and absorbs
large value chunks at genuine cycle turning points, without the
compounding drag of fee, slippage, and realisation-tax costs that
afflict tighter thresholds.

### 6.3 Drawdown Reduction

Table 2 reports the drawdown comparison against buy-and-hold on the
2017--2025 window at $\tau = 0.15$ (the earlier-generation threshold
for which we have the most extensive out-of-sample evidence).

**Table 2.** Strategy vs. HODL performance, 2017--2025.

| Metric | HODL | Strategy |
|:---|---:|---:|
| Total return | $21.3\times$ | $32.2\times$ |
| CAGR | $\approx 54\%$ | $\approx 73\%$ |
| Maximum drawdown | $-83\%$ | $-50\%$ |
| Sharpe ratio | $0.76$ | $1.12$ |
| Trades per year | $0$ | $\approx 6$ |

The drawdown halving is the operationally significant result. A
$-83\%$ drawdown demands psychological endurance that most investors do
not possess in practice; a $-50\%$ drawdown, while still severe, is
survivable for a broader class of participants. We interpret the
$1.68\times$ excess return as a by-product of the volatility
management, not a primary objective.

---

## 7. Backtest Evidence: Rolling Windows

To assess robustness we run the strategy on rolling 2-year windows
stepping every 90 days across 2014--2026 at $\tau = 0.22$.

**Table 3.** Rolling-window summary, $\tau = 0.22$.

| Metric | Value |
|:---|---:|
| Windows tested | 38 |
| Mean strategy/HODL ratio | $1.68\times$ |
| Median strategy/HODL ratio | $1.52\times$ |
| Win rate vs. HODL | $84\%$ |
| Worst window | $0.85\times$ |
| Best window | $3.21\times$ |

The distribution of window-level results is right-skewed, with the
right tail driven by bear-to-bull transition windows (e.g., 2018--2020,
2022--2024) in which the phase penalty keeps the strategy in cash
through the bottom and the floor boost re-enters at depth. The left
tail is driven by straight-line bull-market windows in which the
strategy trims too early relative to peak.

---

## 8. The Finite-Size Limit: Phase Transition Forecast

The framework as specified above assumes that the power-law regime
persists indefinitely. This assumption is unsustainable on physical
grounds.

### 8.1 Saturation Boundaries

The power-law growth projected by (1) implies super-exponential
appreciation over multi-decade horizons. Projecting the floor forward
to 2030 yields $P_{\text{floor}}(2030) \approx 2.6 \times 10^{5}$ USD
per BTC, and to 2035 yields $P_{\text{floor}}(2035) \approx 1.0 \times 10^{6}$
USD per BTC. At fully-diluted supply of $2.1 \times 10^{7}$ coins, these
imply market capitalisations of approximately $\$5.5$ trillion in 2030
and $\$21$ trillion in 2035. The latter is comparable to the total
capitalisation of investable gold.

**Table 4.** Projected collision with planetary-scale reservoirs.

| Reservoir | Approx. cap (current) | Year of floor collision |
|:---|---:|:---:|
| 10% of global M2 | $\sim\!\$12$T | 2029--2031 |
| Investable gold | $\sim\!\$18$T | 2030--2032 |
| Global public equity (1%) | $\sim\!\$1.1$T | passed 2024 |

### 8.2 Expected Regime Shift

As Bitcoin's market capitalisation approaches the scale of these
reservoirs, the marginal capital required to sustain the historical
growth exponent increases. Physical intuition suggests a logistic
(S-curve) saturation rather than unbounded power-law growth. We
anticipate a three-phase trajectory:

1. **Phase 1 — Volumetric growth (to approximately 2029).** Power-law
   regime as specified. The framework applies without modification.
2. **Phase 2 — Drag (approximately 2029--2035).** Growth exponent
   begins to deviate measurably from $B = 5.73$ toward lower values.
   Observed price will spend more time below the modelled floor.
   Volatility continues to decay, in line with the Kleiber amplitude
   term, but the floor itself becomes an increasingly pessimistic
   reference.
3. **Phase 3 — Saturation (post approximately 2035).** Logistic
   regime. Bitcoin behaves as a mature store-of-value asset whose
   growth tracks broad economic aggregates (M2, nominal GDP) rather
   than a steep network-effect curve.

### 8.3 Implications for the Framework

Phases 2 and 3 require a successor framework. The present model will
report increasingly low position scores and increasingly high
allocations through the transition, which is the correct behaviour if
the underlying thesis is sound (a maturing asset absorbing capital) but
is distinguishable in principle from a terminal breakdown only in
retrospect.

We commit explicitly to **retiring, not re-tuning, the current
framework** when the cumulative evidence makes the present parameter set
untenable. Criteria for retirement:

- A full halving cycle (approximately 4 years) completes with observed
  price sustained materially below the calibrated floor.
- The four-year halving rhythm ceases to produce a visible heartbeat
  over two consecutive cycles.
- An alternative framework derivable from first principles, rather
  than phenomenological fit, becomes available.

---

## 9. Limitations and Threats to Validity

**Overfitting.** The framework has five calibrated constants
($A, B, \alpha, k, \delta$) and six derived parameters
($\mu, \sigma_{\text{up}}, \sigma_{\text{down}}(c), \tau$, floor-boost
and phase-penalty envelopes). Against a fifteen-year daily price
series with fewer than ten major structural turning points, the risk
of in-sample overfit is non-trivial. We mitigate this by fixing
$k$ and $\delta$ on structural grounds (biological and halving-schedule
arguments) rather than fitting them, and by reporting rolling-window
results in Section 7.

**Regime dependence.** The calibration assumes persistence of the
four-year halving cycle as the dominant rhythm. A transition to
institutional-flow-dominated dynamics — already visible on the margin
post-2024 — may render the heartbeat pulse progressively less
predictive.

**Reflexivity.** Any widely-adopted allocation rule that systematically
buys floors and sells ceilings will compress the amplitude of future
cycles, reducing the magnitude of the very feature the framework
exploits. The framework remains profitable under moderate reflexivity
but the 2.55$\times$ backtest edge will shrink.

**Non-financial-advice disclosure.** The framework is a research
artefact. It is not personalised investment advice. Specific
implementation decisions (tax treatment, venue selection, position
sizing relative to net worth) require individual consideration that no
general framework can provide.

**Black-swan exclusion.** The framework has no opinion on tail events:
regulatory prohibition, protocol failure, sustained custody compromise
at scale, or the discovery of a cryptographic break. All of these would
invalidate the floor assumption and potentially the asset itself.

---

## 10. Conclusion

We have presented a deterministic, stateless framework for Bitcoin
portfolio allocation that requires only calendar date and spot price as
inputs, produces allocations in $[0, 1]$, and is calibrated on 15
years of daily data. The framework is phenomenological — we offer
biological and physical analogies as motivation for functional form,
not as derivations — and we document its calibration, coverage, and
robustness openly.

Two results are operationally significant. First, a rebalancing
threshold of approximately 22% allocation deviation optimises the
trade-off between signal capture and transaction-cost drag, producing
approximately four to eight trades per year and a backtested
strategy-to-HODL ratio of 2.55$\times$ over 2014--2026. Second, the
strategy approximately halves the maximum drawdown relative to
buy-and-hold, making a long-horizon Bitcoin position accessible to a
broader class of participants than pure HODL.

We also commit to the framework's eventual retirement. The power-law
regime is time-limited by the physical saturation of the global
capital base. Our expected transition window is 2029--2035, after
which we expect Bitcoin to behave as a mature store-of-value asset and
this framework to be superseded.

---

## Acknowledgements

The author thanks the practitioners and researchers whose published
work on Bitcoin power-law scaling — particularly Harold Christopher
Burger and Giovanni Santostasi — provided the empirical foundation
and much of the intellectual starting point for this work. Remaining
errors are the author's.

---

## References

- [@burger2019] Burger, H.C. (2019). *Bitcoin's natural long-term
  power-law corridor of growth.* Medium.
- [@burniske2018] Burniske, C. and Tatar, J. (2018). *Cryptoassets:
  The Innovative Investor's Guide to Bitcoin and Beyond.* McGraw-Hill.
- [@kelly1956] Kelly, J.L. (1956). A new interpretation of information
  rate. *Bell System Technical Journal*, 35(4), 917--926.
- [@kleiber1932] Kleiber, M. (1932). Body size and metabolism.
  *Hilgardia*, 6(11), 315--353.
- [@maclean2010] MacLean, L.C., Thorp, E.O. and Ziemba, W.T. (eds.)
  (2010). *The Kelly Capital Growth Investment Criterion.* World
  Scientific.
- [@metcalfe1995] Metcalfe, R. (1995). Metcalfe's Law: A network
  becomes more valuable as it reaches more users. *InfoWorld*, 17(40).
- [@miller2010] Miller, M. (2010). Up the escalator, down the elevator
  — market-wisdom idiom describing asymmetric price action.
- [@nakamoto2008] Nakamoto, S. (2008). *Bitcoin: A Peer-to-Peer
  Electronic Cash System.* Whitepaper.
- [@santostasi2024] Santostasi, G. (2024). *The Bitcoin Power Law
  Theory.* SSRN preprint.
- [@sharpe1991] Sharpe, W.F. (1991). The arithmetic of active
  management. *Financial Analysts Journal*, 47(1), 7--9.
- [@sun2006] Sun, W., Fan, A., Chen, L-W., Schouwenaars, T. and
  Albota, M.A. (2006). Optimal rebalancing for institutional
  portfolios. *The Journal of Portfolio Management*, 32(2), 33--43.
- [@west1999] West, G.B., Brown, J.H. and Enquist, B.J. (1999). The
  fourth dimension of life: fractal geometry and allometric scaling of
  organisms. *Science*, 284(5420), 1677--1679.

---

## Appendix A: Calibrated Constants

The framework has five calibrated numerical constants and several
derived parameters.

| Symbol | Value | Role | Calibration |
|:---:|:---:|:---|:---|
| $A$ | $-17.0$ | Floor log-intercept | OLS fit, 2011--present |
| $B$ | $5.73$ | Floor exponent | OLS fit, 2011--present |
| $\alpha$ | $40.0$ | Spike amplitude | Cycle-2 (2013) peak |
| $k$ | $0.75$ | Kleiber exponent | Fixed on structural grounds |
| $\delta$ | $0.5$ | Per-halving decay | Fixed on structural grounds |
| $\mu$ | $0.33$ | Peak cycle-progress | Empirical (2013/17/21 peaks) |
| $\sigma_{\text{up}}$ | $0.18$ | Pulse build-up width | Empirical |
| $\sigma_{\text{down}}(c)$ | $0.08 + 0.01c$ | Pulse contraction width | Empirical |
| $\tau$ | $0.22$ | Rebalancing threshold | Threshold sweep, 2014--2026 |

All constants are locked pending explicit retirement of the framework
(Section 8.3).

## Appendix B: Reproduction

The full reference implementation is available at
[github.com/Chris0x88/power-law-allocation](https://github.com/Chris0x88/power-law-allocation).
Key entry points:

- `src/power_law/model.py` — floor, ceiling, heartbeat, allocation, backtest.
- `src/power_law/rebalancer.py` — reference rebalancing loop.
- `scripts/generate_chart.py` — daily BTC/USD from Bitstamp + Binance;
  regenerates Figure 1.

Results reported in this paper are reproducible end-to-end with
`python examples/quickstart.py` for the signal, and
`python -c "from power_law import backtest; ..."` for the backtest tables.
