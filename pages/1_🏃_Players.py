"""
Player Analysis Page — comparison, career history, radar, scatter.
"""

import streamlit as st
import pandas as pd
import numpy as np

from src.data.loader import load_players, get_player_names
from src.data.processor import (
    filter_players, get_player_career_df, compute_percentiles, top_performers
)
from src.metrics.scores import calculate_pps
from src.visualizations.styles import inject_css, render_logo, section_header, position_badge
from src.visualizations.charts import (
    radar_chart, time_series, scatter_plot, bar_chart, score_gauge
)
from src.utils.constants import (
    SEASONS, POSITIONS, POSITION_FULL,
    RADAR_METRICS_FW, RADAR_METRICS_MF, RADAR_METRICS_DF, RADAR_METRICS_GK,
    RADAR_LABELS, PLAYER_METRIC_LABELS,
)

st.set_page_config(page_title="Players · PL Analytics", page_icon="🏃", layout="wide")
inject_css()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
players_df = load_players()
players_with_pps = calculate_pps(players_df)

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
render_logo()
st.sidebar.markdown("### Filtros")

season_filter = st.sidebar.multiselect(
    "Temporadas", SEASONS, default=[SEASONS[-1]], key="p_seasons"
)
position_filter = st.sidebar.multiselect(
    "Posições", POSITIONS,
    format_func=lambda p: POSITION_FULL[p],
    default=POSITIONS, key="p_positions"
)
min_minutes = st.sidebar.slider("Mínimo de minutos", 0, 3420, 450, 90, key="p_min_min")

filtered_df = filter_players(
    players_with_pps,
    seasons=season_filter or None,
    positions=position_filter or None,
    min_minutes=min_minutes,
)

featured_names = sorted(players_df[players_df["is_featured"]]["player_name"].unique().tolist())
all_names = sorted(players_df["player_name"].unique().tolist())

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<h1 style='font-size:2rem;font-weight:900;color:#e6edf3;margin-bottom:4px;'>
    🏃 Análise de Jogadores
</h1>
<p style='color:#8b949e;margin-top:0;'>Comparação, histórico e perfil estatístico</p>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Comparação de Jogadores", "Análise Individual", "Top Performers"])

