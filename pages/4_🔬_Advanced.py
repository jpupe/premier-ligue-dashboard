"""
Advanced Analytics Page — similar player finder, clustering, percentile analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

from src.data.loader import load_players
from src.metrics.scores import calculate_pps
from src.data.processor import compute_percentiles
from src.visualizations.styles import inject_css, render_logo, section_header
from src.visualizations.charts import (
    radar_chart, bar_chart, scatter_plot, cluster_scatter, time_series
)
from src.utils.constants import (
    SEASONS, POSITIONS, POSITION_FULL,
    RADAR_METRICS_FW, RADAR_METRICS_MF, RADAR_METRICS_DF,
    RADAR_LABELS, CLUSTER_NAMES_FW, CLUSTER_NAMES_MF, CLUSTER_NAMES_DF,
)

st.set_page_config(page_title="Advanced · PL Analytics", page_icon="🔬", layout="wide")
inject_css()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
players_df = load_players()
players_pps = calculate_pps(players_df)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
render_logo()
st.sidebar.markdown("### Configurações")
adv_season = st.sidebar.selectbox("Temporada base", SEASONS,
                                  index=len(SEASONS) - 1, key="adv_season")
adv_position = st.sidebar.selectbox(
    "Posição de análise", POSITIONS,
    format_func=lambda p: POSITION_FULL[p],
    key="adv_pos"
)
min_min_adv = st.sidebar.slider("Mínimo de minutos", 0, 3420, 900, 90, key="adv_min")

# ---------------------------------------------------------------------------
# Feature sets by position
# ---------------------------------------------------------------------------
CLUSTER_FEATURES = {
    "FW": ["goals_per90", "assists_per90", "xG_per90", "shots_per90",
           "progressive_carries_per90", "key_passes_per90"],
    "MF": ["assists_per90", "key_passes_per90", "progressive_passes_per90",
           "goals_per90", "tackles_per90", "interceptions_per90"],
    "DF": ["tackles_per90", "interceptions_per90", "progressive_passes_per90",
           "aerial_duels_won_per90", "blocks_per90", "goals_per90"],
    "GK": ["progressive_passes_per90", "tackles_per90",
           "interceptions_per90", "aerial_duels_won_per90"],
}
CLUSTER_NAMES = {"FW": CLUSTER_NAMES_FW, "MF": CLUSTER_NAMES_MF, "DF": CLUSTER_NAMES_DF}

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<h1 style='font-size:2rem;font-weight:900;color:#e6edf3;margin-bottom:4px;'>
    🔬 Analytics Avançado
</h1>
<p style='color:#8b949e;margin-top:0;'>
    Scouting de jogadores similares, clustering de perfis e análise de percentis
</p>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Jogadores Similares", "Clustering de Perfis", "Análise de Percentis"])

# ---------------------------------------------------------------------------
# Prepare position pool
# ---------------------------------------------------------------------------
pool = players_pps[
    (players_pps["position"] == adv_position) &
    (players_pps["season"] == adv_season) &
    (players_pps["minutes"] >= min_min_adv)
].copy().dropna(subset=CLUSTER_FEATURES.get(adv_position, []), how="any")


# ============================================================
# TAB 1 — Similar player finder
# ============================================================
with tab1:
    st.markdown(section_header("Encontrar Jogadores Similares"), unsafe_allow_html=True)
    st.markdown("""
    <div class='info-box'>
    Encontra jogadores com o perfil estatístico mais similar usando
    <b>Cosine Similarity</b> sobre métricas normalizadas por 90 minutos.
    Apenas jogadores da mesma posição e temporada são comparados.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    all_names = sorted(players_pps["player_name"].unique().tolist())
    featured_names = sorted(players_pps[players_pps["is_featured"]]["player_name"].unique().tolist())

    ref_player = st.selectbox(
        "Jogador de referência",
        featured_names + [n for n in all_names if n not in featured_names],
        key="similar_ref"
    )
    n_similar = st.slider("Número de jogadores similares", 3, 15, 8, key="n_similar")

    features = CLUSTER_FEATURES.get(adv_position, CLUSTER_FEATURES["MF"])
    available_features = [f for f in features if f in pool.columns]

    if len(pool) < 3:
        st.warning(f"Poucos jogadores disponíveis para {POSITION_FULL[adv_position]} em {adv_season}. "
                   "Reduza o mínimo de minutos ou mude a temporada.")
    else:
        ref_row = pool[pool["player_name"] == ref_player]
        if ref_row.empty:
            st.info(f"{ref_player} não tem dados suficientes em {adv_season} "
                    f"como {POSITION_FULL[adv_position]} com ≥{min_min_adv} min. "
                    "Tente reduzir o mínimo de minutos.")
        else:
            X = pool[available_features].fillna(0).values
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            ref_idx = pool.index.get_loc(ref_row.index[0])
            sims = cosine_similarity([X_scaled[ref_idx]], X_scaled)[0]
            pool_copy = pool.copy().reset_index(drop=True)
            pool_copy["similarity"] = sims
            pool_copy = pool_copy[pool_copy["player_name"] != ref_player]
            similar = pool_copy.nlargest(n_similar, "similarity")

            # Show similarity table
            st.markdown(f"**Jogadores mais similares a {ref_player} ({POSITION_FULL[adv_position]}, {adv_season})**")
            display_feats = ["player_name", "team", "similarity"] + \
                            [f.replace("_per90", "/90") if "_per90" in f else f for f in available_features[:4]]
            show_df = similar[["player_name", "team", "similarity"] + available_features[:4]].copy()
            show_df["similarity"] = (show_df["similarity"] * 100).round(1)
            st.dataframe(
                show_df.rename(columns={
                    "player_name": "Jogador", "team": "Time", "similarity": "Sim.%",
                })
                .style.format({"Sim.%": "{:.1f}%"})
                .background_gradient(cmap="Purples", subset=["Sim.%"]),
                use_container_width=True,
            )

            # Radar: reference + top 2 similar
            st.markdown(section_header("Radar Comparativo"), unsafe_allow_html=True)
            radar_map = {"FW": RADAR_METRICS_FW, "MF": RADAR_METRICS_MF,
                         "DF": RADAR_METRICS_DF}
            radar_metrics = radar_map.get(adv_position, RADAR_METRICS_FW)
            radar_labels = [RADAR_LABELS.get(m, m) for m in radar_metrics]

            radar_players = [ref_player] + similar["player_name"].head(3).tolist()
            radar_data = []
            for name in radar_players:
                p_row = pool[pool["player_name"] == name]
                if p_row.empty:
                    continue
                pvals = []
                for m in radar_metrics:
                    if m not in pool.columns:
                        pvals.append(50.0)
                        continue
                    val = p_row.iloc[0].get(m, 0)
                    pool_vals = pool[m].dropna()
                    pct = float(np.sum(pool_vals <= val) / max(1, len(pool_vals)) * 100)
                    pvals.append(round(pct, 1))
                radar_data.append({"name": name, "values": pvals})

            if radar_data:
                fig_r = radar_chart(radar_data, radar_metrics, radar_labels,
                                    title=f"Perfil Comparativo · {POSITION_FULL[adv_position]}")
                st.plotly_chart(fig_r, use_container_width=True)


