# Key Parameters
PASSING_TIME = 10  # Common passing time between classes, in minutes
TOTAL_AGENTS = 2380  # 1500 on-campus students, 500 off-campus students, and 380 faculties
INITIALLY_INFECTED = 10  # Number of agents that are initially infected (before running the simulation)
SIMULATION_LENGTH = 15  # Number of weeks the simulation should go for
TUNING_PARAMETER = 1.25

# Attribute Proportions
OFF_CAMPUS_STUDENT_PROPORTION = 500.0/TOTAL_AGENTS
FACULTY_PROPORTION = 380.0/TOTAL_AGENTS
HUMANITIES_PROPORTION = 0.25 # Proportion of agents in the Humanities division
ARTS_PROPORTION = 0.25 # Proportion of agents in the Arts division
SOCIAL_RATIO = 0.5 # Proportion of students that are social

# Space/Subspace Capacities and Multipliers
SPACE_CAPACITIES = {"Transit Space": 100 * TOTAL_AGENTS, "Dining Hall": 650, "Library": 300 * PASSING_TIME,
                    "Gym": 60 * PASSING_TIME}
SPACE_RISK_MULTIPLIERS = {"Transit Space": 1, "Dining Hall": 1, "Library": 1, "Gym": 3,
                          "Office": 1, "Large Gatherings": 3, "Academic": 1, "Dorm": 2}
SPACE_SUBSPACE_AMOUNT = {"Dining Hall": 6, "Library": 6, "Gym": 6, "Office": 6, "Social Space": 100}
SUBSPACE_CAPACITIES = {"Dining Hall": 100, "Faculty Dining Leaf": 20, "Library": 50, "Gym": 10,
                       "Social Space": 10}
SUBSPACE_RISK_MULTIPLIERS = {"Dining Hall": 2, "Faculty Dining Leaf": 2, "Library": 2, "Gym": 3,
                             "Office": 2, "Social Space": 3, "Classroom": 2, "Dorm": 3}
ACADEMIC_SPACE_CAPACITIES = {"Small": PASSING_TIME * 45, "Medium": PASSING_TIME * 90, "Large": PASSING_TIME * 225}
ACADEMIC_SUBSPACE_CAPACITIES = {"Small": 15, "Medium": 20, "Large": 30}  # Capacity for small/medium/large classrooms

# Academic Constants
ACADEMIC_SUBSPACE_SEATS = {"Small": 10, "Medium": 15, "Large": 20}  # Number of seats for small/medium/large classrooms
ACADEMIC_BUILDINGS = {"STEM": [2, 2, 3], "Humanities": [1, 2, 1], "Arts": [2, 1, 1]}  # Number of [small, medium, large] buildings for each academic building
CLASSROOMS = {"Small": [3, 0, 0], "Medium": [2, 3, 0], "Large": [5, 3, 3]}  # Number of [small, medium, large] classrooms for each building size(small/medium/large)
CLASS_TIMES = [10, 12, 14, 16]  # All classes must be at either 10 AM, 12 PM, 2 PM, or 4 PM

# Dorm Constants
DORM_BUILDINGS = {"Small": 25, "Medium": 10, "Large": 10}  # Number of dorm buildings for each size (small/medium/large)

# Probabilities
PROBABILITY_A = 0.15 # Probability of remaining asymptomatic after 2 days of being infected asymptomatic
PROBABILITY_E = 0.5 # Probability of transitioning from infected asymptomatic to infected and extremely symptomatic after 2 days of being asymptomatic
PROBABILITY_G = 0.15 # Probability of being assigned to the gym during a type of day (A, B, W)
PROBABILITY_L = 0.15 # Probability of being assigned to the library during a type of day (A, B, W)
PROBABILITY_S = 0.15 # Probability of being assigned to a social space during a type of day (A, B, W)

# Scheduling
SCHEDULE_DAYS = ['A', 'B', 'W']
SCHEDULE_WEEKDAYS = ['A', 'B']
SCHEDULE_HOURS = list(range(8, 23))

# Interventions
INTERVENTIONS = {"Vaccine": False, "Face mask": False, "Screening": False}
VACCINE_PERCENTAGE = {"Faculty": 0, "Student": 0}
VACCINE_SELF_EFFECTIVENESS = 0.7
VACCINE_SPREAD_EFFECTIVENESS = 0.7
FACE_MASK_COMPLIANCE = 0.5
SCREENING_COMPLIANCE = 0.5
