from global_constants import TOTAL_AGENTS, SPACE_SUBSPACE_AMOUNT, PROBABILITY_E, PROBABILITY_A, INITIALLY_INFECTED, VACCINE_SELF_EFFECTIVENESS, \
 VACCINE_SPREAD_EFFECTIVENESS, FACE_MASK_COMPLIANCE, SCREENING_COMPLIANCE, OFF_CAMPUS_STUDENT_PROPORTION, FACULTY_PROPORTION, HUMANITIES_PROPORTION, \
 ARTS_PROPORTION, SOCIAL_RATIO
import random
import pickle

class Agent:
    def __init__(self):
        self.vaccinated = False 
        self.vaccinated_self_risk_multiplier = 1
        self.vaccinated_spread_risk_multiplier = 1
        self.face_mask_compliant = False  # By default agents are not face mask compliant
        self.face_mask_self_risk_multiplier = {"Dorm": 1, "Academic": 1, "DiningHall": 1, "Gym": 1, "Library": 1, "Office": 1,
                                                "SocialSpace": 1, "TransitSpace": 1, "LargeGatherings": 1}
        self.face_mask_spread_risk_multiplier = {"Dorm": 1, "Academic": 1, "DiningHall": 1, "Gym": 1, "Library": 1, "Office": 1,
                                                "SocialSpace": 1, "TransitSpace": 1, "LargeGatherings": 1}
        self.screening = 0  # screening test compliance
        self.student = True
        self.off_campus = False
        self.division = "STEM"  # agent division/major (either STEM, Humanities, or Arts)
        self.seir = "S"  # agent infection states (either "S", "E", "Ia", "Im", "Ie", "R")
        self.exposed_space = None  # By default, agents do not have a space that exposed them
        self.class_times = []  # list of [[day, time], division_index]
        self.social = False  # default value is that an agent is not social
        self.schedule = {"A": [None] * 15, "B": [None] * 15, "W": [None] * 15}  # time range is from 8 ~ 22, which is 15 blocks & class times are at index 2, 4, 6, 8
        self.days_in_state = 0
        self.bedridden = False
        self.num_of_classes = 0
        # Initialize leaves - the first social space leaf is for A & B days and the second is for W days
        self.leaves = {"Dining Hall": -1, "Library": -1, "Gym": -1, "Social Space": [-1, -1], "Office": -1}

    def initialize(self):
        caI = pickle.load(open('pickle_files/interventions.p', 'rb'))
        caVP = pickle.load(open('pickle_files/vaccine_percentage.p', 'rb'))
        vaccine_intervention = caI.get("Vaccine")  # whether we use vaccine intervention or not ("on" or "off")
        faculty_vaccine_percentage = caVP.get("Faculty")
        student_vaccine_percentage = caVP.get("Student")
        face_mask_intervention = caI.get("Face mask")  # whether we use face mask intervention or not ("on" or "off")

        agents = [Agent() for agent in range(TOTAL_AGENTS)]

        # TYPE (ON-CAMPUS/OFF-CAMPUS/FACULTY): randomly select and assign a certain proportion of agents as "Off-campus Student" and "Faculty"
        random.shuffle(agents)
        for agent_num, agent in enumerate(agents): # By default, agents are on-campus students
            if agent_num < int(TOTAL_AGENTS * FACULTY_PROPORTION):
                agent.student = False
                agent.off_campus = True
            elif agent_num < int(TOTAL_AGENTS * (FACULTY_PROPORTION + OFF_CAMPUS_STUDENT_PROPORTION)): # Off-Campus agents
                agent.off_campus = True

        student_agents = [agent for agent in agents if agent.student]
        faculty_agents = list(set(agents) - set(student_agents))

        # VACCINATION: randomly select and assign vaccination to certain proportion of student/faculty agents
        if vaccine_intervention:
            select_vaccine_student = random.sample(student_agents, k=int(len(student_agents) * student_vaccine_percentage))
            select_vaccine_faculty = random.sample(faculty_agents, k=int(len(faculty_agents) * faculty_vaccine_percentage))
            for vaccine_agent in select_vaccine_student + select_vaccine_faculty:
                vaccine_agent.vaccinated = True
                vaccine_agent.vaccinated_self_risk_multiplier = (1 - VACCINE_SELF_EFFECTIVENESS)
                vaccine_agent.vaccinated_spread_risk_multiplier = (1 - VACCINE_SPREAD_EFFECTIVENESS)

        # FACE MASK COMPLIANCE: randomly select and assign face mask compliance to certain proportion of agents
        if face_mask_intervention:
            select_face_mask_compliant = random.sample(agents, k=int(TOTAL_AGENTS * FACE_MASK_COMPLIANCE))
            for agent in agents:
                if agent in select_face_mask_compliant:  # agents that comply with face masks
                    agent.face_mask_compliant = True
                    agent.face_mask_self_risk_multiplier = {"Dorm": 0.75, "Academic": 0.75, "DiningHall": 0.75, "Gym": 0.75, "Library": 0.75, "Office": 0.75,
                                                         "SocialSpace": 0.75, "TransitSpace": 0.75, "LargeGatherings": 0.75}
                    agent.face_mask_spread_risk_multiplier = {"Dorm": 0.5, "Academic": 0.5, "DiningHall": 0.5, "Gym": 0.5, "Library": 0.5, "Office": 0.5,
                                                           "SocialSpace": 0.5, "TransitSpace": 0.5, "LargeGatherings": 0.5}

                else:  # agents that don't comply with face masks (don't wear in social space, large gatherings, dorm cores, etc.)
                    agent.face_mask_self_risk_multiplier = {"Dorm": 1, "Academic": 0.75, "DiningHall": 0.75, "Gym": 0.75, "Library": 0.75, "Office": 0.75,
                                                         "SocialSpace": 1, "TransitSpace": 0.75, "LargeGatherings": 1}
                    agent.face_mask_spread_risk_multiplier = {"Dorm": 1, "Academic": 0.5, "DiningHall": 0.5, "Gym": 0.5, "Library": 0.5, "Office": 0.5,
                                                           "SocialSpace": 1, "TransitSpace": 0.5, "LargeGatherings": 1}

        #  SCREENING TEST COMPLIANCE: randomly select and assign screening test compliance to certain proportion of agents
        for agent in random.sample(agents, k=int(TOTAL_AGENTS * SCREENING_COMPLIANCE)):
            agent.screening = True

        # DIVISION (STEM/HUMANITIES/ARTS): randomly select and assign a certain proportion of agents as "Humanities" and "Arts"
        for agent_group in [faculty_agents, student_agents]:
            random.shuffle(agent_group)
            for agent_num, agent in enumerate(agent_group):
                if agent_num < (len(agent_group) * ARTS_PROPORTION):
                    agent.division = "Arts"
                elif agent_num < (len(agent_group) * (ARTS_PROPORTION + HUMANITIES_PROPORTION)):
                    agent.division = "Humanities"

        # INITIAL INFECTION: randomly select and assign agents that are initially infected
        for ag in random.sample([agent for agent in agents if agent.vaccinated == False], k=int(INITIALLY_INFECTED)):
            ag.seir = random.choice(["Ia", "Im", "Ie"])  # randomly assign one of the infected states to agents

        # SOCIAL: randomly select and assign student agents as social, which allows them to go to large gatherings
        for ag in random.sample(student_agents, k=int(TOTAL_AGENTS * SOCIAL_RATIO)):
            ag.social = True

        initialize_leaves(agents)
        return agents

    def change_state(self, state):
        """
        Changes an agent seir field to state and also sets an agent's days_in_state field to 0
        """
        self.seir = state
        self.days_in_state = 0

    def get_division_index(self):
        """
        Returns a number, 0-2, representing the division of an agent.\n
        0 is returned if an agent is in the STEM division.\n
        1 is returned if an agent is in the Humanities division.\n
        2 is returned if an agent is in the Arts division.\n
        """
        if self.division == "STEM":
            return 0
        elif self.division == "Humanities":
            return 1
        else:  # self.division == "Arts"
            return 2

    def get_available_hours(self, start_hour, end_hour, day):
        """
        Returns a list of times that an agent does not have scheduled yet.\n
        The times follow the schedule array that agents have, so the possible times returned start at 0 (representing 8 AM)
         and ending at 15 (representing 10 PM).\n
        Takes in three arguments, a start_hour and an end_hour (each should be between 8-22 to represent when agents
         are doing activities), and a day (a character that is either 'A', 'B', or 'W')
        """
        available_times = []
        for i in range(start_hour, end_hour + 1):
            if self.schedule.get(day)[i-8] == None:
                available_times.append(i-8)
        return available_times

    def __str__(self):
        """
        Returns a string representation of an agent with their type (On campus student, Off campus student, Faculty),
         their division/division (STEM, Humanities, Arts), and their seir state (S, E, Ia, Im, Ie, R).\n
        """
        return 'Agent: Student:' + str(self.student) + ' / On-Campus:'+ str(not self.off_campus) + ' /' + self.division + ' /' + self.seir #TODO: Fix