# ============================================================
# TAB 2 — Clustering
# ============================================================
with tab2:
    st.markdown(section_header(f"Clustering — {POSITION_FULL[adv_position]}s · {adv_season}"),
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class='info-box'>
    Agrupa os {POSITION_FULL[adv_position].lower()}s em 5 perfis distintos usando
    <b>K-Means</b> com <b>PCA</b> para visualização em 2D. Os rótulos dos clusters
    são derivados das características médias de cada grupo.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    features = CLUSTER_FEATURES.get(adv_position, CLUSTER_FEATURES["MF"])
    available_features = [f for f in features if f in pool.columns]

    if len(pool) < 10:
        st.warning("Dados insuficientes para clustering. Ajuste os filtros.")
    else:
        X = pool[available_features].fillna(0).values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        n_clusters = min(5, len(pool) - 1)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)

        pca = PCA(n_components=2, random_state=42)
        pcs = pca.fit_transform(X_scaled)

        cluster_df = pool[["player_name", "team", "pps"] + available_features[:3]].copy()
        cluster_df = cluster_df.reset_index(drop=True)
        cluster_df["cluster"] = clusters
        cluster_df["pc1"] = pcs[:, 0]
        cluster_df["pc2"] = pcs[:, 1]

        names_map = CLUSTER_NAMES.get(adv_position, {})
        cluster_df["cluster_name"] = cluster_df["cluster"].map(
            lambda c: names_map.get(c, f"Cluster {c}")
        )

        # PCA explained variance
        var_exp = pca.explained_variance_ratio_
        st.info(f"PCA explica {var_exp[0]*100:.1f}% + {var_exp[1]*100:.1f}% = "
                f"{sum(var_exp)*100:.1f}% da variância total nas {len(available_features)} métricas.")

        fig_cluster = cluster_scatter(cluster_df, title=f"Clusters de {POSITION_FULL[adv_position]}s")
        st.plotly_chart(fig_cluster, use_container_width=True)

        # Cluster stats
        st.markdown(section_header("Perfil Médio por Cluster"), unsafe_allow_html=True)
        cluster_stats = (
            cluster_df.groupby("cluster_name")[available_features[:4] + ["pps"]]
            .mean()
            .round(2)
        )
        st.dataframe(cluster_stats.style.background_gradient(cmap="Purples"),
                     use_container_width=True)

        # Players per cluster
        st.markdown(section_header("Jogadores por Cluster"), unsafe_allow_html=True)
        cluster_filter = st.selectbox(
            "Ver cluster",
            sorted(cluster_df["cluster_name"].unique()),
            key="cluster_filter"
        )
        cluster_players = (
            cluster_df[cluster_df["cluster_name"] == cluster_filter]
            .sort_values("pps", ascending=False)
            [["player_name", "team"] + available_features[:3] + ["pps"]]
        )
        st.dataframe(
            cluster_players.style.format(precision=2)
              .background_gradient(cmap="Purples", subset=["pps"]),
            use_container_width=True,
        )

        # Feature importance per cluster (avg normalized)
        st.markdown(section_header("Radar Médio dos Clusters"), unsafe_allow_html=True)
        cluster_radar_data = []
        for cname in sorted(cluster_df["cluster_name"].unique()):
            sub = cluster_df[cluster_df["cluster_name"] == cname]
            vals = []
            for f in available_features:
                all_vals = cluster_df[f].dropna()
                cluster_mean = sub[f].mean()
                pct = float(np.sum(all_vals <= cluster_mean) / max(1, len(all_vals)) * 100)
                vals.append(round(pct, 1))
            cluster_radar_data.append({"name": cname, "values": vals})

        labels = [RADAR_LABELS.get(f, f) for f in available_features]
        fig_cr = radar_chart(cluster_radar_data, available_features, labels,
                             title=f"Perfil Médio dos Clusters · {POSITION_FULL[adv_position]}")
        st.plotly_chart(fig_cr, use_container_width=True)