# ============================================================
# TAB 1 — Player comparison
# ============================================================
with tab1:
    st.markdown(section_header("Selecione até 5 Jogadores"), unsafe_allow_html=True)
    selected_players = st.multiselect(
        "Jogadores para comparar",
        all_names,
        default=featured_names[:3] if len(featured_names) >= 3 else featured_names,
        max_selections=5,
        key="compare_players",
    )

    if not selected_players:
        st.info("Selecione pelo menos um jogador para iniciar a comparação.")
        st.stop()

    compare_season = st.selectbox(
        "Temporada de referência para radar",
        SEASONS, index=len(SEASONS) - 1, key="compare_season"
    )

    # --- Stat table ---
    comp_rows = []
    for name in selected_players:
        row = filtered_df[filtered_df["player_name"] == name]
        if row.empty:
            row = players_with_pps[players_with_pps["player_name"] == name]
        if not row.empty:
            agg = row.groupby("player_name").agg({
                "goals": "sum", "assists": "sum", "xG": "sum", "xA": "sum",
                "minutes": "sum", "matches_played": "sum",
                "goal_contributions": "sum",
                "progressive_passes": "sum", "tackles": "sum",
                "position": "first", "team": lambda x: x.mode()[0],
                "pps": "mean",
            }).reset_index()
            min_sum = agg["minutes"].iloc[0]
            per90 = 90 / max(1, min_sum)
            agg["goals_per90"] = round(agg["goals"] * per90, 2)
            agg["assists_per90"] = round(agg["assists"] * per90, 2)
            comp_rows.append(agg.iloc[0])

    if comp_rows:
        comp_df = pd.DataFrame(comp_rows).set_index("player_name")
        display_cols = ["team", "position", "goals", "assists", "xG", "xA",
                        "goals_per90", "assists_per90", "goal_contributions",
                        "minutes", "pps"]
        col_labels = {
            "team": "Time", "position": "Pos", "goals": "Gols", "assists": "Ass.",
            "xG": "xG", "xA": "xA", "goals_per90": "G/90", "assists_per90": "A/90",
            "goal_contributions": "G+A", "minutes": "Min.", "pps": "PPS",
        }
        st.dataframe(
            comp_df[[c for c in display_cols if c in comp_df.columns]]
              .rename(columns=col_labels)
              .style.format(precision=2)
              .background_gradient(cmap="Purples", subset=["PPS"] if "PPS" in col_labels.values() else []),
            use_container_width=True,
        )

    # --- Radar charts ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(section_header("Radar de Percentis"), unsafe_allow_html=True)

    # Determine radar metrics from first player's position
    first_pos = "FW"
    for name in selected_players:
        row = players_with_pps[(players_with_pps["player_name"] == name) &
                               (players_with_pps["season"] == compare_season)]
        if not row.empty:
            first_pos = row.iloc[0]["position"]
            break

    radar_map = {"FW": RADAR_METRICS_FW, "MF": RADAR_METRICS_MF,
                 "DF": RADAR_METRICS_DF, "GK": RADAR_METRICS_GK}
    radar_metrics = radar_map.get(first_pos, RADAR_METRICS_FW)
    radar_labels = [RADAR_LABELS.get(m, m) for m in radar_metrics]

    position_pool = players_with_pps[
        (players_with_pps["position"] == first_pos) &
        (players_with_pps["season"] == compare_season) &
        (players_with_pps["minutes"] >= 450)
    ]

    radar_data = []
    for name in selected_players:
        player_row = players_with_pps[
            (players_with_pps["player_name"] == name) &
            (players_with_pps["season"] == compare_season)
        ]
        if player_row.empty:
            latest = players_with_pps[players_with_pps["player_name"] == name]
            if latest.empty:
                continue
            player_row = latest.sort_values("season").tail(1)
        pr = player_row.iloc[0]
        percentiles = []
        for m in radar_metrics:
            if m not in position_pool.columns or m not in player_row.columns:
                percentiles.append(50.0)
                continue
            pool_vals = position_pool[m].dropna()
            val = pr.get(m, 0)
            if len(pool_vals) == 0:
                pct = 50.0
            else:
                pct = float(np.sum(pool_vals <= val) / len(pool_vals) * 100)
            percentiles.append(round(pct, 1))
        radar_data.append({"name": name, "values": percentiles})

    if radar_data:
        fig_radar = radar_chart(radar_data, radar_metrics, radar_labels,
                                title=f"Percentis por Posição ({first_pos}) · {compare_season}")
        st.plotly_chart(fig_radar, use_container_width=True)

    # --- Career timeline comparison ---
    st.markdown(section_header("Evolução de Gols por Temporada"), unsafe_allow_html=True)
    career_rows = []
    for name in selected_players:
        cd = get_player_career_df(players_df, name)
        cd["player_name"] = name
        career_rows.append(cd)

    if career_rows:
        career_all = pd.concat(career_rows, ignore_index=True)
        fig_career = time_series(
            career_all, x="season", y="goals", color_col="player_name",
            title="Gols por Temporada", y_label="Gols",
        )
        st.plotly_chart(fig_career, use_container_width=True)

    fig_assists = time_series(
        career_all, x="season", y="assists", color_col="player_name",
        title="Assistências por Temporada", y_label="Assistências",
    )
    st.plotly_chart(fig_assists, use_container_width=True)