def change_states(agents):
    """
    Automatically changes the states of all agents based on the agent's days_in_state field.\n
    If an agent has been in the seir state "Ia" for 2 days, they have a PROBABILITY_E chance of changing to state "Ie",
     a PROBABILITY_E + PROBABILITY_A chance of staying in state "Ia", and otherwise changes state to "Im".\n
    If an agent has been in the seir state "E" for 2 days, the agent changes state to "Ia".\n
    If an agent has been in any infected seir state for 10 days, the agent changes to the state "R" and, if
     the agent was previously bedridden, they now no longer are.\n
    Finally, if an agent has been in the seir state "Ie" for 5 days, the agent becomes bedridden.\n
    At the end of the loop, each agent has their days_in_state field increased by one to signify that
     the current day has ended.\n
    """
    for agent in agents:
        if agent.days_in_state == 2:
            if agent.seir == "Ia":
                rand_num = random.random()
                if rand_num < PROBABILITY_E:
                    agent.change_state("Ie")
                elif rand_num < PROBABILITY_E + PROBABILITY_A:
                    agent.change_state("Ia")
                else: # An agent transitions from Ia -> Im with a probability 1 - (a + e)
                    agent.change_state("Im")
            elif agent.seir == "E":
                agent.change_state("Ia")
        elif agent.days_in_state == 10 and "I" in agent.seir:
            agent.change_state("R")
            agent.bedridden = False
        elif agent.days_in_state == 5 and agent.seir == "Ie": # After 5 days, agents in state Ie is bed-ridden and does not leave their room
            agent.bedridden = True
        agent.days_in_state += 1

