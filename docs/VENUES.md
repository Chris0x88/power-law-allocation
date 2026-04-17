# Venues: Where to execute

The model says *what* to do. This doc addresses *where* to do it.

The power-law allocation strategy has specific execution requirements that
make some venues strictly better than others for this use case. The short
version: **we favour spot DEXes on low-cost chains, with
SaucerSwap on Hedera being our current pick.** This document explains why.

---

## 1. What the strategy actually demands of a venue

The rebalancer:

- Executes ~4–6 trades per year (at 22% threshold)
- Holds positions for multi-month periods between trades
- Needs a BTC-equivalent asset and a USD-equivalent stablecoin
- Does **not** need leverage
- Does **not** need complex order types
- Benefits from low fees and low / no holding costs

From that list, three properties matter most, in order:

1. **No holding fees.** You sit on a position for months. Anything that bleeds
   you while you wait destroys the strategy.
2. **Low transaction costs.** With only ~5 trades/year, per-trade fees dominate.
3. **Simple, self-custodial spot settlement.** No margin calls, no
   counterparty risk during the long holds.

Everything else (UI, liquidity depth on a specific pair, extra yield
opportunities) is downstream of these three.

---

## 2. The problem with perpetuals

Perpetual futures are the default "crypto exposure" venue for most traders.
For *this strategy*, they are strictly wrong.

### The funding rate kills you

Perps have funding rates paid every 1–8 hours by the long side to the short
side (or vice versa) to keep the perp price tethered to spot.

Typical BTC perp funding: **+0.01% per 8 hours** on average, or about
**+11% annualised** for a long position over time. On strong bull legs,
funding spikes to +0.1–0.3% per 8 hours — **100%+ annualised.**

We hold long for **months at a time** during accumulation phases. At 22%
threshold, a single position can run 3–9 months. Even at modest funding
rates, that's 5–30% bled off the top **before** price moves.

**This alone disqualifies perps.** The strategy is premised on free holding.

### Liquidation risk

Perps expose you to forced liquidation. The strategy specifically targets
buying the floor — where price is at its most volatile and drawdowns are
deepest. Running leveraged long into a floor touch is a direct path to
liquidation during the worst market conditions.

### Taxable treatment

In most jurisdictions, perps are treated as income, not capital gains. This
removes any long-term holding discount and compounds the drag.

### When perps do make sense

If you hold a large spot BTC position and the model says to trim to 30%:

- Option A: sell 70% of BTC → taxable gain
- Option B: short perps to synthetically hedge the difference

Option B can be tax-efficient if you hold for less than one funding cycle,
but for our multi-month holds the funding cost almost always exceeds the
tax saving. **Exception:** if you have unrealised gains in a very
high-tax jurisdiction (40%+), a short perp hedge can be worthwhile.

---

## 3. The case for SaucerSwap (Hedera)

SaucerSwap is a Uniswap V2/V3-style AMM running on the Hedera Hashgraph
network. For the rebalancer's requirements, it hits all three of the
constraints above better than most alternatives.

### 3.1 No holding fees — ever

Spot AMMs charge a fee **per swap**. Not per hour, not per day, not per block.
If you swap into WBTC and sit for nine months, your cost is **zero** over
those nine months. That aligns perfectly with a long-hold rebalancer.

### 3.2 Extremely low transaction costs

Hedera's transaction pricing is roughly fixed and USD-denominated, not
gas-auction-based:

- **Transaction cost: ~$0.001 per tx** (not a typo)
- **Swap fee: 0.05% – 0.30% depending on pool tier**

Compare to:

| Venue | Per-swap cost on $10k trade |
|-------|-----------------------------|
| Ethereum L1 DEX (Uniswap) | $5–100 in gas + 0.30% = $35–$130 |
| Arbitrum / Base L2 DEX | $0.20 gas + 0.30% = ~$30 |
| **SaucerSwap on Hedera** | **$0.001 gas + 0.05–0.30% = $5–$30** |
| Coinbase Pro | 0.40% spot taker = $40 |

Hedera's fixed-fee transaction model means you can ignore gas entirely when
budgeting. The variable cost is purely the swap fee tier, which you pick
when you route the trade.

### 3.3 Self-custody, no counterparty

Funds live in your wallet between trades. No exchange risk. No custodian.
No withdrawal delays. If Hedera itself goes away that's a risk, but it is
a very different risk shape than a centralised counterparty.

