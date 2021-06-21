PASSING_TIME = 10 # Common passing time between classes, in minutes(302-307)
TOTAL_AGENTS = 2380 # 1500 on-campus students, 500 off-campus students, and 380 faculties (217-218)
SPACE_CAPACITIES = {"Transit Space": 100 * TOTAL_AGENTS, "Dining Hall": 650, "Library": 300 * PASSING_TIME,
                    "Gym": 60 * PASSING_TIME}
SPACE_RISK_MULTIPLIERS = {"Transit Space": 1, "Dining Hall": 1, "Library": 1, "Gym": 3,
                          "Office": 1, "Large Gatherings": 3, "Academic": 1, "Dorm": 2}
SUBSPACE_CAPACITIES = {"Dining Hall": 100, "Faculty Dining Leaf": 20, "Library": 50, "Gym": 10,
                       "Social Space": 10}
SUBSPACE_RISK_MULTIPLIERS = {"Dining Hall": 2, "Faculty Dining Leaf": 2, "Library": 2, "Gym": 3,
                             "Office": 2, "Social Space": 3, "Classroom": 2, "Dorm": 3}
ACADEMIC_SUBSPACE_CAPACITIES = {"Small": 15, "Medium": 20, "Large": 30}

DORM_BUILDINGS = {"Small": 25, "Medium": 10, "Large": 10}  # number of dorm buildings for each size (small/medium/large)
