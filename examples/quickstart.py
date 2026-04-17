"""Minimal end-to-end example.

Run:  python examples/quickstart.py
"""
from datetime import datetime, timezone
from pathlib import Path
import sys

# Make the sibling src/ importable without installation
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from power_law import get_daily_signal, get_future_projections
from power_law.rebalancer import PaperVenue, Rebalancer, RebalancerConfig


def today_signal(btc_price: float) -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    s = get_daily_signal(now, btc_price)

    print("=" * 72)
    print("  POWER-LAW ALLOCATION MODEL  — Today's Signal")
    print("=" * 72)
    print(f"  Date:              {s['date']}")
    print(f"  BTC Price:         ${s['price']:,.0f}")
    print(f"  Floor:             ${s['floor']:,.0f}  (power-law equilibrium)")
    print(f"  Ceiling:           ${s['ceiling']:,.0f}  (cycle peak potential)")
    print(f"  Model fair value:  ${s['model_price']:,.0f}")
    print(f"  Position in band:  {s['position_in_band_pct']:.0f}%  → {s['valuation']}")
    print(f"  Cycle {s['cycle']}, {s['cycle_progress_pct']:.0f}% through — {s['phase']}")
    print()
    print(f"  >>> Recommended BTC allocation: {s['allocation_pct']:.0f}%  ({s['stance']}) <<<")
    print(f"  {s['tagline']}")
    print()


def future_view(btc_price: float) -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    proj = get_future_projections(now, btc_price)
    print("  Projection (if price stays at ${:,.0f}):".format(btc_price))
    print(f"  {'Period':<6}  {'Date':<12}  {'Floor':>10}  {'Fair':>10}  {'Ceiling':>12}  {'Alloc':>6}")
    for p in proj["projections"]:
        print(f"  {p['period']:<6}  {p['date']:<12}  ${p['floor']:>9,.0f}  ${p['model_price']:>9,.0f}  ${p['ceiling']:>11,.0f}  {p['allocation_pct']:>5.0f}%")
    print()


def paper_trade_demo(btc_price: float) -> None:
    venue = PaperVenue(btc=0.0, usd=10_000.0, _price=btc_price)
    config = RebalancerConfig(threshold_pct=0.22, fee_rate=0.003)
    r = Rebalancer(venue=venue, config=config)

    print("  Paper-trade demo ($10,000, 22% threshold):")
    r.tick()
    print(f"  → Holdings: {venue.btc:.4f} BTC, ${venue.usd:,.2f} USD")
    print()


if __name__ == "__main__":
    price = 95_000.0  # replace with live price
    today_signal(price)
    future_view(price)
    paper_trade_demo(price)