### 3.4 Liquidity is adequate for our size

At the time of writing, the BTC / USDC pool on SaucerSwap supports single-
trade notional in the $10k–$100k range with <0.3% slippage. That is more
than enough for any individual or small-treasury rebalancer.

For larger size, the rebalancer can be configured to split a single target
change across multiple ticks — the 22% threshold is not tight enough to
require same-block execution.

### 3.5 Optional LP upside

This is the **bonus** of the SaucerSwap choice, not the thesis.

The rebalancer needs to hold BTC and USDC between trades. During the long
holds, that capital can optionally be deployed as a **concentrated
liquidity position** in the BTC / USDC pool, earning swap fees from other
traders.

The LP strategy layers naturally on top of the rebalancer:

- When the model says "hold 50% BTC, 50% USDC" — that's exactly the
  asset mix a balanced LP position consumes.
- Fees earned are a small but real yield on what would otherwise be
  idle capital.
- When the model triggers a rebalance, you withdraw the LP, swap to the
  new target, and re-deploy.

**Caveats to be honest about:**

- Impermanent loss is real. For a balanced LP position, it scales with
  the square of the price ratio. Over a full cycle (10×+ price moves),
  IL can be material.
- Concentrated liquidity (V3-style) can be more capital-efficient but
  requires range management that conflicts with the strategy's multi-
  month holds. Wide ranges (2×–10×) are probably the right fit.
- LP yield varies with volume; don't model it as a fixed APR.

The LP layer is a **research direction**, not a load-bearing part of the
thesis. The rebalancer works fine without it.

---

## 4. Other acceptable venues

SaucerSwap is our preference, not a requirement. The rebalancer is venue-
agnostic. Other reasonable choices, roughly ordered by fit:

| Venue | Holding cost | Tx cost | Custody | Fit |
|-------|--------------|---------|---------|-----|
| **SaucerSwap (Hedera)** | None | **~$0.001 + 0.05–0.30%** | Self | **Best** |
| Uniswap on Base | None | $0.10 + 0.30% | Self | Good |
| Uniswap on Arbitrum | None | $0.20 + 0.30% | Self | Good |
| Curve/Uniswap on L1 | None | $20–$100 + 0.30% | Self | Only for large size |
| Coinbase Pro spot | None | 0.40% | Custodial | OK if self-custody not possible |
| Kraken spot | None | 0.26% | Custodial | OK |
| **Any perpetual futures** | **Funding (~10–100%+/yr)** | Varies | Custodial / on-chain | **Disqualified** |
| Options-based allocation | Theta decay | High | Varies | Over-engineered |
| Leveraged spot (margin) | Interest | — | Custodial | Disqualified |

The rule is simple: **spot, self-custody, low fees, no holding cost.**

---

## 5. Implementation notes for a SaucerSwap adapter

This repo does **not** ship a SaucerSwap adapter — by design. The point is
that the model and rebalancer are venue-agnostic. But if you're building
one, a few hard-won notes:

- **Deadlines are in milliseconds**, not seconds (the SaucerSwap V2 router
  quirk). Any `deadline = time.time() + 60` call will revert.
- **HTS token approvals** need the Hedera SDK, not a standard EVM `approve()`.
- **Native HBAR → HTS token** auto-wraps via `value`.
- **HTS token → native HBAR** requires a `multicall(exactInput + unwrapWHBAR)`.

If you plan to run on Hedera, read SaucerSwap's `SwapRouter02` and
`ERC20Wrapper` contracts directly rather than the docs — the docs are
incomplete.

---

## 6. Summary

| Property | Why it matters | SaucerSwap |
|----------|----------------|------------|
| No holding fees | Multi-month holds, no bleed | Spot AMM — zero holding cost |
| Low tx cost | 5 trades/yr, per-trade dominates | ~$0.001 gas + 0.05–0.30% swap |
| Self-custody | No counterparty risk during holds | Wallet-based |
| Liquidity | Needed for rebalance size | Adequate for <$100k trades |
| Optional yield | Bonus utility between trades | Concentrated LP available |

Perpetuals bleed you dry on funding. CEX spot ties you to a custodian. L1
DEXes make the per-trade cost dominate. SaucerSwap on Hedera threads the
needle.
