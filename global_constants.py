# Agent Initialization
TOTAL_AGENTS = 2380  # 2380 # 1500 on-campus students, 500 off-campus students, and 380 faculties (217-218)
TYPE_RATIO = [500.0/TOTAL_AGENTS, 380.0/TOTAL_AGENTS]  # proportion of ["Off-campus Students", "Faculty"] - default value is "On-campus Student"
DIVISION_RATIO = [0.25, 0.25]  # proportion of ["Humanities", "Arts"] - default value is "STEM"
SOCIAL_RATIO = 0.5  # proportion of students that are social



# Simulation Settings
SIMULATION_LENGTH = 15  # Number of weeks the simulation should go for
INITIALLY_INFECTED = 10  # Number of agents that are initially infected (before running the simulation)
INITIAL_INFECTION_PROPORTION = INITIALLY_INFECTED/TOTAL_AGENTS  # proportion of agents initially in the exposed state
CLASS_TIMES = [10, 12, 14, 16]  # All classes must be at either 10 AM, 12 PM, 2 PM, or 4 PM
SCHEDULE_DAYS = ['A', 'B', 'W']
SCHEDULE_WEEKDAYS = ['A', 'B']
WEEK_SCHEDULE = ['A', 'B', 'A', 'B', 'W', 'W', 'S']
SCHEDULE_HOURS = list(range(8, 23))
EXPOSED_SPACES = {"Dorm": 0, "Academic": 0, "DiningHall": 0, "Gym": 0, "Library": 0, "Office": 0, "SocialSpace": 0, "TransitSpace": 0, "LargeGatherings": 0, "Off-Campus": 0, "Other": 0}


# Risk Multipliers/Parameters
SPACE_RISK_MULTIPLIERS = {"Transit Space": 1, "Dining Hall": 1, "Library": 1, "Gym": 3, "Office": 1, "Large Gatherings": 3, "Academic": 1, "Dorm": 2}
SUBSPACE_RISK_MULTIPLIERS = {"Dining Hall": 2, "Faculty Dining Leaf": 2, "Library": 2, "Gym": 3, "Office": 2, "Social Space": 3, "Classroom": 2, "Dorm": 3}
TUNING_PARAMETER = 1.25
# TUNING_PARAMETER = {"Alpha": 1.25, "Delta": 2.50, "Other": 0}
PASSING_TIME = 10  # Common passing time between classes, in minutes (302-307)
VARIANT_RISK_MULTIPLIER = {"Alpha": 1, "Delta": 2, "Other": 0}

# Capacities
SPACE_CAPACITIES = {"Transit Space": 100 * TOTAL_AGENTS, "Dining Hall": 650, "Library": 300 * PASSING_TIME, "Gym": 60 * PASSING_TIME}
SUBSPACE_CAPACITIES = {"Dining Hall": 100, "Faculty Dining Leaf": 20, "Library": 50, "Gym": 10, "Social Space": 10}
ACADEMIC_SPACE_CAPACITIES = {"Small": PASSING_TIME * 45, "Medium": PASSING_TIME * 90, "Large": PASSING_TIME * 225}
ACADEMIC_SUBSPACE_CAPACITIES = {"Small": 15, "Medium": 20, "Large": 30}  # capacity for small/medium/large classrooms
ACADEMIC_SUBSPACE_SEATS = {"Small": 10, "Medium": 15, "Large": 20}  # number of seats for small/medium/large classrooms


# Number of spaces/buildings
SPACE_SUBSPACE_AMOUNT = {"Dining Hall": 6, "Library": 6, "Gym": 6, "Office": 6, "Social Space": 100}
DORM_BUILDINGS = {"Small": 25, "Medium": 10, "Large": 10}  # number of dorm buildings for each size (small/medium/large)
ACADEMIC_BUILDINGS = {"STEM": [2, 2, 3], "Humanities": [1, 2, 1], "Arts": [2, 1, 1]}  # number of [small, medium, large] buildings for each academic building
CLASSROOMS = {"Small": [3, 0, 0], "Medium": [2, 3, 0], "Large": [5, 3, 3]}  # number of [small, medium, large] classrooms for each building size(small/medium/large)


# Probabilities
PROBABILITY_G = 0.15
PROBABILITY_S = 0.15
PROBABILITY_L = 0.15
PROBABILITY_E = 0.5
PROBABILITY_A = 0.15


# Intervention Settings
INTERVENTIONS = {"Vaccine": False, "Face mask": False, "Screening": False}  # interventions that will be used in simulation (True)
COVID_VARIANTS = {"Alpha": False, "Delta": False, "Other": False}  # variant of covid virus (either Alpha, Delta, or other created by user input)

# Vaccine intervention
VACCINE_PERCENTAGE = {"Faculty": 0, "Student": 0}
VACCINE_SELF = {"Alpha": 0.7, "Delta": 0.3, "Other": 0}
VACCINE_SPREAD = {"Alpha": 0.7, "Delta": 0.3, "Other": 0}

# Face mask intervention
FACE_MASK_LEVEL = "all"  # either ["all", "only unvaccinated"] have to wear masks
FACE_MASK_COMPLIANCE = 0.5  # percentage of total agents complying with face mask intervention
FACE_MASK_SELF = {"Alpha": 0.75, "Delta": 0.3, "Other": 0}
FACE_MASK_SPREAD = {"Alpha": 0.5, "Delta": 0.3, "Other": 0}


# Screening test intervention
SCREENING_PERCENTAGE = 0.5  # [0.25, 0.5, 1]
TESTING_DAY_INDEX = 0  # day of weekly testing (0 = "Monday", 1 = "Tuesday"...)
LATENCY_PERIOD = 2  # [1, 2, 3, 4] days
SCREENING_COMPLIANCE = 0.80  # [0.80, 0.90, 1]
FALSE_POSITIVE_RATE = 0.001  # possibility of agent in state ["S", "E", "R"] receiving positive result
FALSE_NEGATIVE_RATE = 0.03  # possibility of infected agent ["Ia", "Im", "Ie"] receiving negative result
WALK_IN_PROBABILITY = {"Im": 0.70, "Ie": 0.95}







