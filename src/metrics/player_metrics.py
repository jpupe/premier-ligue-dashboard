"""
Player-level metric calculations.
"""

import pandas as pd
import numpy as np


def get_goal_involvement_rate(row: pd.Series) -> float:
    """Goals + assists as % of team goals (approx via xG)."""
    team_xg = row.get("team_xg", 50.0)
    return round(row.get("goal_contributions", 0) / max(1, team_xg) * 100, 1)


def get_shooting_efficiency(row: pd.Series) -> float:
    """Goals per shot on target."""
    sot = row.get("shots_on_target", 0)
    goals = row.get("goals", 0)
    if sot == 0:
        return 0.0
    return round(goals / sot * 100, 1)


def get_xg_overperformance(row: pd.Series) -> float:
    """Goals minus xG — positive means overperforming."""
    return round(row.get("goals", 0) - row.get("xG", 0), 2)


def get_chance_creation_rate(row: pd.Series) -> float:
    """Key passes per 90 minutes."""
    minutes = row.get("minutes", 0)
    kp = row.get("key_passes", 0)
    if minutes < 90:
        return 0.0
    return round(kp / minutes * 90, 2)


def build_player_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-season stats; compute derived metrics."""
    out = df.copy()
    out["xg_diff"] = (out["goals"] - out["xG"]).round(2)
    out["xa_diff"] = (out["assists"] - out["xA"]).round(2)
    out["shot_accuracy"] = np.where(
        out["shots"] > 0,
        (out["shots_on_target"] / out["shots"] * 100).round(1),
        0.0,
    )
    return out


def career_summary(df: pd.DataFrame, player_name: str) -> dict:
    p = df[df["player_name"] == player_name]
    if p.empty:
        return {}
    total_min = p["minutes"].sum()
    per90 = 90 / max(1, total_min)
    return {
        "seasons": len(p),
        "goals": int(p["goals"].sum()),
        "assists": int(p["assists"].sum()),
        "xG": round(p["xG"].sum(), 1),
        "xA": round(p["xA"].sum(), 1),
        "minutes": int(total_min),
        "matches": int(p["matches_played"].sum()),
        "goals_per90": round(p["goals"].sum() * per90, 2),
        "assists_per90": round(p["assists"].sum() * per90, 2),
        "goal_contributions": int(p["goal_contributions"].sum()),
        "yellow_cards": int(p["yellow_cards"].sum()),
    }
