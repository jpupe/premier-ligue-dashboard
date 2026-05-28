"""
Player Performance Score (PPS) and Team Dominance Index (TDI).

PPS methodology:
  Normalises each metric to [0, 100] using percentile rank within the same
  position group and season. Weighted combination varies by position to
  reflect different role demands.

TDI methodology:
  Four components — Attack, Defense, Control, Results — each normalised to
  [0, 100] and weighted to produce a final index.
"""

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# PPS weights by position
# ---------------------------------------------------------------------------
PPS_WEIGHTS = {
    "FW": {
        "goals_per90": 0.30,
        "xG_per90": 0.20,
        "assists_per90": 0.15,
        "xA_per90": 0.10,
        "shots_per90": 0.10,
        "progressive_carries_per90": 0.08,
        "key_passes_per90": 0.07,
    },
    "MF": {
        "assists_per90": 0.20,
        "key_passes_per90": 0.18,
        "progressive_passes_per90": 0.18,
        "goals_per90": 0.15,
        "xG_per90": 0.10,
        "tackles_per90": 0.10,
        "interceptions_per90": 0.09,
    },
    "DF": {
        "tackles_per90": 0.22,
        "interceptions_per90": 0.22,
        "blocks_per90": 0.14,
        "aerial_duels_won_per90": 0.18,
        "progressive_passes_per90": 0.14,
        "goals_per90": 0.05,
        "assists_per90": 0.05,
    },
    "GK": {
        "goals_per90": 0.10,   # proxy: low GA
        "assists_per90": 0.10,
        "progressive_passes_per90": 0.30,
        "tackles_per90": 0.25,
        "interceptions_per90": 0.25,
    },
}

# For GK we invert goals_against context; using available cols as proxy
PPS_WEIGHTS["GK"] = {
    "progressive_passes_per90": 0.35,
    "tackles_per90": 0.30,
    "interceptions_per90": 0.25,
    "aerial_duels_won_per90": 0.10,
}


def _percentile_normalize(series: pd.Series) -> pd.Series:
    """Convert series to [0, 100] percentile ranks."""
    valid = series.dropna()
    if len(valid) == 0:
        return pd.Series(50.0, index=series.index)
    ranks = series.rank(pct=True, na_option="keep") * 100
    return ranks.fillna(50.0)


def calculate_pps(df: pd.DataFrame, min_minutes: int = 450) -> pd.DataFrame:
    """
    Compute Player Performance Score for every (player, season) row.
    Returns df with added column 'pps' (0–100).
    """
    result_frames = []

    for (position, season), group in df.groupby(["position", "season"]):
        weights = PPS_WEIGHTS.get(position, PPS_WEIGHTS["MF"])
        group = group.copy()

        score = pd.Series(0.0, index=group.index)
        total_weight = 0.0

        for metric, weight in weights.items():
            if metric not in group.columns:
                continue
            normed = _percentile_normalize(group[metric])
            score += normed * weight
            total_weight += weight

        if total_weight > 0:
            score = score / total_weight
        else:
            score = pd.Series(50.0, index=group.index)

        group["pps"] = score.round(1)
        result_frames.append(group)

    if not result_frames:
        df["pps"] = 50.0
        return df

    out = pd.concat(result_frames, ignore_index=True)
    # Zero out players with too few minutes
    out.loc[out["minutes"] < min_minutes, "pps"] = np.nan
    return out


# ---------------------------------------------------------------------------
# TDI weights
# ---------------------------------------------------------------------------
TDI_WEIGHTS = {
    "attack":  0.35,   # goals_for, xG_for
    "defense": 0.35,   # goals_against (inverted), xG_against (inverted), clean_sheets
    "control": 0.15,   # possession
    "results": 0.15,   # points, win_percentage
}


def calculate_tdi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Team Dominance Index for every (team, season) row.
    Returns df with added column 'tdi' (0–100).
    """
    result_frames = []

    for season, group in df.groupby("season"):
        group = group.copy()

        # Attack: higher is better
        attack = (
            _percentile_normalize(group["goals_for"]) * 0.50 +
            _percentile_normalize(group["xG_for"]) * 0.50
        )

        # Defense: lower GA/xGA is better → invert by negating rank
        ga_inv = _percentile_normalize(-group["goals_against"])
        xga_inv = _percentile_normalize(-group["xG_against"])
        cs_norm = _percentile_normalize(group["clean_sheets"])
        defense = ga_inv * 0.40 + xga_inv * 0.35 + cs_norm * 0.25

        # Control
        control = _percentile_normalize(group["possession"])

        # Results
        results = (
            _percentile_normalize(group["points"]) * 0.60 +
            _percentile_normalize(group["win_percentage"]) * 0.40
        )

        tdi = (
            attack  * TDI_WEIGHTS["attack"]  +
            defense * TDI_WEIGHTS["defense"] +
            control * TDI_WEIGHTS["control"] +
            results * TDI_WEIGHTS["results"]
        )

        group["tdi"] = tdi.round(1)
        group["tdi_attack"] = attack.round(1)
        group["tdi_defense"] = defense.round(1)
        group["tdi_control"] = control.round(1)
        group["tdi_results"] = results.round(1)
        result_frames.append(group)

    if not result_frames:
        df["tdi"] = 50.0
        return df

    return pd.concat(result_frames, ignore_index=True)


def pps_ranking(df: pd.DataFrame, season: str,
                position: str | None = None, n: int = 20) -> pd.DataFrame:
    mask = (df["season"] == season) & df["pps"].notna()
    if position:
        mask &= df["position"] == position
    return (
        df[mask]
        .nlargest(n, "pps")[["player_name", "team", "position", "pps",
                              "goals", "assists", "minutes", "xG", "xA"]]
        .reset_index(drop=True)
    )


def tdi_ranking(df: pd.DataFrame, season: str, n: int = 20) -> pd.DataFrame:
    mask = df["season"] == season
    return (
        df[mask]
        .nlargest(n, "tdi")[["team", "tdi", "tdi_attack", "tdi_defense",
                              "tdi_control", "tdi_results",
                              "points", "goals_for", "goals_against"]]
        .reset_index(drop=True)
    )
