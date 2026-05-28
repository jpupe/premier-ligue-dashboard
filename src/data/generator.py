"""
Synthetic Premier League data generator.
Produces realistic player and team statistics for seasons 2014-15 through 2023-24.
Featured players use historically grounded stat profiles; squad players are generated
with position-appropriate distributions.
"""

import numpy as np
import pandas as pd
from src.utils.constants import SEASONS, SEASON_TEAMS

RNG = np.random.default_rng(42)

# ---------------------------------------------------------------------------
# Featured players: (name, position, nationality)
# Each season entry: (season, team, age, mp, ms, min, g, a, xG, xA,
#                     shots, sot, kp, pp, pc, tk, int_, blk, aw, yc, rc)
# ---------------------------------------------------------------------------
FEATURED_PLAYERS = {
    # --- FORWARDS ---
    "Mohamed Salah": {
        "position": "FW", "nationality": "Egyptian",
        "seasons": {
            "2017-18": ("Liverpool",  25, 36, 34, 3050, 32, 12, 25.7, 10.2, 147, 72, 68, 110, 85, 26, 18, 8, 22, 0, 0),
            "2018-19": ("Liverpool",  26, 38, 36, 3168, 22,  8, 20.3,  8.6, 131, 58, 55,  98, 76, 24, 14, 6, 20, 2, 0),
            "2019-20": ("Liverpool",  27, 34, 30, 2758, 19, 10, 18.2,  9.1, 120, 55, 57, 102, 80, 22, 16, 5, 18, 1, 0),
            "2020-21": ("Liverpool",  28, 37, 36, 3122, 22,  5, 21.0,  5.8, 134, 65, 60, 106, 82, 20, 13, 4, 19, 0, 0),
            "2021-22": ("Liverpool",  29, 35, 33, 2923, 23, 13, 22.4, 11.8, 128, 64, 70, 112, 90, 22, 15, 5, 21, 2, 0),
            "2022-23": ("Liverpool",  30, 32, 30, 2612, 19, 12, 18.9, 10.4, 118, 57, 65, 105, 80, 19, 12, 4, 18, 1, 0),
            "2023-24": ("Liverpool",  31, 33, 31, 2750, 18, 11, 17.6,  9.8, 115, 54, 62, 101, 78, 18, 11, 3, 17, 0, 0),
        },
    },
    "Harry Kane": {
        "position": "FW", "nationality": "English",
        "seasons": {
            "2014-15": ("Tottenham", 21, 34, 24, 2140, 21,  6, 17.8,  5.2, 110, 52, 38,  55, 45, 18, 10, 3, 14, 1, 0),
            "2015-16": ("Tottenham", 22, 38, 37, 3291, 25,  5, 22.4,  4.9, 132, 63, 42,  70, 52, 20,  8, 3, 16, 2, 0),
            "2016-17": ("Tottenham", 23, 30, 29, 2544, 29,  8, 24.5,  7.1, 138, 68, 48,  78, 58, 16,  7, 2, 18, 1, 0),
            "2017-18": ("Tottenham", 24, 37, 35, 3070, 30,  4, 27.1,  4.6, 148, 73, 52,  88, 65, 18,  9, 4, 22, 3, 0),
            "2018-19": ("Tottenham", 25, 28, 27, 2357, 17,  3, 14.2,  2.9,  91, 45, 38,  65, 50, 12,  6, 2, 14, 1, 0),
            "2019-20": ("Tottenham", 26, 29, 26, 2293, 18,  2, 15.9,  2.4,  99, 50, 40,  68, 55, 14,  7, 3, 16, 2, 0),
            "2020-21": ("Tottenham", 27, 35, 35, 3048, 23, 14, 19.8, 13.1, 128, 64, 66,  98, 72, 18,  8, 3, 20, 1, 0),
            "2021-22": ("Tottenham", 28, 34, 32, 2764, 17,  9, 15.4,  8.7, 108, 53, 56,  85, 62, 16,  7, 2, 18, 2, 0),
            "2022-23": ("Tottenham", 29, 38, 37, 3235, 30,  3, 28.1,  3.5, 151, 75, 55,  95, 70, 18,  8, 3, 24, 2, 0),
        },
    },
    "Erling Haaland": {
        "position": "FW", "nationality": "Norwegian",
        "seasons": {
            "2022-23": ("Manchester City", 22, 35, 35, 2985, 36,  8, 33.8,  8.4, 150, 80, 50,  68, 60, 12,  6, 2, 28, 2, 0),
            "2023-24": ("Manchester City", 23, 31, 29, 2568, 27,  5, 25.1,  5.6, 130, 68, 42,  62, 55, 10,  5, 2, 24, 1, 0),
        },
    },
    "Son Heung-min": {
        "position": "FW", "nationality": "South Korean",
        "seasons": {
            "2015-16": ("Tottenham", 23, 28, 18, 1650,  4,  6,  4.2,  5.8,  65, 32, 38,  72, 60, 28, 12, 5, 10, 1, 0),
            "2016-17": ("Tottenham", 24, 34, 24, 2240, 14, 10, 12.1,  9.4,  96, 48, 55,  88, 75, 32, 14, 6, 14, 2, 0),
            "2017-18": ("Tottenham", 25, 37, 28, 2548, 12, 10, 10.8,  9.8,  98, 50, 58,  92, 80, 30, 12, 5, 12, 1, 0),
            "2018-19": ("Tottenham", 26, 31, 23, 2064, 12, 10, 10.5,  9.2,  92, 46, 55,  88, 78, 28, 10, 4, 10, 0, 0),
            "2019-20": ("Tottenham", 27, 30, 25, 2224, 11, 11, 10.2, 10.5,  88, 44, 56,  90, 82, 25,  9, 3,  9, 1, 0),
            "2020-21": ("Tottenham", 28, 37, 33, 2884, 17, 10, 14.8,  9.9, 105, 54, 60,  95, 85, 28, 11, 4, 11, 2, 0),
            "2021-22": ("Tottenham", 29, 35, 34, 2981, 23,  8, 20.1,  8.2, 120, 62, 58,  98, 88, 26,  9, 4, 12, 1, 0),
            "2022-23": ("Tottenham", 30, 33, 27, 2380, 10,  9,  9.5,  8.9,  85, 42, 52,  88, 78, 22,  8, 3, 10, 1, 0),
            "2023-24": ("Tottenham", 31, 35, 32, 2802, 17, 10, 14.5,  9.4, 105, 54, 58,  96, 85, 25,  9, 3, 11, 0, 0),
        },
    },
    "Jamie Vardy": {
        "position": "FW", "nationality": "English",
        "seasons": {
            "2014-15": ("Leicester City", 27, 34, 22, 2006,  5,  8,  5.8,  7.2,  62, 28, 35,  45, 35, 32, 14, 4,  8, 4, 0),
            "2015-16": ("Leicester City", 28, 36, 35, 3031, 24,  5, 22.8,  4.9, 118, 58, 38,  55, 42, 28, 10, 3, 10, 6, 0),
            "2016-17": ("Leicester City", 29, 35, 27, 2412, 13,  9, 14.2,  8.5,  88, 44, 38,  58, 45, 26,  9, 3,  9, 3, 0),
            "2017-18": ("Leicester City", 30, 37, 33, 2864, 20,  5, 18.5,  4.7, 102, 52, 40,  65, 50, 28, 10, 4, 12, 4, 0),
            "2018-19": ("Leicester City", 31, 32, 28, 2481, 18,  4, 16.9,  4.2,  95, 48, 38,  60, 48, 24,  8, 3, 11, 3, 0),
            "2019-20": ("Leicester City", 32, 35, 32, 2777, 23,  6, 21.4,  5.9, 112, 58, 42,  68, 52, 22,  8, 3, 12, 5, 0),
            "2020-21": ("Leicester City", 33, 34, 28, 2488, 15,  3, 13.9,  2.7,  90, 45, 35,  55, 42, 18,  7, 2, 10, 4, 0),
            "2021-22": ("Leicester City", 34, 35, 29, 2566, 15,  3, 14.1,  2.8,  92, 46, 34,  54, 40, 16,  6, 2, 10, 3, 0),
            "2022-23": ("Leicester City", 35, 24, 15, 1356,  6,  2,  5.8,  1.9,  55, 28, 22,  38, 30, 12,  5, 1,  8, 2, 0),
            "2023-24": ("Leicester City", 36, 18, 10,  892,  4,  1,  3.8,  1.2,  38, 19, 14,  25, 20,  8,  4, 1,  6, 1, 0),
        },
    },
    "Marcus Rashford": {
        "position": "FW", "nationality": "English",
        "seasons": {
            "2016-17": ("Manchester United", 18, 32, 11, 1214,  5,  7,  4.8,  6.5,  52, 24, 40,  65, 55, 22, 10, 3,  5, 2, 0),
            "2017-18": ("Manchester United", 19, 35, 20, 1824,  7,  7,  6.5,  6.8,  68, 32, 48,  78, 68, 24, 10, 4,  6, 3, 0),
            "2018-19": ("Manchester United", 20, 33, 28, 2395, 10,  8,  9.4,  7.5,  82, 40, 52,  85, 75, 25, 11, 4,  7, 2, 0),
            "2019-20": ("Manchester United", 21, 31, 27, 2356, 17,  7, 15.8,  6.5,  98, 48, 55,  88, 80, 22, 10, 3,  7, 2, 0),
            "2020-21": ("Manchester United", 22, 37, 35, 3023, 21, 15, 18.2, 14.2, 110, 55, 64, 100, 92, 24, 12, 4,  8, 3, 0),
            "2021-22": ("Manchester United", 23, 25, 18, 1648,  5,  2,  4.8,  2.1,  65, 30, 38,  58, 52, 18,  8, 3,  5, 2, 0),
            "2022-23": ("Manchester United", 24, 35, 34, 2934, 30,  6, 26.5,  6.1, 138, 68, 55,  98, 88, 22, 10, 3,  9, 2, 0),
            "2023-24": ("Manchester United", 25, 30, 24, 2145, 11,  3, 10.2,  2.9,  95, 46, 40,  72, 65, 18,  8, 3,  7, 2, 0),
        },
    },
    "Gabriel Jesus": {
        "position": "FW", "nationality": "Brazilian",
        "seasons": {
            "2016-17": ("Manchester City", 19, 10,  4,  566,  7,  4,  6.4,  3.8,  42, 20, 28,  42, 38, 18,  8, 2,  6, 0, 0),
            "2017-18": ("Manchester City", 20, 29, 18, 1618, 13,  4, 11.5,  3.9,  75, 36, 38,  58, 52, 20,  9, 3,  9, 1, 0),
            "2018-19": ("Manchester City", 21, 29, 21, 1856, 11,  7, 10.2,  6.5,  72, 35, 42,  65, 58, 22, 10, 3,  8, 2, 0),
            "2019-20": ("Manchester City", 22, 28, 19, 1672, 14,  3, 12.5,  3.4,  78, 38, 38,  60, 55, 20,  9, 3,  9, 1, 0),
            "2020-21": ("Manchester City", 23, 24, 13, 1212,  9,  2,  8.2,  2.2,  58, 28, 32,  50, 45, 16,  7, 2,  7, 0, 0),
            "2021-22": ("Manchester City", 24, 26, 18, 1564, 11,  8,  9.5,  7.2,  68, 33, 40,  62, 56, 18,  8, 3,  8, 1, 0),
            "2022-23": ("Arsenal",         25, 30, 27, 2315, 11,  6, 10.5,  5.8,  75, 36, 45,  68, 62, 22, 10, 4,  9, 2, 0),
            "2023-24": ("Arsenal",         26, 22, 16, 1395,  5,  7,  5.2,  6.8,  52, 25, 35,  55, 50, 18,  8, 3,  6, 0, 0),
        },
    },
    "Bukayo Saka": {
        "position": "FW", "nationality": "English",
        "seasons": {
            "2019-20": ("Arsenal", 18, 26, 14, 1350,  1,  4,  1.5,  4.2,  38, 15, 42,  58, 55, 28, 12, 5,  5, 0, 0),
            "2020-21": ("Arsenal", 19, 32, 27, 2425,  5,  8,  5.2,  7.8,  72, 32, 55,  80, 78, 30, 13, 5,  6, 1, 0),
            "2021-22": ("Arsenal", 20, 38, 34, 2974, 11, 11, 10.2, 10.8,  95, 45, 65,  98, 90, 32, 14, 6,  7, 1, 0),
            "2022-23": ("Arsenal", 21, 38, 37, 3248, 14, 11, 13.5, 10.5, 105, 52, 72, 110, 98, 35, 15, 6,  8, 2, 0),
            "2023-24": ("Arsenal", 22, 35, 35, 2997, 16, 13, 14.8, 12.1, 112, 54, 75, 115, 102, 32, 14, 5,  8, 1, 0),
        },
    },
    # --- MIDFIELDERS ---
    "Kevin De Bruyne": {
        "position": "MF", "nationality": "Belgian",
        "seasons": {
            "2015-16": ("Manchester City", 24, 25, 23, 2050,  7, 16,  6.8, 13.9, 62, 28, 92, 155, 40, 38, 24, 8, 5, 2, 0),
            "2016-17": ("Manchester City", 25, 36, 34, 3065,  6, 18,  6.2, 16.4, 68, 32, 98, 165, 45, 35, 22, 7, 4, 2, 0),
            "2017-18": ("Manchester City", 26, 37, 37, 3246,  8, 16,  7.5, 15.2, 72, 34, 95, 168, 48, 32, 20, 6, 4, 3, 0),
            "2018-19": ("Manchester City", 27, 19, 17, 1490,  2, 11,  2.1,  9.8, 32, 14, 48,  85, 22, 25, 16, 5, 3, 0, 0),
            "2019-20": ("Manchester City", 28, 35, 32, 2832,  9, 21,  8.2, 19.5, 80, 36, 108, 175, 52, 30, 19, 6, 4, 1, 0),
            "2020-21": ("Manchester City", 29, 25, 22, 1956,  6, 12,  5.5, 10.8, 60, 28, 78, 138, 38, 28, 18, 5, 3, 1, 0),
            "2021-22": ("Manchester City", 30, 30, 28, 2514, 15,  8, 13.5,  7.5, 88, 42, 85, 148, 42, 32, 20, 6, 4, 2, 0),
            "2022-23": ("Manchester City", 31, 32, 30, 2674,  7, 16,  6.5, 15.2, 65, 30, 95, 158, 45, 30, 18, 5, 4, 1, 0),
            "2023-24": ("Manchester City", 32, 18, 16, 1405,  5, 10,  4.5,  9.2, 40, 18, 55,  95, 28, 20, 12, 4, 2, 0, 0),
        },
    },
    "Bruno Fernandes": {
        "position": "MF", "nationality": "Portuguese",
        "seasons": {
            "2019-20": ("Manchester United", 25, 14, 14, 1233,  8,  7,  7.5,  6.5, 52, 24, 58, 85, 28, 22, 14, 4, 3, 0, 0),
            "2020-21": ("Manchester United", 26, 37, 37, 3213, 18, 12, 15.8, 11.5, 110, 52, 92, 148, 42, 28, 18, 5, 4, 5, 0),
            "2021-22": ("Manchester United", 27, 35, 35, 3026, 10, 13,  9.5, 11.9,  95, 45, 85, 138, 40, 30, 20, 5, 3, 5, 0),
            "2022-23": ("Manchester United", 28, 35, 34, 2938,  8,  8,  7.5,  7.8,  80, 38, 72, 120, 38, 28, 18, 5, 3, 4, 0),
            "2023-24": ("Manchester United", 29, 35, 35, 3024, 15,  7, 13.5,  6.8,  98, 48, 80, 125, 42, 25, 16, 5, 3, 4, 0),
        },
    },
    "David Silva": {
        "position": "MF", "nationality": "Spanish",
        "seasons": {
            "2014-15": ("Manchester City", 28, 32, 30, 2680,  5, 11,  4.8, 10.5, 45, 20, 88, 148, 38, 35, 22, 7, 3, 1, 0),
            "2015-16": ("Manchester City", 29, 30, 28, 2444,  6, 10,  5.5,  9.8, 48, 22, 82, 140, 36, 32, 20, 6, 3, 1, 0),
            "2016-17": ("Manchester City", 30, 33, 31, 2756,  5, 11,  4.9, 10.2, 48, 22, 85, 145, 38, 30, 18, 6, 2, 2, 0),
            "2017-18": ("Manchester City", 31, 33, 30, 2655,  5, 15,  4.8, 13.9, 46, 20, 92, 155, 38, 28, 16, 5, 2, 2, 0),
            "2018-19": ("Manchester City", 32, 32, 28, 2492,  4, 12,  3.9, 11.2, 42, 18, 85, 145, 36, 26, 15, 5, 2, 1, 0),
            "2019-20": ("Manchester City", 33, 28, 24, 2168,  4, 11,  3.8, 10.5, 40, 18, 80, 135, 34, 24, 14, 5, 2, 0, 0),
        },
    },
    "Declan Rice": {
        "position": "MF", "nationality": "English",
        "seasons": {
            "2018-19": ("West Ham United", 20, 26, 24, 2148,  2,  2,  1.8,  1.9, 38, 15, 28, 95, 22, 58, 38, 12, 4, 2, 0),
            "2019-20": ("West Ham United", 21, 35, 34, 2978,  1,  1,  1.2,  1.2, 40, 16, 25, 102, 20, 68, 45, 14, 3, 3, 0),
            "2020-21": ("West Ham United", 22, 35, 35, 3150,  2,  3,  1.9,  2.5, 45, 18, 32, 108, 22, 72, 48, 15, 4, 4, 0),
            "2021-22": ("West Ham United", 23, 36, 35, 3090,  2,  3,  2.1,  2.8, 48, 20, 35, 110, 24, 78, 52, 16, 4, 3, 0),
            "2022-23": ("West Ham United", 24, 38, 38, 3329,  5,  8,  4.5,  7.8, 68, 28, 48, 120, 28, 82, 55, 18, 5, 3, 0),
            "2023-24": ("Arsenal",         25, 35, 35, 3058,  7,  8,  6.5,  7.5, 72, 32, 52, 130, 32, 78, 50, 16, 5, 2, 0),
        },
    },
    "Phil Foden": {
        "position": "MF", "nationality": "English",
        "seasons": {
            "2018-19": ("Manchester City", 18,  5,  0,  168,  1,  0,  0.9,  0.2, 12,  5, 10, 25,  8, 12,  8, 3, 2, 0, 0),
            "2019-20": ("Manchester City", 19, 22, 11, 1054,  8,  4,  7.2,  3.5, 52, 25, 35, 60, 18, 18, 12, 4, 3, 0, 0),
            "2020-21": ("Manchester City", 20, 28, 25, 2163, 16,  9, 14.2,  8.4, 88, 42, 52, 90, 25, 22, 14, 5, 4, 1, 0),
            "2021-22": ("Manchester City", 21, 28, 22, 1999,  9,  5,  8.5,  4.8, 72, 34, 42, 80, 22, 20, 12, 4, 3, 1, 0),
            "2022-23": ("Manchester City", 22, 35, 30, 2627, 11, 10, 10.2,  9.5, 85, 40, 58, 95, 28, 22, 14, 5, 4, 0, 0),
            "2023-24": ("Manchester City", 23, 35, 34, 2958, 19,  8, 17.5,  7.8, 108, 52, 62, 105, 32, 25, 16, 5, 4, 1, 0),
        },
    },
    # --- DEFENDERS ---
    "Trent Alexander-Arnold": {
        "position": "DF", "nationality": "English",
        "seasons": {
            "2017-18": ("Liverpool", 19, 28, 22, 2012,  1,  7,  1.2,  6.8, 28, 10, 68, 128, 42, 48, 28, 10, 5, 1, 0),
            "2018-19": ("Liverpool", 20, 38, 36, 3153,  1, 12,  1.4, 11.2, 32, 12, 78, 148, 52, 55, 32, 12, 5, 0, 0),
            "2019-20": ("Liverpool", 21, 38, 37, 3231,  4, 13,  3.2, 12.1, 38, 15, 85, 152, 55, 52, 30, 11, 4, 1, 0),
            "2020-21": ("Liverpool", 22, 29, 28, 2416,  2,  5,  1.8,  4.9, 30, 11, 62, 118, 40, 42, 24, 9, 3, 1, 0),
            "2021-22": ("Liverpool", 23, 32, 29, 2554,  2, 12,  1.8, 11.5, 35, 14, 80, 148, 52, 50, 28, 10, 4, 0, 0),
            "2022-23": ("Liverpool", 24, 32, 30, 2638,  3, 10,  2.5,  9.8, 38, 15, 75, 142, 50, 48, 26, 9, 4, 1, 0),
            "2023-24": ("Liverpool", 25, 30, 29, 2524,  3,  9,  2.8,  8.9, 35, 14, 72, 138, 48, 45, 25, 9, 3, 0, 0),
        },
    },
    "Virgil van Dijk": {
        "position": "DF", "nationality": "Dutch",
        "seasons": {
            "2017-18": ("Liverpool", 26, 13, 13, 1170,  2,  0,  1.8,  0.2, 18,  9, 8, 82, 12, 68, 42, 18, 9, 0, 0),
            "2018-19": ("Liverpool", 27, 38, 38, 3420,  4,  1,  3.5,  1.0, 28, 14, 12, 102, 15, 80, 50, 22, 12, 1, 0),
            "2019-20": ("Liverpool", 28, 38, 38, 3420,  5,  1,  4.2,  1.0, 32, 15, 12, 108, 15, 85, 52, 24, 12, 1, 0),
            "2020-21": ("Liverpool", 29,  5,  5,  450,  1,  0,  0.8,  0.1,  5,  2,  4, 35,  5, 25, 15,  6,  3, 0, 0),
            "2021-22": ("Liverpool", 30, 36, 36, 3240,  3,  2,  2.5,  1.5, 22, 11, 10, 95, 12, 78, 48, 20, 10, 2, 0),
            "2022-23": ("Liverpool", 31, 38, 38, 3420,  3,  1,  2.8,  1.0, 25, 12, 10, 98, 12, 80, 50, 22, 11, 2, 0),
            "2023-24": ("Liverpool", 32, 36, 36, 3240,  2,  1,  1.9,  0.8, 20, 10,  9, 95, 11, 78, 48, 20, 10, 1, 0),
        },
    },
    # --- GOALKEEPERS ---
    "Alisson": {
        "position": "GK", "nationality": "Brazilian",
        "seasons": {
            "2018-19": ("Liverpool", 25, 38, 38, 3420, 1, 1, 0.2, 0.2,  2,  1, 2, 15, 5, 0, 0, 0, 0, 0, 0),
            "2019-20": ("Liverpool", 26, 29, 29, 2610, 0, 0, 0.1, 0.1,  1,  0, 1, 12, 4, 0, 0, 0, 0, 1, 0),
            "2020-21": ("Liverpool", 27, 21, 21, 1890, 0, 1, 0.1, 0.2,  1,  0, 2, 10, 3, 0, 0, 0, 0, 0, 0),
            "2021-22": ("Liverpool", 28, 36, 36, 3240, 0, 0, 0.1, 0.1,  1,  0, 1, 14, 4, 0, 0, 0, 0, 0, 0),
            "2022-23": ("Liverpool", 29, 34, 34, 3060, 0, 0, 0.1, 0.1,  1,  0, 1, 12, 3, 0, 0, 0, 0, 0, 0),
            "2023-24": ("Liverpool", 30, 33, 33, 2970, 0, 0, 0.1, 0.1,  1,  0, 1, 12, 3, 0, 0, 0, 0, 0, 0),
        },
    },
    "Ederson": {
        "position": "GK", "nationality": "Brazilian",
        "seasons": {
            "2017-18": ("Manchester City", 23, 37, 37, 3330, 0, 0, 0.1, 0.1,  1,  0, 2, 18, 5, 0, 0, 0, 0, 0, 0),
            "2018-19": ("Manchester City", 24, 38, 38, 3420, 0, 0, 0.1, 0.1,  1,  0, 2, 18, 5, 0, 0, 0, 0, 0, 0),
            "2019-20": ("Manchester City", 25, 35, 35, 3150, 0, 0, 0.1, 0.1,  1,  0, 2, 16, 4, 0, 0, 0, 0, 0, 0),
            "2020-21": ("Manchester City", 26, 38, 38, 3420, 0, 0, 0.1, 0.1,  1,  0, 2, 18, 5, 0, 0, 0, 0, 0, 0),
            "2021-22": ("Manchester City", 27, 38, 38, 3420, 0, 0, 0.1, 0.1,  1,  0, 2, 18, 5, 0, 0, 0, 0, 0, 0),
            "2022-23": ("Manchester City", 28, 38, 38, 3420, 0, 0, 0.1, 0.1,  1,  0, 2, 18, 5, 0, 0, 0, 0, 0, 0),
            "2023-24": ("Manchester City", 29, 30, 30, 2700, 0, 0, 0.1, 0.1,  1,  0, 2, 14, 4, 0, 0, 0, 0, 0, 0),
        },
    },
}

