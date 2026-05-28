"""
Team Analysis Page — league table, comparison, evolution, rankings.
"""

import streamlit as st
import pandas as pd
import numpy as np

from src.data.loader import load_teams
from src.metrics.team_metrics import (
    build_team_summary, season_table, team_form, compare_teams
)
from src.metrics.scores import calculate_tdi
from src.visualizations.styles import inject_css, render_logo, section_header
from src.visualizations.charts import (
    time_series, bar_chart, scatter_plot, heatmap, grouped_bar, score_gauge
)
from src.utils.constants import SEASONS, TEAM_METRICS, TEAM_METRIC_LABELS

st.set_page_config(page_title="Teams · PL Analytics", page_icon="🏆", layout="wide")
inject_css()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
teams_df = load_teams()
teams_df = build_team_summary(teams_df)
teams_with_tdi = calculate_tdi(teams_df)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
render_logo()
st.sidebar.markdown("### Filtros de Times")

all_teams = sorted(teams_df["team"].unique().tolist())
selected_season = st.sidebar.selectbox("Temporada", SEASONS,
                                       index=len(SEASONS) - 1, key="tm_season")
selected_teams = st.sidebar.multiselect(
    "Times para comparar", all_teams,
    default=["Manchester City", "Liverpool", "Arsenal", "Chelsea"],
    key="tm_teams",
)
season_range = st.sidebar.select_slider(
    "Intervalo de temporadas (histórico)",
    options=SEASONS, value=(SEASONS[0], SEASONS[-1]),
    key="tm_range",
)

range_seasons = SEASONS[SEASONS.index(season_range[0]):SEASONS.index(season_range[1]) + 1]

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<h1 style='font-size:2rem;font-weight:900;color:#e6edf3;margin-bottom:4px;'>
    🏆 Análise de Times
</h1>
<p style='color:#8b949e;margin-top:0;'>Comparação, evolução histórica e rankings por temporada</p>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Tabela e Rankings", "Comparação de Times", "Evolução Histórica"])

