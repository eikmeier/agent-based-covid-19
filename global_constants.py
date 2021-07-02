PASSING_TIME = 10  # Common passing time between classes, in minutes (302-307)
TOTAL_AGENTS = 2380  # 1500 on-campus students, 500 off-campus students, and 380 faculties (217-218)
SPACE_CAPACITIES = {"Transit Space": 100 * TOTAL_AGENTS, "Dining Hall": 650, "Library": 300 * PASSING_TIME,
                    "Gym": 60 * PASSING_TIME}
SPACE_RISK_MULTIPLIERS = {"Transit Space": 1, "Dining Hall": 1, "Library": 1, "Gym": 3,
                          "Office": 1, "Large Gatherings": 3, "Academic": 1, "Dorm": 2}
SUBSPACE_CAPACITIES = {"Dining Hall": 100, "Faculty Dining Leaf": 20, "Library": 50, "Gym": 10,
                       "Social Space": 10}
SUBSPACE_RISK_MULTIPLIERS = {"Dining Hall": 2, "Faculty Dining Leaf": 2, "Library": 2, "Gym": 3,
                             "Office": 2, "Social Space": 3, "Classroom": 2, "Dorm": 3}
ACADEMIC_SPACE_CAPACITIES = {"Small": PASSING_TIME * 45, "Medium": PASSING_TIME * 90, "Large": PASSING_TIME * 225}
ACADEMIC_SUBSPACE_CAPACITIES = {"Small": 15, "Medium": 20, "Large": 30}  # capacity for small/medium/large classrooms
ACADEMIC_SUBSPACE_SEATS = {"Small": 10, "Medium": 15, "Large": 20}  # number of seats for small/medium/large classrooms

DORM_BUILDINGS = {"Small": 25, "Medium": 10, "Large": 10}  # number of dorm buildings for each size (small/medium/large)

ACADEMIC_BUILDINGS = {"STEM": [2, 2, 3], "Humanities": [1, 2, 1], "Arts": [2, 1, 1]}  # number of [small, medium, large] buildings for each academic building
CLASSROOMS = {"Small": [3, 0, 0], "Medium": [2, 3, 0], "Large": [5, 3, 3]}  # number of [small, medium, large] classrooms for each building size(small/medium/large)

PROBABILITY_G = 0.15
PROBABILITY_S = 0.15
PROBABILITY_L = 0.15