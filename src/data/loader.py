"""
Data loading layer with Streamlit caching and DuckDB for efficient querying.
"""

import streamlit as st
import pandas as pd
import duckdb

from src.data.generator import generate_players_data, generate_teams_data
from src.utils.helpers import build_per90_columns


@st.cache_data(show_spinner="Carregando dados dos jogadores...")
def load_players() -> pd.DataFrame:
    df = generate_players_data()
    df = build_per90_columns(df)
    return df


@st.cache_data(show_spinner="Carregando dados dos times...")
def load_teams() -> pd.DataFrame:
    return generate_teams_data()


@st.cache_resource
def get_duckdb_connection(players_df: pd.DataFrame, teams_df: pd.DataFrame) -> duckdb.DuckDBPyConnection:
    """Create an in-memory DuckDB connection with registered tables."""
    conn = duckdb.connect(database=":memory:")
    conn.register("players", players_df)
    conn.register("teams", teams_df)
    return conn


def query_players(conn: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    return conn.execute(sql).df()


def query_teams(conn: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    return conn.execute(sql).df()


def get_seasons(df: pd.DataFrame) -> list[str]:
    return sorted(df["season"].unique().tolist())


def get_teams_list(df: pd.DataFrame, season: str | None = None) -> list[str]:
    if season:
        return sorted(df[df["season"] == season]["team"].unique().tolist())
    return sorted(df["team"].unique().tolist())


def get_player_names(df: pd.DataFrame) -> list[str]:
    featured = df[df["is_featured"]]["player_name"].unique().tolist()
    others = df[~df["is_featured"]]["player_name"].unique().tolist()
    return sorted(featured) + sorted(others)