# ---------------------------------------------------------------------------
# Name pools for generated players
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    "James","John","William","Oliver","Harry","George","Charlie","Jack","Noah","Ethan",
    "Lucas","Liam","Mason","Logan","Elijah","Aiden","Daniel","Owen","Sebastian","Henry",
    "Alex","Jordan","Tyler","Ryan","Nathan","Dylan","Brandon","Cameron","Callum","Leon",
    "Pierre","Andre","Theo","Kieran","Aaron","Reece","Ben","Tom","Sam","Chris","Matt","Josh",
    "Raheem","Sadio","Romelu","Tammy","Eddie","Ollie","Emile","Jadon","Jude","Kobbie",
    "Casemiro","Raphael","Rodri","Bernardo","Ilkay","Leandro","Ferran","Riyad","Joao","Diogo",
    "Ivan","Sergio","Roberto","Alvaro","Diego","Carlos","Pablo","Antonio","Marcos","Jesus",
    "Wilfried","Yannick","Nicolas","Maxwel","Ismaila","Amadou","Mamadou","Cheikhou",
]

LAST_NAMES = [
    "Smith","Jones","Williams","Brown","Taylor","Davies","Wilson","Evans","Thomas","Roberts",
    "Johnson","White","Martin","Anderson","Thompson","Garcia","Martinez","Robinson","Clark","Lewis",
    "Walker","Hall","Allen","Young","Hernandez","King","Wright","Lopez","Hill","Scott",
    "Green","Adams","Baker","Gonzalez","Nelson","Carter","Mitchell","Perez","Roberts","Turner",
    "Phillips","Campbell","Parker","Evans","Edwards","Collins","Stewart","Sanchez","Morris","Rogers",
    "Reed","Cook","Morgan","Bell","Murphy","Bailey","Rivera","Cooper","Richardson","Cox",
    "Howard","Ward","Torres","Peterson","Gray","Ramirez","James","Watson","Brooks","Kelly",
    "Sanders","Price","Bennett","Wood","Barnes","Ross","Henderson","Coleman","Jenkins","Perry",
    "Silva","Santos","Ferreira","Oliveira","Rodrigues","Costa","Alves","Pereira","Carvalho","Gomes",
    "Diallo","Traore","Kone","Cisse","Toure","Keita","Dembele","Sissoko","Camara","Balde",
]

