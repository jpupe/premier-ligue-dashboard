SEASONS = [
    "2014-15", "2015-16", "2016-17", "2017-18", "2018-19",
    "2019-20", "2020-21", "2021-22", "2022-23", "2023-24"
]

ALL_TEAMS = [
    "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
    "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
    "Leeds United", "Leicester City", "Liverpool", "Luton Town",
    "Manchester City", "Manchester United", "Newcastle United", "Norwich City",
    "Nottingham Forest", "Sheffield United", "Southampton", "Stoke City",
    "Swansea City", "Tottenham", "Watford", "West Bromwich Albion",
    "West Ham United", "Wolverhampton", "Sunderland", "Hull City",
    "Middlesbrough", "Cardiff City", "Queens Park Rangers",
]

SEASON_TEAMS = {
    "2014-15": ["Arsenal","Aston Villa","Burnley","Chelsea","Crystal Palace","Everton",
                "Hull City","Leicester City","Liverpool","Manchester City","Manchester United",
                "Newcastle United","Queens Park Rangers","Southampton","Stoke City","Sunderland",
                "Swansea City","Tottenham","West Bromwich Albion","West Ham United"],
    "2015-16": ["Arsenal","Aston Villa","Bournemouth","Chelsea","Crystal Palace","Everton",
                "Leicester City","Liverpool","Manchester City","Manchester United",
                "Newcastle United","Norwich City","Southampton","Stoke City","Sunderland",
                "Swansea City","Tottenham","Watford","West Bromwich Albion","West Ham United"],
    "2016-17": ["Arsenal","Bournemouth","Burnley","Chelsea","Crystal Palace","Everton",
                "Hull City","Leicester City","Liverpool","Manchester City","Manchester United",
                "Middlesbrough","Southampton","Stoke City","Sunderland","Swansea City",
                "Tottenham","Watford","West Bromwich Albion","West Ham United"],
    "2017-18": ["Arsenal","Bournemouth","Brighton","Burnley","Chelsea","Crystal Palace",
                "Everton","Huddersfield","Leicester City","Liverpool","Manchester City",
                "Manchester United","Newcastle United","Southampton","Stoke City","Swansea City",
                "Tottenham","Watford","West Bromwich Albion","West Ham United"],
    "2018-19": ["Arsenal","Bournemouth","Brighton","Burnley","Cardiff City","Chelsea",
                "Crystal Palace","Everton","Fulham","Huddersfield","Leicester City","Liverpool",
                "Manchester City","Manchester United","Newcastle United","Southampton",
                "Tottenham","Watford","West Ham United","Wolverhampton"],
    "2019-20": ["Arsenal","Aston Villa","Bournemouth","Brighton","Burnley","Chelsea",
                "Crystal Palace","Everton","Leicester City","Liverpool","Manchester City",
                "Manchester United","Newcastle United","Norwich City","Sheffield United",
                "Southampton","Tottenham","Watford","West Ham United","Wolverhampton"],
    "2020-21": ["Arsenal","Aston Villa","Brighton","Burnley","Chelsea","Crystal Palace",
                "Everton","Fulham","Leeds United","Leicester City","Liverpool","Manchester City",
                "Manchester United","Newcastle United","Sheffield United","Southampton",
                "Tottenham","West Bromwich Albion","West Ham United","Wolverhampton"],
    "2021-22": ["Arsenal","Aston Villa","Brentford","Brighton","Burnley","Chelsea",
                "Crystal Palace","Everton","Leeds United","Leicester City","Liverpool",
                "Manchester City","Manchester United","Newcastle United","Norwich City",
                "Southampton","Tottenham","Watford","West Ham United","Wolverhampton"],
    "2022-23": ["Arsenal","Aston Villa","Bournemouth","Brentford","Brighton","Chelsea",
                "Crystal Palace","Everton","Fulham","Leeds United","Leicester City","Liverpool",
                "Manchester City","Manchester United","Newcastle United","Nottingham Forest",
                "Southampton","Tottenham","West Ham United","Wolverhampton"],
    "2023-24": ["Arsenal","Aston Villa","Bournemouth","Brentford","Brighton","Burnley",
                "Chelsea","Crystal Palace","Everton","Fulham","Liverpool","Luton Town",
                "Manchester City","Manchester United","Newcastle United","Nottingham Forest",
                "Sheffield United","Tottenham","West Ham United","Wolverhampton"],
}

POSITIONS = ["GK", "DF", "MF", "FW"]
POSITION_FULL = {"GK": "Goalkeeper", "DF": "Defender", "MF": "Midfielder", "FW": "Forward"}

