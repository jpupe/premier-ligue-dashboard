"""
Team-level metric calculations.
"""

import pandas as pd
import numpy as np


def build_team_summary(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["points_per_game"] = (out["points"] / out["matches_played"]).round(2)
    out["goals_per_game"] = (out["goals_for"] / out["matches_played"]).round(2)
    out["goals_conceded_per_game"] = (out["goals_against"] / out["matches_played"]).round(2)
    out["xg_diff"] = (out["xG_for"] - out["xG_against"]).round(1)
    return out


def season_table(df: pd.DataFrame, season: str) -> pd.DataFrame:
    """Return the league table for a given season."""
    s = df[df["season"] == season].copy()
    s = s.sort_values("points", ascending=False).reset_index(drop=True)
    s.index = s.index + 1
    s.index.name = "Pos"
    return s


def team_form(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """Season-by-season performance for a single team."""
    t = df[df["team"] == team].sort_values("season").copy()
    t["season_num"] = range(1, len(t) + 1)
    return t


def compare_teams(df: pd.DataFrame, teams: list[str],
                  seasons: list[str] | None = None) -> pd.DataFrame:
    mask = df["team"].isin(teams)
    if seasons:
        mask &= df["season"].isin(seasons)
    return df[mask].sort_values(["team", "season"]).copy()


def top_teams_metric(df: pd.DataFrame, metric: str,
                     season: str, n: int = 10) -> pd.DataFrame:
    s = df[df["season"] == season].copy()
    asc = metric in ("goals_against", "xG_against")
    return s.nsmallest(n, metric) if asc else s.nlargest(n, metric)
