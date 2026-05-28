"""
Data transformation and filtering utilities.
"""

import pandas as pd
import numpy as np
from src.utils.helpers import build_per90_columns


def filter_players(
    df: pd.DataFrame,
    seasons: list[str] | None = None,
    positions: list[str] | None = None,
    teams: list[str] | None = None,
    min_minutes: int = 0,
) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    if seasons:
        mask &= df["season"].isin(seasons)
    if positions:
        mask &= df["position"].isin(positions)
    if teams:
        mask &= df["team"].isin(teams)
    if min_minutes > 0:
        mask &= df["minutes"] >= min_minutes
    return df[mask].copy()


def filter_teams(
    df: pd.DataFrame,
    seasons: list[str] | None = None,
    teams: list[str] | None = None,
) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    if seasons:
        mask &= df["season"].isin(seasons)
    if teams:
        mask &= df["team"].isin(teams)
    return df[mask].copy()


def aggregate_career(df: pd.DataFrame, player_name: str) -> pd.Series:
    """Sum and average a player's stats across all seasons."""
    p = df[df["player_name"] == player_name].copy()
    if p.empty:
        return pd.Series()

    total_minutes = p["minutes"].sum()
    per90 = 90 / max(1, total_minutes)

    numeric_sum = ["goals", "assists", "minutes", "matches_played",
                   "goal_contributions", "shots", "progressive_passes",
                   "progressive_carries", "tackles", "interceptions", "blocks",
                   "yellow_cards", "red_cards"]
    float_avg = ["xG", "xA"]

    result = {}
    for col in numeric_sum:
        if col in p.columns:
            result[col] = p[col].sum()
    for col in float_avg:
        if col in p.columns:
            result[col] = round(p[col].sum(), 1)

    result["goals_per90"] = round(result.get("goals", 0) * per90, 3)
    result["assists_per90"] = round(result.get("assists", 0) * per90, 3)
    result["xG_per90"] = round(result.get("xG", 0) * per90, 3)
    result["xA_per90"] = round(result.get("xA", 0) * per90, 3)
    result["seasons_played"] = len(p)
    result["teams"] = ", ".join(sorted(p["team"].unique()))

    return pd.Series(result)


def get_player_career_df(df: pd.DataFrame, player_name: str) -> pd.DataFrame:
    """Return season-by-season career rows for a player."""
    return df[df["player_name"] == player_name].sort_values("season").copy()


def compute_percentiles(df: pd.DataFrame, player_name: str,
                        season: str, metrics: list[str]) -> pd.Series:
    """Compute percentile ranks for a player within their position group."""
    row = df[(df["player_name"] == player_name) & (df["season"] == season)]
    if row.empty:
        return pd.Series()

    position = row.iloc[0]["position"]
    pool = df[(df["position"] == position) & (df["season"] == season) & (df["minutes"] >= 450)]

    percentiles = {}
    for m in metrics:
        if m not in pool.columns or m not in row.columns:
            continue
        val = row.iloc[0][m]
        series = pool[m].dropna()
        if len(series) == 0:
            percentiles[m] = 50.0
        else:
            percentiles[m] = round(float(np.sum(series <= val) / len(series) * 100), 1)
    return pd.Series(percentiles)


def top_performers(df: pd.DataFrame, season: str, metric: str, n: int = 10,
                   position: str | None = None) -> pd.DataFrame:
    mask = (df["season"] == season) & (df["minutes"] >= 450)
    if position:
        mask &= df["position"] == position
    return (
        df[mask]
        .nlargest(n, metric)[["player_name", "team", "position", metric]]
        .reset_index(drop=True)
    )