def initialize_leaves(agents):
    """
    Initializes the leaves field for a given list of agents.\n
    All faculty are assigned to the Faculty Dining Leaf, while students are randomly distributed among the other 5 Dining Hall leaves.\n
    All students are randomly uniformly distributed among 100 unique social spaces for both the weekdays and the weekends.\n
    All students are randomly uniformly distributed among the 6 leaves of the Gym and Library.\n
    And finally, all faculty are randomly uniformly distributed among the 6 leaves of the Office spaces.\n
    """
    spaces = agents[0].leaves.keys() # Get the leaves field of the first agent, since all agents are initialized with an equivalent leaves field
    student_agents = [agent for agent in agents if agent.student]  # list of students
    for space in spaces:
        if space == "Dining Hall":
            random.shuffle(agents)
            for count, agent in enumerate(agents):
                if not agent.student:
                    agent.leaves[space] = SPACE_SUBSPACE_AMOUNT.get(space) - 1 # Assign all faculty to the faculty dining leaf
                else:
                    agent.leaves[space] = count % (SPACE_SUBSPACE_AMOUNT.get(space) - 1) # We cannot assign students to the last DH space, which is faculty dining
        elif space == "Social Space":
            random.shuffle(student_agents)
            for count, student in enumerate(student_agents):
                student.leaves[space][0] = count % SPACE_SUBSPACE_AMOUNT.get(space)
            random.shuffle(student_agents)
            # Only on-campus students can access a social space on the weekend
            for count, student in enumerate([student for student in student_agents if not student.off_campus]):
                student.leaves[space][1] = count % SPACE_SUBSPACE_AMOUNT.get(space)
        else:
            if space == "Office":
                stem_faculty = [agent for agent in agents if not agent.student and agent.division == "STEM"]
                humanities_faculty = [agent for agent in agents if not agent.student and agent.division == "Humanities"]
                arts_faculty = [agent for agent in agents if not agent.student and agent.division == "Arts"]
                for division_faculty in [stem_faculty, humanities_faculty, arts_faculty]:
                    random.shuffle(division_faculty)
                    for count, faculty in enumerate(division_faculty):
                        faculty.leaves[space] = count % SPACE_SUBSPACE_AMOUNT.get(space)
            else:  # Gym or Library space
                random.shuffle(student_agents)
                for count, student in enumerate(student_agents):
                    student.leaves[space] = count % SPACE_SUBSPACE_AMOUNT.get(space)
