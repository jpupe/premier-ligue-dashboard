import pandas as pd
import numpy as np
from src.utils.constants import TEAM_COLORS, DEFAULT_TEAM_COLOR


def get_team_color(team: str) -> str:
    return TEAM_COLORS.get(team, DEFAULT_TEAM_COLOR)


def format_number(value, decimals: int = 1) -> str:
    if pd.isna(value):
        return "N/A"
    if isinstance(value, (int, np.integer)):
        return f"{value:,}"
    return f"{value:,.{decimals}f}"


def safe_divide(a, b, default=0.0) -> float:
    if b == 0 or pd.isna(b):
        return default
    return a / b


def percentile_rank(series: pd.Series, value: float) -> float:
    """Return the percentile (0–100) of value within series."""
    valid = series.dropna()
    if len(valid) == 0:
        return 50.0
    return float(np.sum(valid <= value) / len(valid) * 100)


def normalize_series(series: pd.Series) -> pd.Series:
    """Min-max normalization to [0, 100]."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(50.0, index=series.index)
    return (series - min_val) / (max_val - min_val) * 100


def rank_color(rank: int, total: int) -> str:
    """Return a color based on rank position."""
    pct = rank / total
    if pct <= 0.10:
        return "#3fb950"
    if pct <= 0.33:
        return "#8b5cf6"
    if pct <= 0.66:
        return "#d29922"
    return "#8b949e"


def season_to_year(season: str) -> int:
    """Convert '2022-23' to 2022."""
    return int(season.split("-")[0])


def build_per90_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add per-90 columns for all countable metrics."""
    minutes = df["minutes"].replace(0, np.nan)
    per90_map = {
        "goals": "goals_per90",
        "assists": "assists_per90",
        "xG": "xG_per90",
        "xA": "xA_per90",
        "shots": "shots_per90",
        "key_passes": "key_passes_per90",
        "progressive_passes": "progressive_passes_per90",
        "progressive_carries": "progressive_carries_per90",
        "tackles": "tackles_per90",
        "interceptions": "interceptions_per90",
        "blocks": "blocks_per90",
        "aerial_duels_won": "aerial_duels_won_per90",
    }
    out = df.copy()
    for raw, per90 in per90_map.items():
        if raw in out.columns:
            out[per90] = (out[raw] / minutes * 90).round(2)
    return out


def card_delta_color(value: float) -> str:
    if value > 0:
        return "normal"
    if value < 0:
        return "inverse"
    return "off"