# ============================================================
# TAB 3 — Percentile analysis
# ============================================================
with tab3:
    st.markdown(section_header("Análise de Percentis"), unsafe_allow_html=True)

    pct_player = st.selectbox(
        "Selecione um jogador",
        sorted(players_pps[players_pps["is_featured"]]["player_name"].unique().tolist()) +
        sorted(players_pps[~players_pps["is_featured"]]["player_name"].unique().tolist()),
        key="pct_player"
    )
    pct_season = st.selectbox("Temporada", SEASONS, index=len(SEASONS) - 1, key="pct_season")

    pct_row = players_pps[
        (players_pps["player_name"] == pct_player) &
        (players_pps["season"] == pct_season)
    ]

    if pct_row.empty:
        st.warning(f"Nenhum dado para {pct_player} em {pct_season}.")
    else:
        row = pct_row.iloc[0]
        pos = row["position"]

        radar_map = {"FW": RADAR_METRICS_FW, "MF": RADAR_METRICS_MF,
                     "DF": RADAR_METRICS_DF}
        metrics = radar_map.get(pos, RADAR_METRICS_FW)
        position_pool = players_pps[
            (players_pps["position"] == pos) &
            (players_pps["season"] == pct_season) &
            (players_pps["minutes"] >= 450)
        ]

        # Compute percentiles
        pct_vals = {}
        raw_vals = {}
        for m in metrics:
            if m not in position_pool.columns:
                continue
            val = row.get(m, 0)
            raw_vals[m] = round(float(val), 2) if not pd.isna(val) else 0
            pool_s = position_pool[m].dropna()
            pct_vals[m] = round(float(np.sum(pool_s <= val) / max(1, len(pool_s)) * 100), 1)

        # Display percentile bars
        st.markdown(f"""
        <div style='font-size:1.1rem;font-weight:700;color:#e6edf3;margin-bottom:12px;'>
            {pct_player} · {POSITION_FULL.get(pos, pos)} · {pct_season}
        </div>
        """, unsafe_allow_html=True)

        for m, pct in pct_vals.items():
            label = RADAR_LABELS.get(m, m)
            raw = raw_vals.get(m, 0)
            bar_color = (
                "#3fb950" if pct >= 80 else
                "#6e40c9" if pct >= 60 else
                "#d29922" if pct >= 40 else "#f85149"
            )
            st.markdown(f"""
            <div style='margin-bottom:10px;'>
                <div style='display:flex;justify-content:space-between;
                            font-size:0.82rem;color:#e6edf3;margin-bottom:3px;'>
                    <span>{label}</span>
                    <span style='color:{bar_color};font-weight:700;'>{pct:.0f}th pct
                    <span style='color:#8b949e;font-weight:400;'>(val: {raw})</span></span>
                </div>
                <div style='background:#21262d;border-radius:4px;height:8px;overflow:hidden;'>
                    <div style='width:{pct}%;height:100%;background:{bar_color};
                                border-radius:4px;transition:width 0.3s;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Radar
        st.markdown("<br>", unsafe_allow_html=True)
        fig_pct_radar = radar_chart(
            [{"name": pct_player, "values": list(pct_vals.values())}],
            list(pct_vals.keys()),
            [RADAR_LABELS.get(m, m) for m in pct_vals.keys()],
            title=f"Percentis · {pct_player} · {pct_season}",
        )
        st.plotly_chart(fig_pct_radar, use_container_width=True)

        # Career percentile evolution
        st.markdown(section_header("Evolução de Percentis por Temporada"), unsafe_allow_html=True)
        career_pcts = []
        for s in SEASONS:
            s_row = players_pps[
                (players_pps["player_name"] == pct_player) &
                (players_pps["season"] == s)
            ]
            if s_row.empty:
                continue
            s_pos = s_row.iloc[0]["position"]
            s_pool = players_pps[
                (players_pps["position"] == s_pos) &
                (players_pps["season"] == s) &
                (players_pps["minutes"] >= 450)
            ]
            row_data = {"season": s}
            for m in metrics[:3]:
                if m not in s_pool.columns:
                    continue
                val = s_row.iloc[0].get(m, 0)
                pool_s = s_pool[m].dropna()
                row_data[RADAR_LABELS.get(m, m)] = round(
                    float(np.sum(pool_s <= val) / max(1, len(pool_s)) * 100), 1
                )
            career_pcts.append(row_data)

        if len(career_pcts) > 1:
            cdf = pd.DataFrame(career_pcts)
            metric_cols = [c for c in cdf.columns if c != "season"]
            fig_evo = time_series(
                cdf, x="season", y=metric_cols,
                title=f"Percentis por Temporada · {pct_player}",
                y_label="Percentil",
            )
            st.plotly_chart(fig_evo, use_container_width=True)