NATIONALITIES = [
    "English","English","English","English","English","English",
    "French","French","Spanish","German","Portuguese","Brazilian",
    "Argentine","Belgian","Dutch","Irish","Scottish","Welsh",
    "Senegalese","Ivory Coast","Nigerian","Ghanaian","South African",
    "Moroccan","Algerian","Cameroonian","Egyptian","Jamaican",
    "Swedish","Norwegian","Danish","Serbian","Croatian","Polish",
    "Czech","Slovak","Hungarian","Romanian","Ukrainian",
    "Japanese","South Korean","Australian","American","Canadian",
]


def _rand_name() -> str:
    return f"{RNG.choice(FIRST_NAMES)} {RNG.choice(LAST_NAMES)}"


# ---------------------------------------------------------------------------
# Position-specific stat distributions
# mu, sigma for: goals, assists, xG_offset, xA_offset,
#                shots, shots_pct, key_passes, prog_passes, prog_carries,
#                tackles, interceptions, blocks, aerial_duels, yellow, red
# ---------------------------------------------------------------------------
POSITION_PARAMS = {
    "FW": dict(
        goals=(8, 6), assists=(4, 3), xG_adj=0.85, xA_adj=0.80,
        shots=(70, 30), sot_pct=(0.45, 0.07), key_passes=(30, 15),
        prog_passes=(55, 22), prog_carries=(65, 22),
        tackles=(18, 8), interceptions=(10, 5), blocks=(8, 4),
        aerial=(18, 10), yellow=(2, 1.5), red=(0.1, 0.2),
    ),
    "MF": dict(
        goals=(4, 3), assists=(5, 4), xG_adj=0.82, xA_adj=0.78,
        shots=(40, 20), sot_pct=(0.38, 0.08), key_passes=(55, 25),
        prog_passes=(110, 40), prog_carries=(55, 22),
        tackles=(45, 20), interceptions=(28, 14), blocks=(18, 9),
        aerial=(15, 8), yellow=(3, 2), red=(0.1, 0.2),
    ),
    "DF": dict(
        goals=(1, 1), assists=(2, 2), xG_adj=0.70, xA_adj=0.70,
        shots=(14, 8), sot_pct=(0.32, 0.09), key_passes=(18, 10),
        prog_passes=(88, 35), prog_carries=(28, 14),
        tackles=(58, 22), interceptions=(42, 18), blocks=(25, 12),
        aerial=(55, 25), yellow=(4, 2), red=(0.1, 0.2),
    ),
    "GK": dict(
        goals=(0, 0), assists=(0, 0), xG_adj=0.0, xA_adj=0.0,
        shots=(1, 1), sot_pct=(0.2, 0.1), key_passes=(2, 2),
        prog_passes=(20, 10), prog_carries=(2, 2),
        tackles=(1, 1), interceptions=(1, 1), blocks=(0, 0),
        aerial=(5, 4), yellow=(1, 1), red=(0.02, 0.1),
    ),
}


