"""
Scores Page — Player Performance Score (PPS) and Team Dominance Index (TDI).
"""

import streamlit as st
import pandas as pd
import numpy as np

from src.data.loader import load_players, load_teams
from src.metrics.scores import calculate_pps, calculate_tdi, pps_ranking, tdi_ranking
from src.visualizations.styles import inject_css, render_logo, section_header
from src.visualizations.charts import bar_chart, scatter_plot, score_gauge, time_series
from src.utils.constants import SEASONS, POSITIONS, POSITION_FULL

st.set_page_config(page_title="Scores · PL Analytics", page_icon="⭐", layout="wide")
inject_css()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
players_df = load_players()
teams_df = load_teams()
players_pps = calculate_pps(players_df)
teams_tdi = calculate_tdi(teams_df)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
render_logo()
st.sidebar.markdown("### Configurações")
score_season = st.sidebar.selectbox("Temporada", SEASONS,
                                    index=len(SEASONS) - 1, key="sc_season")
score_position = st.sidebar.selectbox(
    "Posição (PPS)", ["Todas"] + POSITIONS,
    format_func=lambda p: "Todas" if p == "Todas" else POSITION_FULL[p],
    key="sc_pos"
)
n_show = st.sidebar.slider("Top N jogadores/times", 5, 30, 20, key="sc_n")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<h1 style='font-size:2rem;font-weight:900;color:#e6edf3;margin-bottom:4px;'>
    ⭐ Scores: PPS &amp; TDI
</h1>
<p style='color:#8b949e;margin-top:0;'>
    Player Performance Score e Team Dominance Index — rankings e metodologia
</p>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Player Performance Score", "Team Dominance Index", "Metodologia"])

