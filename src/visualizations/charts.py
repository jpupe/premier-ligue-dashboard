"""
Centralised Plotly chart factory for the PL Analytics dashboard.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from src.utils.constants import PLOTLY_TEMPLATE, TEAM_COLORS, DEFAULT_TEAM_COLOR
from src.utils.helpers import get_team_color

_BG = "#0d1117"
_GRID = "#21262d"
_TEXT = "#e6edf3"
_SUB = "#8b949e"


def _base_layout(**kwargs) -> dict:
    base = dict(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=_BG,
        plot_bgcolor="#161b22",
        font=dict(family="Inter, Segoe UI, sans-serif", color=_TEXT),
        xaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID, tickfont=dict(color=_SUB)),
        yaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID, tickfont=dict(color=_SUB)),
        margin=dict(l=60, r=30, t=60, b=60),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=_GRID, font=dict(color=_TEXT)),
        hoverlabel=dict(bgcolor="#1c2128", bordercolor="#30363d", font_color=_TEXT),
    )
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# Radar chart
# ---------------------------------------------------------------------------
def radar_chart(players_data: list[dict], metrics: list[str],
                labels: list[str], title: str = "") -> go.Figure:
    """
    players_data: list of {"name": str, "values": [0-100 percentile scores]}
    """
    palette = ["#8b5cf6", "#3fb950", "#f59e0b", "#f87171", "#60a5fa"]
    fig = go.Figure()
    for i, player in enumerate(players_data):
        vals = player["values"] + [player["values"][0]]   # close polygon
        cats = labels + [labels[0]]
        color = palette[i % len(palette)]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=cats, name=player["name"],
            fill="toself",
            fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15)",
            line=dict(color=color, width=2),
            marker=dict(size=6, color=color),
        ))

    fig.update_layout(
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(size=9, color=_SUB),
                gridcolor=_GRID, linecolor=_GRID,
                tickvals=[20, 40, 60, 80, 100],
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color=_TEXT),
                linecolor=_GRID, gridcolor=_GRID,
            ),
        ),
        paper_bgcolor=_BG,
        font=dict(color=_TEXT, family="Inter, Segoe UI, sans-serif"),
        title=dict(text=title, font=dict(size=15, color=_TEXT), x=0.5),
        legend=dict(orientation="h", y=-0.15, font=dict(color=_TEXT),
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=50, r=50, t=60, b=60),
        hoverlabel=dict(bgcolor="#1c2128", bordercolor="#30363d", font_color=_TEXT),
    )
    return fig


# ---------------------------------------------------------------------------
# Time series / line chart
# ---------------------------------------------------------------------------
def time_series(df: pd.DataFrame, x: str, y: str | list[str],
                color_col: str | None = None, title: str = "",
                y_label: str = "") -> go.Figure:
    if isinstance(y, str):
        y = [y]

    palette = ["#8b5cf6", "#3fb950", "#f59e0b", "#f87171", "#60a5fa",
               "#fb923c", "#a78bfa", "#34d399"]
    fig = go.Figure()

    if color_col and color_col in df.columns:
        for i, val in enumerate(df[color_col].unique()):
            sub = df[df[color_col] == val].sort_values(x)
            color = get_team_color(val) if color_col == "team" else palette[i % len(palette)]
            for metric in y:
                if metric not in sub.columns:
                    continue
                fig.add_trace(go.Scatter(
                    x=sub[x], y=sub[metric], name=f"{val}",
                    mode="lines+markers",
                    line=dict(color=color, width=2.5),
                    marker=dict(size=7, color=color,
                                line=dict(color="#0d1117", width=1.5)),
                ))
    else:
        for i, metric in enumerate(y):
            if metric not in df.columns:
                continue
            sub = df.sort_values(x)
            color = palette[i % len(palette)]
            fig.add_trace(go.Scatter(
                x=sub[x], y=sub[metric], name=metric,
                mode="lines+markers",
                line=dict(color=color, width=2.5),
                marker=dict(size=7, color=color,
                            line=dict(color="#0d1117", width=1.5)),
            ))

    layout = _base_layout(title=dict(text=title, font=dict(size=15, color=_TEXT), x=0.5))
    layout["yaxis"]["title"] = y_label
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# Bar chart
# ---------------------------------------------------------------------------
def bar_chart(df: pd.DataFrame, x: str, y: str,
              color_col: str | None = None, title: str = "",
              orientation: str = "v", n_max: int = 20) -> go.Figure:
    df = df.head(n_max).copy()

    if color_col and color_col in df.columns:
        colors = [get_team_color(t) if color_col == "team" else "#6e40c9"
                  for t in df[color_col]]
    else:
        colors = "#6e40c9"

    if orientation == "h":
        fig = go.Figure(go.Bar(
            x=df[y], y=df[x], orientation="h",
            marker=dict(color=colors, line=dict(color="rgba(0,0,0,0)")),
            hovertemplate=f"<b>%{{y}}</b><br>{y}: %{{x}}<extra></extra>",
        ))
        fig.update_layout(yaxis=dict(autorange="reversed"))
    else:
        fig = go.Figure(go.Bar(
            x=df[x], y=df[y],
            marker=dict(color=colors, line=dict(color="rgba(0,0,0,0)")),
            hovertemplate=f"<b>%{{x}}</b><br>{y}: %{{y}}<extra></extra>",
        ))

    layout = _base_layout(title=dict(text=title, font=dict(size=15, color=_TEXT), x=0.5))
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# Scatter plot
# ---------------------------------------------------------------------------
def scatter_plot(df: pd.DataFrame, x: str, y: str,
                 size: str | None = None, color_col: str | None = None,
                 hover_name: str | None = None, title: str = "",
                 trend_line: bool = True) -> go.Figure:
    kw = dict(
        x=x, y=y,
        template=PLOTLY_TEMPLATE,
        title=title,
    )
    if size and size in df.columns:
        kw["size"] = size
        kw["size_max"] = 30
    if color_col and color_col in df.columns:
        kw["color"] = color_col
        if color_col == "team":
            kw["color_discrete_map"] = TEAM_COLORS
        elif color_col == "position":
            kw["color_discrete_map"] = {
                "FW": "#f87171", "MF": "#60a5fa",
                "DF": "#4ade80", "GK": "#facc15",
            }
    if hover_name and hover_name in df.columns:
        kw["hover_name"] = hover_name

    tl = "ols" if trend_line else None
    fig = px.scatter(df, trendline=tl, **kw)

    layout = _base_layout(title=dict(text=title, font=dict(size=15, color=_TEXT), x=0.5))
    fig.update_layout(**layout)
    fig.update_traces(marker=dict(line=dict(color="#0d1117", width=1)))
    return fig


# ---------------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------------
def heatmap(df: pd.DataFrame, x: str, y: str, z: str,
            title: str = "") -> go.Figure:
    pivot = df.pivot_table(values=z, index=y, columns=x, aggfunc="mean")
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, "#161b22"], [0.5, "#6e40c9"], [1, "#8b5cf6"]],
        hoverongaps=False,
        hovertemplate=f"{x}: %{{x}}<br>{y}: %{{y}}<br>{z}: %{{z:.1f}}<extra></extra>",
    ))
    layout = _base_layout(title=dict(text=title, font=dict(size=15, color=_TEXT), x=0.5))
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# Grouped bar (team radar-like comparison)
# ---------------------------------------------------------------------------
def grouped_bar(df: pd.DataFrame, groups: str, metrics: list[str],
                title: str = "") -> go.Figure:
    palette = ["#8b5cf6", "#3fb950", "#f59e0b", "#f87171", "#60a5fa",
               "#fb923c", "#a78bfa", "#34d399"]
    fig = go.Figure()
    for i, row in df.iterrows():
        name = row[groups]
        color = get_team_color(name) if groups == "team" else palette[int(i) % len(palette)]
        fig.add_trace(go.Bar(
            name=name,
            x=metrics,
            y=[row.get(m, 0) for m in metrics],
            marker_color=color,
        ))
    layout = _base_layout(
        title=dict(text=title, font=dict(size=15, color=_TEXT), x=0.5),
        barmode="group",
    )
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# Score gauge (PPS / TDI)
# ---------------------------------------------------------------------------
def score_gauge(value: float, title: str, max_val: float = 100) -> go.Figure:
    normalized = min(100, max(0, value))
    if normalized >= 75:
        color = "#3fb950"
    elif normalized >= 50:
        color = "#6e40c9"
    elif normalized >= 25:
        color = "#d29922"
    else:
        color = "#f85149"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(font=dict(size=36, color=_TEXT)),
        gauge=dict(
            axis=dict(range=[0, max_val], tickfont=dict(color=_SUB)),
            bar=dict(color=color, thickness=0.25),
            bgcolor="#161b22",
            bordercolor="#30363d",
            steps=[
                dict(range=[0, 25], color="#1a1a2e"),
                dict(range=[25, 50], color="#16213e"),
                dict(range=[50, 75], color="#0f3460"),
                dict(range=[75, 100], color="#1a1a5e"),
            ],
            threshold=dict(line=dict(color=color, width=3), thickness=0.8,
                           value=value),
        ),
        title=dict(text=title, font=dict(size=13, color=_TEXT)),
        domain={"x": [0, 1], "y": [0, 1]},
    ))
    fig.update_layout(
        paper_bgcolor=_BG,
        font=dict(color=_TEXT),
        margin=dict(l=20, r=20, t=50, b=20),
        height=220,
    )
    return fig


# ---------------------------------------------------------------------------
# PCA / cluster scatter
# ---------------------------------------------------------------------------
def cluster_scatter(df: pd.DataFrame, title: str = "Player Clusters") -> go.Figure:
    cluster_colors = {
        0: "#8b5cf6", 1: "#3fb950", 2: "#f59e0b",
        3: "#f87171", 4: "#60a5fa",
    }
    fig = go.Figure()
    for cluster_id in sorted(df["cluster"].unique()):
        sub = df[df["cluster"] == cluster_id]
        name = sub["cluster_name"].iloc[0] if "cluster_name" in sub.columns else f"Cluster {cluster_id}"
        color = cluster_colors.get(cluster_id, "#8b949e")
        fig.add_trace(go.Scatter(
            x=sub["pc1"], y=sub["pc2"], mode="markers",
            name=name,
            marker=dict(size=8, color=color, opacity=0.8,
                        line=dict(color="#0d1117", width=1)),
            text=sub.get("player_name", sub.index),
            hovertemplate="<b>%{text}</b><br>PC1: %{x:.2f}<br>PC2: %{y:.2f}<extra></extra>",
        ))
    layout = _base_layout(
        title=dict(text=title, font=dict(size=15, color=_TEXT), x=0.5),
        xaxis=dict(title="Principal Component 1", gridcolor=_GRID),
        yaxis=dict(title="Principal Component 2", gridcolor=_GRID),
    )
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# Points progression over season chart
# ---------------------------------------------------------------------------
def points_progression(teams_data: dict[str, list], title: str = "") -> go.Figure:
    """
    teams_data: {team_name: [pts_s1, pts_s2, ...]}
    """
    palette = ["#8b5cf6", "#3fb950", "#f59e0b", "#f87171", "#60a5fa",
               "#fb923c", "#a78bfa", "#34d399"]
    fig = go.Figure()
    for i, (team, points) in enumerate(teams_data.items()):
        color = get_team_color(team) if team in TEAM_COLORS else palette[i % len(palette)]
        fig.add_trace(go.Scatter(
            y=points, mode="lines+markers", name=team,
            line=dict(color=color, width=2.5),
            marker=dict(size=7, color=color, line=dict(color="#0d1117", width=1.5)),
        ))
    layout = _base_layout(
        title=dict(text=title or "Points Progression", font=dict(size=15, color=_TEXT), x=0.5),
        yaxis=dict(title="Points", gridcolor=_GRID),
    )
    fig.update_layout(**layout)
    return fig