# ============================================================
# TAB 1 — League table & rankings
# ============================================================
with tab1:
    season_data = teams_with_tdi[teams_with_tdi["season"] == selected_season].copy()
    season_data = season_data.sort_values("points", ascending=False).reset_index(drop=True)
    season_data.index = season_data.index + 1

    # KPI bar
    if not season_data.empty:
        leader = season_data.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🥇 Campeão", leader["team"], f"{int(leader['points'])} pts")
        c2.metric("⚽ Mais Gols", season_data.nlargest(1, "goals_for").iloc[0]["team"],
                  f"{int(season_data.nlargest(1, 'goals_for').iloc[0]['goals_for'])} gols")
        c3.metric("🛡️ Menos Sofridos", season_data.nsmallest(1, "goals_against").iloc[0]["team"],
                  f"{int(season_data.nsmallest(1, 'goals_against').iloc[0]['goals_against'])} GC")
        c4.metric("📊 Maior TDI", season_data.nlargest(1, "tdi").iloc[0]["team"],
                  f"{season_data.nlargest(1, 'tdi').iloc[0]['tdi']:.1f}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(section_header(f"Tabela da Liga · {selected_season}"), unsafe_allow_html=True)

    if not season_data.empty:
        cols = ["team", "wins", "draws", "losses", "goals_for", "goals_against",
                "goal_difference", "points", "clean_sheets", "possession", "xG_for", "tdi"]
        renames = {
            "team": "Time", "wins": "V", "draws": "E", "losses": "D",
            "goals_for": "GM", "goals_against": "GC", "goal_difference": "SG",
            "points": "Pts", "clean_sheets": "CS",
            "possession": "Poss%", "xG_for": "xG", "tdi": "TDI",
        }
        st.dataframe(
            season_data[[c for c in cols if c in season_data.columns]]
              .rename(columns=renames)
              .style.format({"Poss%": "{:.1f}", "xG": "{:.1f}", "TDI": "{:.1f}"})
              .background_gradient(cmap="Purples", subset=["TDI"]),
            use_container_width=True,
            height=660,
        )

    # Ranking bars
    st.markdown(section_header("Rankings por Métrica"), unsafe_allow_html=True)
    rank_metric = st.selectbox(
        "Métrica", TEAM_METRICS,
        format_func=lambda m: TEAM_METRIC_LABELS[m],
        key="rank_metric"
    )
    asc = rank_metric in ("goals_against", "xG_against")
    rank_data = (
        season_data.nsmallest(10, rank_metric) if asc
        else season_data.nlargest(10, rank_metric)
    )
    fig_rank = bar_chart(
        rank_data.reset_index(), x="team", y=rank_metric, color_col="team",
        title=f"{TEAM_METRIC_LABELS[rank_metric]} · {selected_season}",
        orientation="h",
    )
    st.plotly_chart(fig_rank, use_container_width=True)


# ============================================================
# TAB 2 — Team comparison
# ============================================================
with tab2:
    if not selected_teams:
        st.info("Selecione times no filtro lateral para comparar.")
    else:
        comp_data = season_data[season_data["team"].isin(selected_teams)].copy()

        if comp_data.empty:
            st.warning(f"Times selecionados não participaram de {selected_season}.")
        else:
            # Summary metrics
            st.markdown(section_header(f"Comparação · {selected_season}"), unsafe_allow_html=True)
            metrics_to_show = ["points", "goals_for", "goals_against", "goal_difference",
                               "clean_sheets", "possession", "xG_for", "tdi"]
            fig_group = grouped_bar(
                comp_data.reset_index(), groups="team",
                metrics=metrics_to_show,
                title=f"Métricas por Time · {selected_season}",
            )
            st.plotly_chart(fig_group, use_container_width=True)

            # Radar for teams (using TDI sub-scores)
            st.markdown(section_header("TDI Componentes"), unsafe_allow_html=True)
            from src.visualizations.charts import radar_chart as rchart
            tdi_metrics = ["tdi_attack", "tdi_defense", "tdi_control", "tdi_results"]
            tdi_labels = ["Ataque", "Defesa", "Controle", "Resultados"]
            team_radar_data = []
            for _, row in comp_data.iterrows():
                vals = [float(row.get(m, 50)) for m in tdi_metrics]
                team_radar_data.append({"name": row["team"], "values": vals})
            if team_radar_data:
                fig_tdi = rchart(team_radar_data, tdi_metrics, tdi_labels,
                                 title=f"Componentes TDI · {selected_season}")
                st.plotly_chart(fig_tdi, use_container_width=True)

            # Data table
            st.dataframe(
                comp_data[["team", "wins", "draws", "losses", "goals_for",
                           "goals_against", "points", "clean_sheets",
                           "possession", "tdi"]]
                .rename(columns={
                    "team": "Time", "wins": "V", "draws": "E", "losses": "D",
                    "goals_for": "GM", "goals_against": "GC", "points": "Pts",
                    "clean_sheets": "CS", "possession": "Poss%", "tdi": "TDI",
                })
                .style.format({"Poss%": "{:.1f}", "TDI": "{:.1f}"}),
                use_container_width=True,
            )

            # xG scatter
            st.markdown(section_header("xG For vs xG Against"), unsafe_allow_html=True)
            fig_xg = scatter_plot(
                season_data, x="xG_for", y="xG_against",
                color_col="team", hover_name="team",
                title=f"xG For vs xG Against · {selected_season}",
                trend_line=False,
            )
            st.plotly_chart(fig_xg, use_container_width=True)


# ============================================================
# TAB 3 — Historical evolution
# ============================================================
with tab3:
    if not selected_teams:
        st.info("Selecione times no filtro lateral.")
    else:
        hist_data = teams_with_tdi[
            (teams_with_tdi["team"].isin(selected_teams)) &
            (teams_with_tdi["season"].isin(range_seasons))
        ].copy()

        if hist_data.empty:
            st.warning("Sem dados para os filtros selecionados.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                fig_pts = time_series(
                    hist_data, x="season", y="points", color_col="team",
                    title="Pontos por Temporada", y_label="Pontos",
                )
                st.plotly_chart(fig_pts, use_container_width=True)

            with c2:
                fig_pos = time_series(
                    hist_data, x="season", y="position", color_col="team",
                    title="Posição na Liga por Temporada", y_label="Posição",
                )
                # Invert y axis so position 1 is at top
                fig_pos.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_pos, use_container_width=True)

            c3, c4 = st.columns(2)
            with c3:
                fig_gf = time_series(
                    hist_data, x="season", y="goals_for", color_col="team",
                    title="Gols Marcados por Temporada", y_label="Gols",
                )
                st.plotly_chart(fig_gf, use_container_width=True)

            with c4:
                fig_ga = time_series(
                    hist_data, x="season", y="goals_against", color_col="team",
                    title="Gols Sofridos por Temporada", y_label="Gols Sofridos",
                )
                st.plotly_chart(fig_ga, use_container_width=True)

            # Possession heatmap
            st.markdown(section_header("Heatmap de Posse de Bola"), unsafe_allow_html=True)
            fig_heat = heatmap(
                hist_data[hist_data["team"].isin(selected_teams)],
                x="season", y="team", z="possession",
                title="Posse Média (%) por Time e Temporada",
            )
            st.plotly_chart(fig_heat, use_container_width=True)

            # Points & clean sheets table
            st.markdown(section_header("Resumo Histórico"), unsafe_allow_html=True)
            pivot_pts = hist_data.pivot_table(
                values="points", index="team", columns="season", aggfunc="sum"
            ).fillna(0).astype(int)
            pivot_pts["Total"] = pivot_pts.sum(axis=1)
            st.dataframe(pivot_pts.sort_values("Total", ascending=False),
                         use_container_width=True)