# ============================================================
# TAB 1 — PPS
# ============================================================
with tab1:
    pos_arg = None if score_position == "Todas" else score_position
    pps_df = pps_ranking(players_pps, score_season, pos_arg, n_show)

    st.markdown(section_header(f"Top {n_show} PPS · {score_season}"), unsafe_allow_html=True)

    if pps_df.empty:
        st.warning("Sem dados para os filtros selecionados.")
    else:
        # Bar chart
        fig_pps = bar_chart(
            pps_df, x="player_name", y="pps", color_col="team",
            title=f"Player Performance Score · {score_season}",
            orientation="h",
        )
        st.plotly_chart(fig_pps, use_container_width=True)

        # Table with styling
        st.dataframe(
            pps_df.rename(columns={
                "player_name": "Jogador", "team": "Time", "position": "Pos",
                "pps": "PPS", "goals": "Gols", "assists": "Ass.",
                "minutes": "Min.", "xG": "xG", "xA": "xA",
            })
            .style.format({"PPS": "{:.1f}", "xG": "{:.1f}", "xA": "{:.1f}"})
            .background_gradient(cmap="Purples", subset=["PPS"]),
            use_container_width=True,
        )

        # Gauges for top 3
        st.markdown(section_header("Top 3 Destaque"), unsafe_allow_html=True)
        g_cols = st.columns(3)
        for i, col in enumerate(g_cols):
            if i < len(pps_df):
                row = pps_df.iloc[i]
                with col:
                    st.plotly_chart(
                        score_gauge(float(row["pps"]),
                                    f"{row['player_name'].split()[0]} {row['player_name'].split()[-1][:3]}."),
                        use_container_width=True,
                    )
                    st.markdown(f"""
                    <div style='text-align:center;margin-top:-10px;'>
                        <b style='color:#e6edf3;'>{row['player_name']}</b><br>
                        <span style='color:#8b949e;font-size:0.8rem;'>
                            {row['team']} · {row['position']}
                        </span><br>
                        <span style='color:#8b5cf6;font-size:0.8rem;'>
                            {int(row.get('goals',0))}G · {int(row.get('assists',0))}A
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

    # PPS scatter: Goals/90 vs Assists/90 colored by PPS
    st.markdown(section_header("PPS — Distribuição por G/90 vs A/90"), unsafe_allow_html=True)
    scatter_data = players_pps[
        (players_pps["season"] == score_season) &
        (players_pps["minutes"] >= 450) &
        players_pps["pps"].notna()
    ].copy()
    if pos_arg:
        scatter_data = scatter_data[scatter_data["position"] == pos_arg]

    if not scatter_data.empty:
        fig_sc = scatter_plot(
            scatter_data, x="goals_per90", y="assists_per90",
            size="pps", color_col="position",
            hover_name="player_name",
            title=f"Gols/90 vs Assists/90 (tamanho = PPS) · {score_season}",
        )
        st.plotly_chart(fig_sc, use_container_width=True)

    # PPS evolution for featured players
    st.markdown(section_header("Evolução PPS — Jogadores Destaque"), unsafe_allow_html=True)
    featured = players_pps[players_pps["is_featured"] & players_pps["pps"].notna()]
    if pos_arg:
        featured = featured[featured["position"] == pos_arg]
    top_featured = featured.groupby("player_name")["pps"].mean().nlargest(6).index.tolist()
    feat_evo = featured[featured["player_name"].isin(top_featured)]
    if not feat_evo.empty:
        fig_evo = time_series(
            feat_evo, x="season", y="pps", color_col="player_name",
            title="Evolução do PPS por Temporada",
            y_label="PPS",
        )
        st.plotly_chart(fig_evo, use_container_width=True)


# ============================================================
# TAB 2 — TDI
# ============================================================
with tab2:
    tdi_df = tdi_ranking(teams_tdi, score_season, n_show)

    st.markdown(section_header(f"Team Dominance Index · {score_season}"), unsafe_allow_html=True)

    if tdi_df.empty:
        st.warning("Sem dados para a temporada selecionada.")
    else:
        fig_tdi = bar_chart(
            tdi_df, x="team", y="tdi", color_col="team",
            title=f"Team Dominance Index · {score_season}",
            orientation="h",
        )
        st.plotly_chart(fig_tdi, use_container_width=True)

        st.dataframe(
            tdi_df.rename(columns={
                "team": "Time", "tdi": "TDI",
                "tdi_attack": "Ataque", "tdi_defense": "Defesa",
                "tdi_control": "Controle", "tdi_results": "Resultados",
                "points": "Pts", "goals_for": "GM", "goals_against": "GC",
            })
            .style.format({
                "TDI": "{:.1f}", "Ataque": "{:.1f}", "Defesa": "{:.1f}",
                "Controle": "{:.1f}", "Resultados": "{:.1f}",
            })
            .background_gradient(cmap="Purples", subset=["TDI"]),
            use_container_width=True,
        )

        # TDI gauges for top 3
        st.markdown(section_header("Top 3 Times"), unsafe_allow_html=True)
        g_cols = st.columns(3)
        for i, col in enumerate(g_cols):
            if i < len(tdi_df):
                row = tdi_df.iloc[i]
                with col:
                    st.plotly_chart(
                        score_gauge(float(row["tdi"]), row["team"]),
                        use_container_width=True,
                    )

        # TDI sub-component stacked
        st.markdown(section_header("Componentes TDI — Top Times"), unsafe_allow_html=True)
        import plotly.graph_objects as go
        from src.utils.helpers import get_team_color

        top8 = tdi_df.head(8)
        comp_labels = ["Ataque", "Defesa", "Controle", "Resultados"]
        comp_cols = ["tdi_attack", "tdi_defense", "tdi_control", "tdi_results"]
        comp_colors = ["#f87171", "#60a5fa", "#4ade80", "#facc15"]

        fig_comp = go.Figure()
        for label, col, color in zip(comp_labels, comp_cols, comp_colors):
            fig_comp.add_trace(go.Bar(
                name=label,
                x=top8["team"],
                y=top8[col],
                marker_color=color,
            ))
        from src.visualizations.charts import _base_layout
        fig_comp.update_layout(
            barmode="stack",
            **_base_layout(
                title=dict(text="Componentes TDI · Top 8", font=dict(size=15), x=0.5)
            )
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        # TDI evolution
        st.markdown(section_header("Evolução TDI — Top Times Históricos"), unsafe_allow_html=True)
        top_teams_ever = (
            teams_tdi.groupby("team")["tdi"].mean()
            .nlargest(6).index.tolist()
        )
        tdi_evo = teams_tdi[teams_tdi["team"].isin(top_teams_ever)]
        fig_tdi_evo = time_series(
            tdi_evo, x="season", y="tdi", color_col="team",
            title="Evolução do TDI por Temporada",
            y_label="TDI",
        )
        st.plotly_chart(fig_tdi_evo, use_container_width=True)


# ============================================================
# TAB 3 — Methodology
# ============================================================
with tab3:
    st.markdown("""
    <h2 style='color:#e6edf3;'>Metodologia dos Scores</h2>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='info-box'>
    <h3 style='color:#8b5cf6;margin-top:0;'>Player Performance Score (PPS)</h3>

    O <b>PPS</b> é um índice de 0 a 100 que mede o desempenho individual de cada jogador
    dentro do contexto de sua posição e temporada.

    <br><br><b>Como é calculado:</b>
    <ol>
    <li>Para cada combinação posição + temporada, calculamos o <b>percentil</b> de cada
        jogador em cada métrica relevante (ex: Goals/90, xG/90 para atacantes).</li>
    <li>Os percentis são normalizados de 0 a 100.</li>
    <li>Uma média ponderada dos percentis produz o score final.</li>
    </ol>

    <b>Pesos por posição:</b><br>
    • <b>Atacante (FW)</b>: Goals/90 (30%), xG/90 (20%), Assists/90 (15%), xA/90 (10%),
      Shots/90 (10%), Progressive Carries/90 (8%), Key Passes/90 (7%)<br>
    • <b>Meia (MF)</b>: Assists/90 (20%), Key Passes/90 (18%), Prog. Passes/90 (18%),
      Goals/90 (15%), xG/90 (10%), Tackles/90 (10%), Interceptions/90 (9%)<br>
    • <b>Defensor (DF)</b>: Tackles/90 (22%), Interceptions/90 (22%), Aerial Duels/90 (18%),
      Blocks/90 (14%), Prog. Passes/90 (14%), Goals/90 (5%), Assists/90 (5%)<br>
    • <b>Goleiro (GK)</b>: Prog. Passes/90 (35%), Tackles/90 (30%),
      Interceptions/90 (25%), Aerial Duels/90 (10%)

    <br><br><b>Interpretação:</b><br>
    • 80–100: Elite mundial<br>
    • 65–79: Muito acima da média<br>
    • 50–64: Acima da média<br>
    • 35–49: Na média ou abaixo<br>
    • 0–34: Fraco para o nível da Premier League
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class='info-box'>
    <h3 style='color:#3fb950;margin-top:0;'>Team Dominance Index (TDI)</h3>

    O <b>TDI</b> é um índice de 0 a 100 que quantifica o domínio geral de um time
    em uma temporada, combinando quatro dimensões:

    <br><br><b>Componentes (peso total = 100%):</b><br>
    • <b>Ataque (35%)</b>: Gols marcados (50%) + xG For (50%) — capacidade ofensiva real<br>
    • <b>Defesa (35%)</b>: Gols sofridos invertido (40%) + xG Against invertido (35%) +
      Clean Sheets (25%) — solidez defensiva<br>
    • <b>Controle (15%)</b>: Posse de bola — domínio no meio de campo<br>
    • <b>Resultados (15%)</b>: Pontos (60%) + Aproveitamento % (40%) — eficiência em resultados

    <br><br><b>Normalização:</b><br>
    Cada componente é normalizado por <i>percentile rank</i> dentro da mesma temporada,
    garantindo comparabilidade entre diferentes eras do futebol.

    <br><br><b>Interpretação:</b><br>
    • 75–100: Dominância absoluta (Manchester City 2017-18, Liverpool 2019-20)<br>
    • 60–74: Time de elite<br>
    • 45–59: Time competitivo<br>
    • 30–44: Time mediano<br>
    • 0–29: Time em dificuldade
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class='info-box'>
    <h3 style='color:#f59e0b;margin-top:0;'>Notas sobre os Dados</h3>

    Os dados utilizados neste dashboard são gerados sinteticamente com base em padrões
    estatísticos reais da Premier League (2014–2024). Jogadores em destaque possuem
    perfis de carreira historicamente embasados.

    <br><br>Para uso com dados reais, o sistema suporta substituição transparente dos
    arquivos CSV na pasta <code>data/</code>. Fontes recomendadas:
    <ul>
    <li><b>FBref.com</b> — estatísticas avançadas completas</li>
    <li><b>Kaggle</b> — datasets históricos da Premier League</li>
    <li><b>StatsBomb Open Data</b> — dados de eventos detalhados</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