def _generate_player_season(name: str, pos: str, team: str, season: str,
                             age: int, minutes_budget: int) -> dict:
    """Generate a realistic player season row for a squad player."""
    p = POSITION_PARAMS[pos]
    minutes = max(90, int(RNG.normal(minutes_budget, minutes_budget * 0.20)))
    minutes = min(minutes, 3420)
    matches_started = max(1, int(minutes / 90))
    matches_played = min(38, matches_started + RNG.integers(0, 5))

    goals = max(0, int(RNG.normal(*p["goals"])))
    assists = max(0, int(RNG.normal(*p["assists"])))
    xG = max(0.0, round(goals / max(1, p["xG_adj"]) + RNG.normal(0, 1.5), 1))
    xA = max(0.0, round(assists / max(1, p["xA_adj"]) + RNG.normal(0, 1.0), 1))
    shots = max(0, int(RNG.normal(*p["shots"])))
    sot = max(0, int(shots * max(0.1, RNG.normal(p["sot_pct"][0], p["sot_pct"][1]))))
    key_passes = max(0, int(RNG.normal(*p["key_passes"])))
    prog_passes = max(0, int(RNG.normal(*p["prog_passes"])))
    prog_carries = max(0, int(RNG.normal(*p["prog_carries"])))
    tackles = max(0, int(RNG.normal(*p["tackles"])))
    interceptions = max(0, int(RNG.normal(*p["interceptions"])))
    blocks = max(0, int(RNG.normal(*p["blocks"])))
    aerial = max(0, int(RNG.normal(*p["aerial"])))
    yellow = max(0, int(RNG.normal(*p["yellow"])))
    red = max(0, int(RNG.normal(p["red"][0], p["red"][1])))
    dribbles = max(0, int(RNG.normal(12, 8)))

    per90 = 90 / max(1, minutes)
    return dict(
        player_name=name, season=season, team=team, position=pos,
        nationality=RNG.choice(NATIONALITIES), age=age,
        matches_played=matches_played, matches_started=matches_started, minutes=minutes,
        goals=goals, assists=assists, xG=xG, xA=xA,
        goals_per90=round(goals * per90, 3), assists_per90=round(assists * per90, 3),
        goal_contributions=goals + assists,
        shots=shots, shots_on_target=sot, key_passes=key_passes,
        progressive_passes=prog_passes, progressive_carries=prog_carries,
        tackles=tackles, interceptions=interceptions, blocks=blocks,
        aerial_duels_won=aerial, dribbles=dribbles,
        yellow_cards=yellow, red_cards=red, is_featured=False,
    )


