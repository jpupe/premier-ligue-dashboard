"""
Premier League Analytics Dashboard — Home Page
"""

import streamlit as st
import pandas as pd

from src.data.loader import load_players, load_teams
from src.metrics.scores import calculate_pps, calculate_tdi
from src.visualizations.styles import inject_css, render_logo, section_header
from src.visualizations.charts import time_series, scatter_plot, bar_chart
from src.utils.constants import SEASONS

st.set_page_config(
    page_title="PL Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
render_logo()
st.sidebar.markdown("### Temporada Atual")
selected_season = st.sidebar.selectbox("", SEASONS, index=len(SEASONS) - 1,
                                       key="home_season")
st.sidebar.markdown("<hr style='border-color:#30363d;'>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='font-size:0.78rem;color:#8b949e;line-height:1.7;'>
<b style='color:#e6edf3;'>Navegação</b><br>
🏃 <b>Players</b> — Comparação individual<br>
🏆 <b>Teams</b> — Rankings e evolução<br>
⭐ <b>Scores</b> — PPS &amp; TDI<br>
🔬 <b>Advanced</b> — Clustering &amp; Scouting
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
players_df = load_players()
teams_df = load_teams()

players_with_pps = calculate_pps(players_df)
teams_with_tdi = calculate_tdi(teams_df)

season_players = players_with_pps[
    (players_with_pps["season"] == selected_season) &
    (players_with_pps["minutes"] >= 450)
]
season_teams = teams_with_tdi[teams_with_tdi["season"] == selected_season]

# ---------------------------------------------------------------------------
# Hero section
# ---------------------------------------------------------------------------
st.markdown("""
<div style='text-align:center;padding:32px 0 16px;'>
    <div style='font-size:3rem;margin-bottom:6px;'>⚽</div>
    <h1 style='font-size:2.4rem;font-weight:900;color:#e6edf3;margin:0;
               background:linear-gradient(135deg,#8b5cf6,#60a5fa);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
        Premier League Analytics
    </h1>
    <p style='color:#8b949e;font-size:1rem;margin-top:6px;'>
        Plataforma avançada de análise estatística e scouting · 2014–2024
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(section_header(f"Destaques da Temporada {selected_season}"), unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

top_scorer = season_players.nlargest(1, "goals").iloc[0] if not season_players.empty else None
top_assist = season_players.nlargest(1, "assists").iloc[0] if not season_players.empty else None
top_xg = season_players.nlargest(1, "xG").iloc[0] if not season_players.empty else None
top_team_pts = season_teams.nlargest(1, "points").iloc[0] if not season_teams.empty else None
avg_goals = round(season_teams["goals_for"].mean(), 1) if not season_teams.empty else 0

with c1:
    if top_scorer is not None:
        st.metric("⚽ Artilheiro",
                  f"{top_scorer['player_name'].split()[-1]}",
                  f"{int(top_scorer['goals'])} gols")
with c2:
    if top_assist is not None:
        st.metric("🎯 Assistências",
                  f"{top_assist['player_name'].split()[-1]}",
                  f"{int(top_assist['assists'])} ass.")
with c3:
    if top_xg is not None:
        st.metric("📊 Melhor xG",
                  f"{top_xg['player_name'].split()[-1]}",
                  f"xG {top_xg['xG']:.1f}")
with c4:
    if top_team_pts is not None:
        st.metric("🏆 Campeão",
                  f"{top_team_pts['team']}",
                  f"{int(top_team_pts['points'])} pts")
with c5:
    st.metric("⚡ Média Gols/Time", f"{avg_goals}", "por temporada")

st.markdown("<hr style='border-color:#30363d;margin:24px 0;'>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# League table
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown(section_header("Tabela da Liga"), unsafe_allow_html=True)
    if not season_teams.empty:
        table = (
            season_teams
            .sort_values("points", ascending=False)
            .reset_index(drop=True)
        )
        table.index = table.index + 1
        display_cols = ["team", "wins", "draws", "losses",
                        "goals_for", "goals_against", "goal_difference",
                        "points", "clean_sheets"]
        col_renames = {
            "team": "Time", "wins": "V", "draws": "E", "losses": "D",
            "goals_for": "GM", "goals_against": "GC", "goal_difference": "SG",
            "points": "Pts", "clean_sheets": "CS",
        }
        st.dataframe(
            table[display_cols].rename(columns=col_renames),
            use_container_width=True,
            height=580,
        )

with col_right:
    st.markdown(section_header("Top Marcadores"), unsafe_allow_html=True)
    if not season_players.empty:
        top10 = (
            season_players
            .nlargest(10, "goals")[["player_name", "team", "position", "goals", "xG"]]
            .reset_index(drop=True)
        )
        top10.index = top10.index + 1
        st.dataframe(
            top10.rename(columns={
                "player_name": "Jogador", "team": "Time",
                "position": "Pos", "goals": "Gols", "xG": "xG",
            }),
            use_container_width=True,
            height=270,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(section_header("Top Assistências"), unsafe_allow_html=True)
    if not season_players.empty:
        top10a = (
            season_players
            .nlargest(10, "assists")[["player_name", "team", "position", "assists", "xA"]]
            .reset_index(drop=True)
        )
        top10a.index = top10a.index + 1
        st.dataframe(
            top10a.rename(columns={
                "player_name": "Jogador", "team": "Time",
                "position": "Pos", "assists": "Ass.", "xA": "xA",
            }),
            use_container_width=True,
            height=270,
        )

st.markdown("<hr style='border-color:#30363d;margin:24px 0;'>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Historical trends
# ---------------------------------------------------------------------------
st.markdown(section_header("Tendências Históricas"), unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

tc1, tc2 = st.columns(2)

with tc1:
    top_teams_all = (
        teams_df.groupby("team")["points"].sum()
        .nlargest(6).index.tolist()
    )
    filtered = teams_df[teams_df["team"].isin(top_teams_all)]
    fig_pts = time_series(
        filtered, x="season", y="points", color_col="team",
        title="Pontos por Temporada — Top 6 Times",
        y_label="Pontos",
    )
    st.plotly_chart(fig_pts, use_container_width=True)

with tc2:
    goals_by_season = teams_df.groupby("season")["goals_for"].mean().reset_index()
    goals_by_season.columns = ["season", "avg_goals"]
    fig_goals = time_series(
        goals_by_season, x="season", y="avg_goals",
        title="Média de Gols por Time por Temporada",
        y_label="Gols (média)",
    )
    st.plotly_chart(fig_goals, use_container_width=True)

# ---------------------------------------------------------------------------
# xG scatter
# ---------------------------------------------------------------------------
st.markdown(section_header("xG vs Gols Marcados (Todos os Times)"), unsafe_allow_html=True)
fig_xg = scatter_plot(
    season_teams, x="xG_for", y="goals_for",
    color_col="team", hover_name="team",
    title=f"xG For vs Goals For · {selected_season}",
    trend_line=True,
)
st.plotly_chart(fig_xg, use_container_width=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("""
<div style='text-align:center;padding:32px 0;color:#484f58;font-size:0.78rem;'>
    Premier League Analytics Dashboard · Dados sintéticos baseados em padrões históricos reais<br>
    Construído com Streamlit, Plotly, DuckDB e scikit-learn
</div>
""", unsafe_allow_html=True)
