"""Generate the hero chart image for the README.

Produces two files:
  chart/model_hero.png        — main README banner (wide, 30-year view)
  chart/model_zoom.png        — ±5-year zoom around today

Usage:
    python scripts/generate_chart.py
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from power_law.model import (
    HALVINGS,
    DAYS_PER_CYCLE,
    ceiling_price,
    cycle_index,
    cycle_progress,
    floor_price,
    get_halving_date,
    model_price,
    position_score,
    allocation_signal,
)


# ============================================================================
# DATA
# ============================================================================

def _fetch_bitstamp(start: datetime, end: datetime) -> pd.DataFrame:
    """Daily BTC/USD closes from Bitstamp (covers 2011-08 onward)."""
    rows = []
    step = 86400  # 1 day in seconds
    cur = int(start.timestamp())
    stop = int(end.timestamp())
    while cur < stop:
        r = requests.get(
            "https://www.bitstamp.net/api/v2/ohlc/btcusd/",
            params={"step": step, "limit": 1000, "start": cur},
            timeout=20,
        )
        r.raise_for_status()
        ohlc = r.json().get("data", {}).get("ohlc", [])
        if not ohlc:
            break
        rows.extend(ohlc)
        last_ts = int(ohlc[-1]["timestamp"])
        if last_ts <= cur:
            break
        cur = last_ts + step
        time.sleep(0.15)
    if not rows:
        return pd.DataFrame(columns=["price"])
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["timestamp"].astype(int), unit="s")
    df["price"] = df["close"].astype(float)
    return df.set_index("date")[["price"]]


def _fetch_binance(start: datetime, end: datetime) -> pd.DataFrame:
    """Daily BTCUSDT closes from Binance (covers 2017-08 onward)."""
    rows = []
    cur = int(start.timestamp() * 1000)
    stop = int(end.timestamp() * 1000)
    while cur < stop:
        r = requests.get(
            "https://api.binance.com/api/v3/klines",
            params={"symbol": "BTCUSDT", "interval": "1d", "startTime": cur, "limit": 1000},
            timeout=15,
        )
        r.raise_for_status()
        k = r.json()
        if not k:
            break
        rows.extend(k)
        cur = k[-1][0] + 1
        time.sleep(0.15)
    if not rows:
        return pd.DataFrame(columns=["price"])
    df = pd.DataFrame(rows, columns=[
        "ts", "open", "high", "low", "close", "volume",
        "close_time", "qv", "trades", "tbbav", "tbqav", "ignore",
    ])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    df["price"] = df["close"].astype(float)
    return df.set_index("date")[["price"]]


def fetch_btc_history() -> pd.DataFrame:
    """Fetch clean daily BTC/USD prices from 2011 onward.

    Stitches Bitstamp (2011-08 → 2017-07) with Binance BTCUSDT (2017-08 →
    today). Both sources return daily closes, so the join is seamless.
    """
    frames: list[pd.DataFrame] = []

    try:
        print("Fetching 2011-2017 from Bitstamp...")
        bs = _fetch_bitstamp(datetime(2011, 8, 18), datetime(2017, 8, 16))
        if len(bs):
            print(f"  Bitstamp: {len(bs)} days from {bs.index.min().date()} to {bs.index.max().date()}")
            frames.append(bs)
    except Exception as e:
        print(f"  Bitstamp failed: {e}")

    try:
        print("Fetching 2017+ from Binance...")
        bn = _fetch_binance(datetime(2017, 8, 17), datetime.now())
        if len(bn):
            print(f"  Binance: {len(bn)} days from {bn.index.min().date()} to {bn.index.max().date()}")
            frames.append(bn)
    except Exception as e:
        print(f"  Binance failed: {e}")

    if not frames:
        # Last-resort fallback
        try:
            print("Falling back to Yahoo Finance...")
            import yfinance as yf
            df = yf.Ticker("BTC-USD").history(period="max", interval="1d")
            if df.empty:
                raise RuntimeError("empty")
            df.index = df.index.tz_localize(None)
            return df.rename(columns={"Close": "price"})[["price"]]
        except Exception as e:
            print(f"  Yahoo failed: {e}")
        raise RuntimeError("Could not fetch BTC history from any source")

    joined = pd.concat(frames).sort_index()
    joined = joined[~joined.index.duplicated(keep="last")]
    return joined


# ============================================================================
# STYLING
# ============================================================================

BG = "#0b0e13"
PANEL = "#141821"
TEXT = "#e7ecf3"
DIM = "#8b95a8"
ACCENT = "#ffb347"
GREEN = "#3ec28f"
RED = "#e5616d"
PURPLE = "#b794f6"
WHITE = "#ffffff"


def apply_dark_style():
    plt.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor": PANEL,
        "savefig.facecolor": BG,
        "axes.edgecolor": "#222b3c",
        "axes.labelcolor": TEXT,
        "axes.titlecolor": TEXT,
        "xtick.color": DIM,
        "ytick.color": DIM,
        "grid.color": "#222b3c",
        "grid.alpha": 0.6,
        "grid.linestyle": ":",
        "text.color": TEXT,
        "font.family": ["DejaVu Sans", "Helvetica Neue", "Helvetica", "Arial"],
        "font.size": 11,
    })


# ============================================================================
# CHART BUILDERS
# ============================================================================

def compute_reference_lines(start, end, step_days=3):
    dates = pd.date_range(start=start, end=end, freq=f"{step_days}D")
    floor = np.array([floor_price(d.to_pydatetime()) for d in dates])
    ceil = np.array([ceiling_price(d.to_pydatetime()) for d in dates])
    model = np.array([model_price(d.to_pydatetime()) for d in dates])
    return dates, floor, ceil, model


def draw_halvings(ax, start, end, future_count=3):
    ylim = ax.get_ylim()
    all_halvings = list(HALVINGS)
    for i in range(1, future_count + 1):
        all_halvings.append(get_halving_date(len(HALVINGS) + i))
    for i, h in enumerate(all_halvings):
        if start <= h <= end:
            ax.axvline(h, color=PURPLE, linestyle="--", alpha=0.25, linewidth=0.9)
            ax.text(
                h, ylim[0] * 2.0, f" H{i+1}",
                color=PURPLE, alpha=0.8, fontsize=9, fontweight="bold",
                verticalalignment="bottom",
            )


def render_hero(btc_df: pd.DataFrame, out_path: Path):
    apply_dark_style()
    fig, ax = plt.subplots(figsize=(16, 8.5), dpi=160)

    start = datetime(2012, 1, 1)
    end = datetime(2034, 1, 1)
    dates, floor, ceil, model = compute_reference_lines(start, end, step_days=3)

    # Shaded fair-value band (floor → ceiling)
    ax.fill_between(dates, floor, ceil, color=ACCENT, alpha=0.04, zorder=1)

    # Model fair value (heartbeat midpoint) — subtle
    ax.plot(dates, model, color=ACCENT, linewidth=1.4, linestyle="--",
            alpha=0.75, label="Model fair value", zorder=3)

    # Floor
    ax.plot(dates, floor, color=GREEN, linewidth=2.2, alpha=0.95,
            label="Power-law floor", zorder=4)

    # Ceiling
    ax.plot(dates, ceil, color=RED, linewidth=2.2, alpha=0.95,
            label="Cycle ceiling (Kleiber decay)", zorder=4)

    # Actual BTC price
    mask = (btc_df.index >= start) & (btc_df.index <= end)
    actual = btc_df.loc[mask]
    if len(actual):
        ax.plot(actual.index, actual["price"], color=WHITE, linewidth=1.4,
                alpha=0.92, label="BTC price", zorder=5)

    ax.set_yscale("log")
    ax.set_ylim(1e-2, 1e7)
    ax.set_xlim(start, end)

    # Today marker
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if start <= today <= end:
        ax.axvline(today, color=ACCENT, linewidth=1.5, alpha=0.7, linestyle="-")

        # Badge with current signal
        try:
            latest_price = float(actual["price"].iloc[-1]) if len(actual) else None
        except Exception:
            latest_price = None
        if latest_price:
            pos = position_score(today, latest_price) * 100
            alloc = allocation_signal(today, latest_price) * 100
            badge_text = (
                f"Today  ${latest_price:,.0f}\n"
                f"Position: {pos:.0f}% of band\n"
                f"Allocation: {alloc:.0f}% BTC"
            )
            ax.text(
                0.985, 0.975, badge_text,
                transform=ax.transAxes,
                fontsize=11, color=TEXT, family="monospace",
                verticalalignment="top", horizontalalignment="right",
                bbox=dict(boxstyle="round,pad=0.6", facecolor="#1c2230",
                          edgecolor="#3a4458", linewidth=1),
                zorder=20,
            )

    # Title block
    fig.text(0.062, 0.955, "Power-Law Allocation",
             fontsize=22, fontweight="bold", color=TEXT)
    fig.text(0.062, 0.920,
             "Bitcoin: power-law floor · Kleiber-decay ceiling · heartbeat fair value",
             fontsize=12, color=DIM)

    # Axes
    ax.set_xlabel("Year", fontsize=11, color=DIM)
    ax.set_ylabel("Price (USD, log)", fontsize=11, color=DIM)
    ax.grid(True, which="both", axis="y", alpha=0.2)
    ax.grid(True, which="major", axis="x", alpha=0.2)

    # Nicer y ticks ($1, $100, $10k, $1M)
    ax.yaxis.set_major_locator(plt.FixedLocator([1e-2, 1, 1e2, 1e4, 1e6]))
    ax.set_yticklabels(["$0.01", "$1", "$100", "$10K", "$1M"])

    # Halving markers
    draw_halvings(ax, start, end, future_count=2)

    # Legend
    leg = ax.legend(
        loc="upper left", fontsize=10.5, frameon=True,
        facecolor="#1c2230", edgecolor="#3a4458", framealpha=0.92,
        labelcolor=TEXT,
    )
    leg.get_frame().set_linewidth(1)

    # Footer
    fig.text(0.062, 0.025,
             "Floor: P = 10⁻¹⁷ · d^5.73   ·   Ceiling: Floor × (1 + 40·c^−0.75·0.5^(c−2))   ·   Heartbeat peaks at 33% cycle progress",
             fontsize=10, color=DIM, family="monospace")
    fig.text(0.938, 0.025,
             "github.com/Chris0x88/power-law-allocation",
             fontsize=9.5, color=DIM, horizontalalignment="right")

    fig.subplots_adjust(left=0.062, right=0.985, top=0.88, bottom=0.085)
    fig.savefig(out_path, dpi=160, facecolor=BG)
    plt.close(fig)
    print(f"Wrote {out_path}")


def render_zoom(btc_df: pd.DataFrame, out_path: Path):
    """Narrower zoom: ±5 years around today."""
    apply_dark_style()
    fig, ax = plt.subplots(figsize=(14, 7), dpi=160)

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=365 * 6)
    end = today + timedelta(days=365 * 5)

    dates, floor, ceil, model = compute_reference_lines(start, end, step_days=2)

    ax.fill_between(dates, floor, ceil, color=ACCENT, alpha=0.05, zorder=1)
    ax.plot(dates, model, color=ACCENT, linewidth=1.6, linestyle="--",
            alpha=0.8, label="Model fair value")
    ax.plot(dates, floor, color=GREEN, linewidth=2.2, label="Floor")
    ax.plot(dates, ceil, color=RED, linewidth=2.2, label="Ceiling")

    mask = (btc_df.index >= start) & (btc_df.index <= end)
    actual = btc_df.loc[mask]
    if len(actual):
        ax.plot(actual.index, actual["price"], color=WHITE,
                linewidth=1.6, alpha=0.95, label="BTC price")

    ax.set_yscale("log")
    ax.set_xlim(start, end)

    if len(actual):
        y_lo = max(1000, float(actual["price"].min()) * 0.3)
    else:
        y_lo = max(floor.min() * 0.5, 1000)
    y_hi = max(ceil.max() * 1.3, 1e6)
    ax.set_ylim(y_lo, y_hi)

    ax.axvline(today, color=ACCENT, linewidth=1.5, alpha=0.7)
    draw_halvings(ax, start, end, future_count=2)

    fig.text(0.06, 0.955, "Model zoom: ±5 years around today",
             fontsize=16, fontweight="bold", color=TEXT)

    ax.set_xlabel("Year", color=DIM)
    ax.set_ylabel("Price (USD, log)", color=DIM)
    ax.grid(True, which="major", alpha=0.2)
    ax.legend(loc="upper left", fontsize=10.5, frameon=True,
              facecolor="#1c2230", edgecolor="#3a4458", framealpha=0.92,
              labelcolor=TEXT)

    fig.subplots_adjust(left=0.07, right=0.985, top=0.905, bottom=0.08)
    fig.savefig(out_path, dpi=160, facecolor=BG)
    plt.close(fig)
    print(f"Wrote {out_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    chart_dir = ROOT / "chart"
    chart_dir.mkdir(exist_ok=True)

    btc = fetch_btc_history()
    render_hero(btc, chart_dir / "model_hero.png")
    render_zoom(btc, chart_dir / "model_zoom.png")


if __name__ == "__main__":
    main()