TEAM_COLORS = {
    "Arsenal": "#EF0107",
    "Aston Villa": "#95BFE5",
    "Bournemouth": "#DA291C",
    "Brentford": "#D20000",
    "Brighton": "#0057B8",
    "Burnley": "#6C1D45",
    "Cardiff City": "#0070B5",
    "Chelsea": "#034694",
    "Crystal Palace": "#1B458F",
    "Everton": "#003399",
    "Fulham": "#CC0000",
    "Huddersfield": "#0E63AD",
    "Hull City": "#F5A12D",
    "Leeds United": "#FFCD00",
    "Leicester City": "#003090",
    "Liverpool": "#C8102E",
    "Luton Town": "#F78F1E",
    "Manchester City": "#6CABDD",
    "Manchester United": "#DA291C",
    "Middlesbrough": "#D71920",
    "Newcastle United": "#241F20",
    "Norwich City": "#FFF200",
    "Nottingham Forest": "#DD0000",
    "Queens Park Rangers": "#1D5BA4",
    "Sheffield United": "#EE2737",
    "Southampton": "#D71920",
    "Stoke City": "#E03A3E",
    "Sunderland": "#EB172B",
    "Swansea City": "#121212",
    "Tottenham": "#132257",
    "Watford": "#FBEE23",
    "West Bromwich Albion": "#122F67",
    "West Ham United": "#7A263A",
    "Wolverhampton": "#FDB913",
}

DEFAULT_TEAM_COLOR = "#6e40c9"

PLAYER_METRICS = [
    "goals", "assists", "xG", "xA",
    "goals_per90", "assists_per90",
    "minutes", "progressive_passes",
    "progressive_carries", "tackles", "interceptions",
    "goal_contributions", "shots", "key_passes",
]

PLAYER_METRIC_LABELS = {
    "goals": "Goals",
    "assists": "Assists",
    "xG": "xG",
    "xA": "xA",
    "goals_per90": "Goals/90",
    "assists_per90": "Assists/90",
    "minutes": "Minutes",
    "progressive_passes": "Prog. Passes",
    "progressive_carries": "Prog. Carries",
    "tackles": "Tackles",
    "interceptions": "Interceptions",
    "goal_contributions": "G+A",
    "shots": "Shots",
    "key_passes": "Key Passes",
}

TEAM_METRICS = [
    "points", "goal_difference", "win_percentage",
    "goals_for", "goals_against", "clean_sheets",
    "possession", "xG_for", "xG_against",
]

TEAM_METRIC_LABELS = {
    "points": "Points",
    "goal_difference": "Goal Diff.",
    "win_percentage": "Win %",
    "goals_for": "Goals For",
    "goals_against": "Goals Against",
    "clean_sheets": "Clean Sheets",
    "possession": "Possession %",
    "xG_for": "xG For",
    "xG_against": "xG Against",
}

RADAR_METRICS_FW = ["goals_per90", "assists_per90", "xG_per90", "shots_per90",
                     "progressive_carries_per90", "key_passes_per90"]
RADAR_METRICS_MF = ["assists_per90", "key_passes_per90", "progressive_passes_per90",
                     "goals_per90", "tackles_per90", "interceptions_per90"]
RADAR_METRICS_DF = ["tackles_per90", "interceptions_per90", "progressive_passes_per90",
                     "aerial_duels_won_per90", "blocks_per90", "goals_per90"]
RADAR_METRICS_GK = ["clean_sheets", "saves_pct", "goals_prevented", "minutes", "goals", "assists"]

RADAR_LABELS = {
    "goals_per90": "Goals/90", "assists_per90": "Assists/90",
    "xG_per90": "xG/90", "shots_per90": "Shots/90",
    "progressive_carries_per90": "Carries/90", "key_passes_per90": "KeyPass/90",
    "progressive_passes_per90": "ProgPass/90", "tackles_per90": "Tackles/90",
    "interceptions_per90": "Intercept/90", "aerial_duels_won_per90": "Aerials/90",
    "blocks_per90": "Blocks/90", "clean_sheets": "Clean Sheets",
    "saves_pct": "Save %", "goals_prevented": "Goals Prev.",
    "minutes": "Minutes", "goals": "Goals", "assists": "Assists",
}

CLUSTER_NAMES_FW = {0: "Target Man", 1: "Poacher", 2: "Complete FW", 3: "Wide Forward", 4: "False 9"}
CLUSTER_NAMES_MF = {0: "Box-to-Box", 1: "Playmaker", 2: "Defensive Mid", 3: "Attacking Mid", 4: "Wide Mid"}
CLUSTER_NAMES_DF = {0: "Ball-Playing CB", 1: "Aerial CB", 2: "Attacking FB", 3: "Defensive FB", 4: "Sweeper"}

PLOTLY_TEMPLATE = "plotly_dark"

ACCENT_COLOR = "#6e40c9"
ACCENT_LIGHT = "#8b5cf6"
SUCCESS_COLOR = "#3fb950"
WARNING_COLOR = "#d29922"
ERROR_COLOR = "#f85149"
