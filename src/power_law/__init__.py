"""Power-Law Allocation Model — deterministic Bitcoin portfolio allocation.

Primary API:

    from power_law import get_daily_signal, allocation_signal

    signal = get_daily_signal(datetime.now(), btc_price=95000)
    print(signal["allocation_pct"])  # e.g. 42.0

See docs/MODEL.md for the math, docs/THESIS.md for the philosophy,
docs/REBALANCER.md for the rebalancing policy.
"""
from .model import (
    GENESIS,
    HALVINGS,
    PortfolioState,
    allocation_signal,
    backtest,
    ceiling_price,
    cycle_index,
    cycle_progress,
    floor_price,
    generate_tagline,
    get_daily_signal,
    get_future_projections,
    heartbeat_pulse,
    model_price,
    position_score,
    rebalance_to_target,
    sentiment_tags,
)

__all__ = [
    "GENESIS",
    "HALVINGS",
    "PortfolioState",
    "allocation_signal",
    "backtest",
    "ceiling_price",
    "cycle_index",
    "cycle_progress",
    "floor_price",
    "generate_tagline",
    "get_daily_signal",
    "get_future_projections",
    "heartbeat_pulse",
    "model_price",
    "position_score",
    "rebalance_to_target",
    "sentiment_tags",
]

__version__ = "1.0.0"