def _featured_row(name: str, pos: str, nat: str, season: str,
                  data: tuple) -> dict:
    """Convert a featured player season tuple into a row dict."""
    (team, age, mp, ms, minutes, goals, assists, xG, xA,
     shots, sot, kp, pp, pc, tk, int_, blk, aw, yc, rc) = data

    per90 = 90 / max(1, minutes)
    dribbles = max(0, int(RNG.normal(15, 8)))
    return dict(
        player_name=name, season=season, team=team, position=pos,
        nationality=nat, age=age,
        matches_played=mp, matches_started=ms, minutes=minutes,
        goals=goals, assists=assists, xG=xG, xA=xA,
        goals_per90=round(goals * per90, 3), assists_per90=round(assists * per90, 3),
        goal_contributions=goals + assists,
        shots=shots, shots_on_target=sot, key_passes=kp,
        progressive_passes=pp, progressive_carries=pc,
        tackles=tk, interceptions=int_, blocks=blk,
        aerial_duels_won=aw, dribbles=dribbles,
        yellow_cards=yc, red_cards=rc, is_featured=True,
    )


def generate_players_data() -> pd.DataFrame:
    rows = []

    # Featured players
    for name, info in FEATURED_PLAYERS.items():
        pos = info["position"]
        nat = info["nationality"]
        for season, data in info["seasons"].items():
            rows.append(_featured_row(name, pos, nat, season, data))

    # Squad players: fill each team-season with realistic depth
    position_slots = {"GK": 3, "DF": 7, "MF": 7, "FW": 6}
    for season, teams in SEASON_TEAMS.items():
        featured_in_season = {
            (r["player_name"], r["season"]): r["team"]
            for r in rows if r["season"] == season
        }
        for team in teams:
            for pos, n_slots in position_slots.items():
                for _ in range(n_slots):
                    name = _rand_name()
                    age = int(RNG.integers(18, 35))
                    # Starters get more minutes; bench players get less
                    is_starter = RNG.random() < 0.55
                    budget = int(RNG.normal(2400, 400)) if is_starter else int(RNG.normal(900, 350))
                    budget = max(90, budget)
                    row = _generate_player_season(name, pos, team, season, age, budget)
                    rows.append(row)

    df = pd.DataFrame(rows)
    # Ensure no duplicate featured players per season
    df = df.drop_duplicates(subset=["player_name", "season"])
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Team data
# ---------------------------------------------------------------------------
TEAM_SEASON_RESULTS = {
    # (wins, draws, losses, gf, ga, cs, possession, xGf, xGa)
    ("Manchester City",   "2014-15"): (24,  7,  7, 83, 38, 14, 55.8, 75.2, 35.1),
    ("Chelsea",           "2014-15"): (26,  9,  3, 73, 32, 17, 52.4, 66.1, 30.5),
    ("Arsenal",           "2014-15"): (22,  9,  7, 71, 36, 10, 55.2, 64.2, 33.8),
    ("Manchester United", "2014-15"): (20, 10,  8, 62, 37, 11, 52.1, 56.8, 34.2),
    ("Tottenham",         "2014-15"): (19,  7, 12, 58, 53,  9, 52.8, 54.2, 48.5),
    ("Liverpool",         "2014-15"): (18,  8, 12, 52, 48,  8, 54.2, 49.1, 44.2),

    ("Leicester City",    "2015-16"): (23, 12,  3, 68, 36, 15, 44.1, 58.9, 33.8),
    ("Arsenal",           "2015-16"): (20, 11,  7, 65, 36, 12, 55.8, 61.2, 33.1),
    ("Tottenham",         "2015-16"): (19, 13,  6, 69, 35, 15, 53.2, 64.1, 32.5),
    ("Manchester City",   "2015-16"): (19,  9, 10, 71, 41, 10, 56.1, 66.5, 38.5),
    ("Manchester United", "2015-16"): (19,  9, 10, 49, 35, 11, 52.5, 46.2, 33.2),
    ("Southampton",       "2015-16"): (18,  9, 11, 59, 41, 14, 49.8, 54.2, 39.1),

    ("Chelsea",           "2016-17"): (30,  3,  5, 85, 33, 16, 51.8, 77.5, 31.2),
    ("Tottenham",         "2016-17"): (26,  8,  4, 86, 26, 17, 55.5, 78.5, 25.8),
    ("Manchester City",   "2016-17"): (23,  9,  6, 80, 39, 15, 57.2, 73.5, 37.8),
    ("Liverpool",         "2016-17"): (22, 10,  6, 78, 42, 11, 55.8, 72.1, 40.5),
    ("Arsenal",           "2016-17"): (23,  6,  9, 77, 44, 11, 56.2, 70.5, 41.8),

    ("Manchester City",   "2017-18"): (32,  4,  2, 106, 27, 20, 58.8, 96.2, 26.5),
    ("Manchester United", "2017-18"): (25,  6,  7, 68, 28, 18, 52.1, 62.5, 27.2),
    ("Tottenham",         "2017-18"): (23,  8,  7, 74, 36, 14, 53.5, 67.8, 34.5),
    ("Liverpool",         "2017-18"): (21, 12,  5, 84, 38, 11, 56.2, 78.5, 36.1),
    ("Chelsea",           "2017-18"): (21,  7, 10, 62, 38, 12, 52.8, 58.5, 36.8),
    ("Arsenal",           "2017-18"): (19,  6, 13, 74, 51,  8, 56.5, 68.2, 49.5),

    ("Manchester City",   "2018-19"): (32,  2,  4, 95, 23, 20, 58.5, 87.5, 22.5),
    ("Liverpool",         "2018-19"): (30,  7,  1, 89, 22, 21, 57.5, 84.2, 21.8),
    ("Chelsea",           "2018-19"): (21,  9,  8, 63, 39, 11, 53.5, 60.5, 37.8),
    ("Tottenham",         "2018-19"): (23,  2, 13, 67, 39, 11, 53.8, 63.2, 37.5),
    ("Arsenal",           "2018-19"): (21,  7, 10, 73, 51,  9, 55.5, 70.5, 49.2),
    ("Manchester United", "2018-19"): (19,  9, 10, 65, 54,  8, 51.5, 62.2, 52.5),

    ("Liverpool",         "2019-20"): (32,  3,  3, 85, 33, 13, 58.2, 80.5, 31.8),
    ("Manchester City",   "2019-20"): (26,  3,  9, 102, 35, 16, 58.8, 96.5, 33.8),
    ("Manchester United", "2019-20"): (18, 12,  8, 66, 36, 13, 52.5, 62.8, 34.5),
    ("Chelsea",           "2019-20"): (20,  6, 12, 69, 54,  9, 54.8, 65.5, 52.5),
    ("Leicester City",    "2019-20"): (18,  8, 12, 67, 41, 13, 50.5, 63.5, 39.5),
    ("Tottenham",         "2019-20"): (16, 11, 11, 61, 47,  8, 52.5, 58.5, 45.5),

    ("Manchester City",   "2020-21"): (27,  5,  6, 83, 32, 15, 58.5, 78.5, 30.8),
    ("Manchester United", "2020-21"): (21, 11,  6, 73, 44, 12, 52.5, 70.5, 42.5),
    ("Liverpool",         "2020-21"): (20,  9,  9, 68, 42, 10, 57.5, 65.5, 40.5),
    ("Chelsea",           "2020-21"): (19, 10,  9, 58, 36, 14, 53.5, 56.5, 35.5),
    ("Leicester City",    "2020-21"): (20,  6, 12, 68, 50,  9, 50.5, 65.5, 48.5),
    ("West Ham United",   "2020-21"): (19,  8, 11, 62, 47, 10, 48.5, 59.5, 45.5),

    ("Manchester City",   "2021-22"): (29,  6,  3, 99, 26, 20, 57.5, 91.5, 25.5),
    ("Liverpool",         "2021-22"): (28,  8,  2, 94, 26, 22, 58.5, 89.5, 25.5),
    ("Chelsea",           "2021-22"): (21, 11,  6, 76, 33, 16, 55.5, 73.5, 32.5),
    ("Tottenham",         "2021-22"): (22,  5, 11, 69, 40, 12, 54.5, 66.5, 38.5),
    ("Arsenal",           "2021-22"): (22,  3, 13, 61, 48,  9, 55.5, 58.5, 46.5),
    ("Manchester United", "2021-22"): (16, 10, 12, 57, 57,  8, 52.5, 55.5, 55.5),

    ("Manchester City",   "2022-23"): (28,  5,  5, 94, 33, 17, 57.5, 87.5, 32.5),
    ("Arsenal",           "2022-23"): (26,  6,  6, 88, 43, 14, 57.5, 83.5, 41.5),
    ("Manchester United", "2022-23"): (23,  6,  9, 58, 43, 11, 52.5, 56.5, 41.5),
    ("Newcastle United",  "2022-23"): (19, 14,  5, 68, 33, 17, 49.5, 65.5, 32.5),
    ("Liverpool",         "2022-23"): (19, 10,  9, 75, 47, 12, 57.5, 72.5, 45.5),
    ("Brighton",          "2022-23"): (18,  8, 12, 72, 53, 10, 56.5, 69.5, 51.5),

    ("Manchester City",   "2023-24"): (28,  7,  3, 96, 34, 18, 57.5, 89.5, 33.5),
    ("Arsenal",           "2023-24"): (28,  5,  5, 91, 29, 18, 58.5, 86.5, 28.5),
    ("Liverpool",         "2023-24"): (24,  8,  6, 86, 41, 16, 58.5, 82.5, 39.5),
    ("Aston Villa",       "2023-24"): (20, 10,  8, 76, 61, 12, 51.5, 73.5, 59.5),
    ("Tottenham",         "2023-24"): (20,  6, 12, 74, 61, 10, 54.5, 71.5, 59.5),
    ("Chelsea",           "2023-24"): (18, 12,  8, 77, 63, 11, 54.5, 74.5, 61.5),
}