# ============================================================
# TAB 2 — Individual analysis
# ============================================================
with tab2:
    individual_player = st.selectbox(
        "Selecione um jogador",
        featured_names + [n for n in all_names if n not in featured_names],
        key="individual_player",
    )
    ind_season = st.selectbox("Temporada de referência", SEASONS,
                              index=len(SEASONS) - 1, key="ind_season")

    career_df = get_player_career_df(players_df, individual_player)

    if career_df.empty:
        st.warning("Nenhum dado encontrado para este jogador.")
    else:
        info_row = career_df.sort_values("season").iloc[-1]
        pos = info_row["position"]
        pos_badge = position_badge(pos)

        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:16px;padding:16px;
                    background:#161b22;border:1px solid #30363d;border-radius:12px;
                    margin-bottom:16px;'>
            <div style='font-size:3rem;'>
                {"🥅" if pos=="GK" else "🛡️" if pos=="DF" else "⚙️" if pos=="MF" else "⚽"}
            </div>
            <div>
                <div style='font-size:1.5rem;font-weight:800;color:#e6edf3;'>
                    {individual_player}
                </div>
                <div style='margin-top:4px;'>{pos_badge}
                    <span style='color:#8b949e;font-size:0.85rem;margin-left:8px;'>
                        {info_row.get("nationality","—")} · {info_row.get("team","—")}
                        · {int(info_row.get("age", 0))} anos
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Career KPIs
        total_min = career_df["minutes"].sum()
        per90 = 90 / max(1, total_min)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Gols (carreira)", int(career_df["goals"].sum()))
        c2.metric("Assistências", int(career_df["assists"].sum()))
        c3.metric("xG total", f"{career_df['xG'].sum():.1f}")
        c4.metric("G/90", f"{career_df['goals'].sum() * per90:.2f}")
        c5.metric("Temporadas", len(career_df))

        # Season-by-season table
        st.markdown(section_header("Histórico por Temporada"), unsafe_allow_html=True)
        show_cols = ["season", "team", "age", "matches_played", "minutes",
                     "goals", "assists", "xG", "xA", "goals_per90", "assists_per90",
                     "goal_contributions", "yellow_cards"]
        st.dataframe(
            career_df[show_cols].sort_values("season")
              .rename(columns={
                  "season": "Temporada", "team": "Time", "age": "Idade",
                  "matches_played": "JJ", "minutes": "Min.",
                  "goals": "G", "assists": "A", "xG": "xG", "xA": "xA",
                  "goals_per90": "G/90", "assists_per90": "A/90",
                  "goal_contributions": "G+A", "yellow_cards": "CA",
              })
              .style.format(precision=2),
            use_container_width=True,
        )

        # Charts
        fig_g = time_series(career_df, x="season", y=["goals", "xG"],
                            title="Gols vs xG por Temporada")
        st.plotly_chart(fig_g, use_container_width=True)

        fig_a = time_series(career_df, x="season", y=["assists", "xA"],
                            title="Assistências vs xA por Temporada")
        st.plotly_chart(fig_a, use_container_width=True)

        # PPS gauge for selected season
        pps_row = players_with_pps[
            (players_with_pps["player_name"] == individual_player) &
            (players_with_pps["season"] == ind_season)
        ]
        if not pps_row.empty and not pd.isna(pps_row.iloc[0].get("pps", np.nan)):
            pps_val = round(float(pps_row.iloc[0]["pps"]), 1)
            st.markdown(section_header(f"PPS · {ind_season}"), unsafe_allow_html=True)
            g1, g2 = st.columns([1, 2])
            with g1:
                st.plotly_chart(score_gauge(pps_val, "Player Performance Score"),
                                use_container_width=True)
            with g2:
                st.markdown(f"""
                <div class='info-box' style='margin-top:20px;'>
                <b>Player Performance Score (PPS)</b><br><br>
                O PPS é calculado normalizando métricas-chave para a posição do jogador
                ({POSITION_FULL.get(pos, pos)}) em percentis dentro do mesmo grupo de
                posição e temporada, depois aplicando pesos específicos de cada função.<br><br>
                <b>Pontuação: {pps_val}/100</b> —
                {"Elite" if pps_val >= 80 else "Muito bom" if pps_val >= 65 else
                 "Bom" if pps_val >= 50 else "Abaixo da média" if pps_val >= 35 else "Fraco"}
                </div>
                """, unsafe_allow_html=True)


# ============================================================
# TAB 3 — Top performers
# ============================================================
with tab3:
    st.markdown(section_header("Top Performers por Métrica"), unsafe_allow_html=True)

    tp_season = st.selectbox("Temporada", SEASONS, index=len(SEASONS) - 1, key="tp_season")
    tp_position = st.selectbox(
        "Posição", ["Todas"] + POSITIONS,
        format_func=lambda p: "Todas" if p == "Todas" else POSITION_FULL[p],
        key="tp_position"
    )
    tp_metric = st.selectbox(
        "Métrica",
        list(PLAYER_METRIC_LABELS.keys()),
        format_func=lambda m: PLAYER_METRIC_LABELS[m],
        key="tp_metric"
    )
    tp_n = st.slider("Número de jogadores", 5, 30, 15, key="tp_n")

    pos_arg = None if tp_position == "Todas" else tp_position
    top_df = top_performers(players_with_pps, tp_season, tp_metric, tp_n, pos_arg)

    if not top_df.empty:
        fig_top = bar_chart(
            top_df, x="player_name", y=tp_metric,
            color_col="team",
            title=f"Top {tp_n} — {PLAYER_METRIC_LABELS[tp_metric]} · {tp_season}",
            orientation="h",
        )
        st.plotly_chart(fig_top, use_container_width=True)

        st.dataframe(
            top_df.rename(columns={
                "player_name": "Jogador", "team": "Time", "position": "Pos",
                tp_metric: PLAYER_METRIC_LABELS[tp_metric],
            }),
            use_container_width=True,
        )

    # xG vs Goals scatter
    st.markdown(section_header("xG vs Gols — Todos os Jogadores"), unsafe_allow_html=True)
    scatter_data = players_with_pps[
        (players_with_pps["season"] == tp_season) &
        (players_with_pps["minutes"] >= 450) &
        (players_with_pps["position"] != "GK")
    ].copy()
    scatter_data["label"] = scatter_data.apply(
        lambda r: r["player_name"] if r.get("is_featured") else "", axis=1
    )
    fig_scatter = scatter_plot(
        scatter_data, x="xG", y="goals",
        size="minutes", color_col="position",
        hover_name="player_name",
        title=f"xG vs Gols · {tp_season}  (tamanho = minutos jogados)",
        trend_line=True,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