TEAM_TIER = {
    "Manchester City": 1, "Liverpool": 1, "Chelsea": 1, "Arsenal": 1,
    "Manchester United": 2, "Tottenham": 2,
    "Leicester City": 2, "Newcastle United": 2, "West Ham United": 2,
    "Aston Villa": 3, "Everton": 3, "Brighton": 3, "Wolverhampton": 3,
    "Crystal Palace": 3, "Brentford": 3, "Fulham": 3,
    "Southampton": 4, "Burnley": 4, "Watford": 4, "Norwich City": 4,
    "Stoke City": 4, "Swansea City": 4, "Hull City": 4, "Sunderland": 4,
    "West Bromwich Albion": 4, "Middlesbrough": 4, "Cardiff City": 4,
    "Queens Park Rangers": 4, "Huddersfield": 4, "Sheffield United": 4,
    "Leeds United": 3, "Bournemouth": 3, "Nottingham Forest": 3,
    "Luton Town": 4, "Brentford": 3,
}


def _generate_team_season(team: str, season: str) -> dict:
    """Generate a realistic team season from tier-based distributions."""
    tier = TEAM_TIER.get(team, 3)
    base_wins = [22, 16, 11, 7][tier - 1]
    wins = max(1, int(RNG.normal(base_wins, 5)))
    draws = max(0, int(RNG.normal(8, 3)))
    losses = max(0, 38 - wins - draws)
    if wins + draws + losses != 38:
        losses = 38 - wins - draws

    base_gf = [85, 58, 48, 38][tier - 1]
    base_ga = [30, 42, 52, 62][tier - 1]
    gf = max(20, int(RNG.normal(base_gf, 12)))
    ga = max(15, int(RNG.normal(base_ga, 12)))
    cs = max(0, int(wins * RNG.uniform(0.35, 0.65)))
    possession = round(max(38, min(68, float(RNG.normal([56, 50, 47, 44][tier - 1], 3)))), 1)
    xGf = round(max(20.0, gf * RNG.uniform(0.88, 1.05)), 1)
    xGa = round(max(18.0, ga * RNG.uniform(0.88, 1.05)), 1)

    return dict(
        team=team, season=season,
        matches_played=38, wins=wins, draws=draws, losses=losses,
        goals_for=gf, goals_against=ga, goal_difference=gf - ga,
        points=wins * 3 + draws,
        clean_sheets=cs, possession=possession,
        xG_for=xGf, xG_against=xGa,
        win_percentage=round(wins / 38 * 100, 1),
        ppg=round((wins * 3 + draws) / 38, 2),
    )


def generate_teams_data() -> pd.DataFrame:
    rows = []
    for season, teams in SEASON_TEAMS.items():
        for team in teams:
            key = (team, season)
            if key in TEAM_SEASON_RESULTS:
                (w, d, l, gf, ga, cs, poss, xGf, xGa) = TEAM_SEASON_RESULTS[key]
                rows.append(dict(
                    team=team, season=season,
                    matches_played=38, wins=w, draws=d, losses=l,
                    goals_for=gf, goals_against=ga, goal_difference=gf - ga,
                    points=w * 3 + d, clean_sheets=cs, possession=poss,
                    xG_for=xGf, xG_against=xGa,
                    win_percentage=round(w / 38 * 100, 1),
                    ppg=round((w * 3 + d) / 38, 2),
                ))
            else:
                rows.append(_generate_team_season(team, season))

    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["team", "season"])

    # Add league position per season
    df["position"] = (
        df.groupby("season")["points"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    return df.reset_index(drop=True)
