from global_constants import TOTAL_AGENTS, SPACE_SUBSPACE_AMOUNT, PROBABILITY_E, PROBABILITY_A,\
    FACE_MASK_LEVEL, FALSE_POSITIVE_RATE, FALSE_NEGATIVE_RATE, FACE_MASK_COMPLIANCE, TYPE_RATIO, DIVISION_RATIO, \
    INITIAL_INFECTION_PROPORTION, SOCIAL_RATIO, WALK_IN_PROBABILITY
import random
import pickle

n = TOTAL_AGENTS  # n = 2380, on-campus: 1500, off-campus: 500, faculty: 380


class Agent:
    def initialize(self):
        caCV = pickle.load(open('pickle_files/covid_variants.p', 'rb'))
        covid_variant = [key for key in caCV[0].keys() if caCV[0].get(key) is True][0]
        vaccine_self = caCV[2][0].get(covid_variant)
        vaccine_spread = caCV[2][1].get(covid_variant)
        face_mask_self = caCV[3][0].get(covid_variant)
        face_mask_spread = caCV[3][1].get(covid_variant)
        caI = pickle.load(open('pickle_files/interventions.p', 'rb'))
        caVP = pickle.load(open('pickle_files/vaccine_percentage.p', 'rb'))
        vaccine_intervention = caI.get("Vaccine")  # whether we use vaccine intervention or not ("on" or "off")
        faculty_vaccine_percentage = caVP.get("Faculty")
        student_vaccine_percentage = caVP.get("Student")
        face_mask_intervention = caI.get("Face mask")  # whether we use face mask intervention or not ("on" or "off")
        # global agents
        agents = []
        for i in range(TOTAL_AGENTS):
            ag = Agent()
            ag.vaccinated = False  # vaccination status (0 = not vaccinated, 1 = vaccinated)
            ag.vaccinated_self_risk_multiplier = 1
            ag.vaccinated_spread_risk_multiplier = 1
            ag.face_mask = False  # face_mask compliance
            ag.face_mask_self_risk_multiplier = {"Dorm": 1, "Academic": 1, "DiningHall": 1, "Gym": 1, "Library": 1, "Office": 1,
                                                 "SocialSpace": 1, "TransitSpace": 1, "LargeGatherings": 1}
            ag.face_mask_spread_risk_multiplier = {"Dorm": 1, "Academic": 1, "DiningHall": 1, "Gym": 1, "Library": 1, "Office": 1,
                                                   "SocialSpace": 1, "TransitSpace": 1, "LargeGatherings": 1}
            # ag.screening = False  # screening test compliance
            ag.screening_result = []  # result of screening test - whether agent is infected or not

            ag.type = "On-campus Student"
            ag.division = "STEM"  # agent subtype/division (either STEM, Humanities, or Arts)
            ag.seir = "S"  # agent infection states (either "S", "E", "Ia", "Im", "Ie", "R")
            ag.exposed_space = None  # By default, agents do not have a space that exposed them
            ag.class_times = []  # list of [[day, time], division_index]
            ag.social = False  # default value is that an agent is not social
            ag.schedule = {"A": [None] * 15, "B": [None] * 15, "W": [None] * 15}  # time range is from 8 ~ 22, which is 15 blocks & class times are at index 2, 4, 6, 8
            ag.days_in_state = 0
            ag.bedridden = False
            ag.bedridden_days = False  # by default, agents are not quarantined
            ag.num_of_classes = 0
            # Initialize leaves - the first social space leaf is for A & B days and the second is for W days
            ag.leaves = {"Dining Hall": -1, "Library": -1, "Gym": -1, "Social Space": [-1, -1], "Office": -1}

            agents.append(ag)


        # TYPE (ON-CAMPUS/OFF-CAMPUS/FACULTY): randomly select and assign a certain proportion of agents as "Off-campus Student" and "Faculty"
        select_type = random.sample(agents, k=int(TOTAL_AGENTS * (TYPE_RATIO[0] + TYPE_RATIO[1])))
        i = 0
        while i < (len(select_type) * (TYPE_RATIO[0] / (TYPE_RATIO[0] + TYPE_RATIO[1]))):
            select_type[i].type = "Off-campus Student"
            i += 1
        while i < len(select_type):
            select_type[i].type = "Faculty"
            i += 1


        # VACCINATION: randomly select and assign vaccination to certain proportion of student/faculty agents
        if vaccine_intervention is True:
            student_agents = [agent for agent in agents if agent.type != "Faculty"]
            faculty_agents = [agent for agent in agents if agent.type == "Faculty"]
            select_vaccine_student = random.sample(student_agents, k=int(len(student_agents) * student_vaccine_percentage))
            select_vaccine_faculty = random.sample(faculty_agents, k=int(len(faculty_agents) * faculty_vaccine_percentage))
            for ag in agents:
                if ag in select_vaccine_student or ag in select_vaccine_faculty:
                    ag.vaccinated = True
                    ag.vaccinated_self_risk_multiplier = (1 - vaccine_self)
                    ag.vaccinated_spread_risk_multiplier = (1 - vaccine_spread)


        # FACE MASK COMPLIANCE: randomly select and assign face mask compliance to certain proportion of agents
        if face_mask_intervention is True:

            # version that follows paper (all agents need to wear face masks in certain spaces, and in the remaining spaces the )
            if FACE_MASK_LEVEL == "only unvaccinated":
                unvaccinated = [ag for ag in agents if ag.vaccinated is False]
                select_face_mask = random.sample(unvaccinated, k=int(len(unvaccinated) * FACE_MASK_COMPLIANCE))
            else:  # if FACE_MASK_LEVEL == "all":
                select_face_mask = random.sample(agents, k=int(TOTAL_AGENTS * FACE_MASK_COMPLIANCE))

            for ag in agents:
                if ag in select_face_mask:  # agents that comply with face masks
                    ag.face_mask = True
                    for key in ag.face_mask_self_risk_multiplier.keys():
                        ag.face_mask_self_risk_multiplier[key] = (1 - face_mask_self)
                        ag.face_mask_spread_risk_multiplier[key] = (1 - face_mask_spread)

                else:  # agents that don't comply with face masks (don't wear in social space, large gatherings, dorm cores, etc.)
                    for key in ag.face_mask_self_risk_multiplier.keys():
                        if key in ["Academic", "DiningHall", "Gym", "Library", "Office", "TransitSpace"]:
                            ag.face_mask_self_risk_multiplier[key] = (1 - face_mask_self)
                            ag.face_mask_spread_risk_multiplier[key] = (1 - face_mask_spread)

            """
            # version that may be more realistic (non-compliant agents do not wear face masks in any space)
            select_face_mask = random.sample(agents, k=int(TOTAL_AGENTS * FACE_MASK_COMPLIANCE))

            for ag in select_face_mask:
                ag.face_mask = True
                for key in ag.face_mask_self_risk_multiplier.keys():
                    ag.face_mask_self_risk_multiplier[key] = 1 - face_mask_self
                    ag.face_mask_spread_risk_multiplier[key] = 1 - face_mask_spread
            """










        # DIVISION (STEM/HUMANITIES/ARTS): randomly select and assign a certain proportion of agents as "Humanities" and "Arts"
        faculty_list = []
        student_list = []
        for ag in agents:
            if ag.type == "Faculty":
                faculty_list.append(ag)
            else:  # if agent is a student
                student_list.append(ag)

        select_division_faculty = random.sample(faculty_list, k=int(len(faculty_list) * (DIVISION_RATIO[0] + DIVISION_RATIO[1])))
        select_division_student = random.sample(student_list, k=int(len(student_list) * (DIVISION_RATIO[0] + DIVISION_RATIO[1])))
        select_division = [select_division_faculty, select_division_student]

        for select in select_division:
            i = 0
            while i < (len(select) * (DIVISION_RATIO[0] / (DIVISION_RATIO[0] + DIVISION_RATIO[1]))):
                select[i].division = "Humanities"
                i += 1
            while i < len(select):
                select[i].division = "Arts"
                i += 1

        # INITIAL INFECTION: randomly select and assign agents that are initially infected
        select_seir = random.sample([agent for agent in agents if agent.vaccinated is False], k=int(TOTAL_AGENTS * INITIAL_INFECTION_PROPORTION))  # randomly select initial number of agents (that haven't been vaccinated)
        for ag in select_seir:
            ag.seir = random.choice(["Ia", "Im", "Ie"])  # randomly assign one of the infected states to agents

        # SOCIAL: randomly select and assign student agents as social, which allows them to go to large gatherings
        select_social = random.sample(student_list, k=int(TOTAL_AGENTS * SOCIAL_RATIO))  # list of all social agents
        for ag in select_social:
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

    def __repr__(self):
        return 'Agent:' + self.type + '/' + self.division + '/' + self.seir


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
            if self.schedule.get(day)[i-8] is None:
                available_times.append(i-8)
        return available_times


    def __str__(self):
        """
        Returns a string representation of an agent with their type (On campus student, Off campus student, Faculty),
         their division/division (STEM, Humanities, Arts), and their seir state (S, E, Ia, Im, Ie, R).\n
        """
        return 'Agent: ' + self.type + '/' + self.division + '/' + self.seir


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
        if agent.bedridden_days is not False:  # if agent is in quarantine
            if agent.bedridden_days == 14:  # after 14 days, agent get out of quarantine
                agent.bedridden = False  # in whatever state the agent was, after 14 days the agent will be either susceptible or recovered, so we don't need to change their state
                agent.bedridden_days = False
            elif agent.bedridden_days < 14:
                agent.bedridden_days += 1

        if agent.days_in_state == 2:
            if agent.seir == "Ia":
                rand_num = random.random()
                if rand_num < PROBABILITY_E:
                    agent.change_state("Ie")
                elif rand_num < PROBABILITY_E + PROBABILITY_A:
                    agent.change_state("Ia")
                else:  # An agent transitions from Ia -> Im with a probability 1 - (a + e)
                    agent.change_state("Im")
            elif agent.seir == "E":
                agent.change_state("Ia")
        elif agent.days_in_state == 10 and "I" in agent.seir:
            agent.change_state("R")
            agent.bedridden = False
        elif agent.days_in_state == 5 and agent.seir == "Ie":  # After 5 days, agents in state Ie is bed-ridden and does not leave their room
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
    student_agents = [agent for agent in agents if agent.type == "On-campus Student" or agent.type == "Off-campus Student"]  # list of students
    for space in spaces:
        if space == "Dining Hall":
            random.shuffle(agents)
            for count, agent in enumerate(agents):
                if agent.type == "Faculty":
                    agent.leaves[space] = SPACE_SUBSPACE_AMOUNT.get(space) - 1 # Assign all faculty to the faculty dining leaf
                else:
                    agent.leaves[space] = count % (SPACE_SUBSPACE_AMOUNT.get(space) - 1) # We cannot assign students to the last DH space, which is faculty dining
        elif space == "Social Space":
            random.shuffle(student_agents)
            for count, student in enumerate(student_agents):
                student.leaves[space][0] = count % SPACE_SUBSPACE_AMOUNT.get(space)
            random.shuffle(student_agents)
            # Only on-campus students can access a social space on the weekend
            for count, student in enumerate([student for student in student_agents if student.type == "On-campus Student"]):
                student.leaves[space][1] = count % SPACE_SUBSPACE_AMOUNT.get(space)
        else:
            if space == "Office":
                stem_faculty = [agent for agent in agents if agent.type == "Faculty" and agent.division == "STEM"]
                humanities_faculty = [agent for agent in agents if agent.type == "Faculty" and agent.division == "Humanities"]
                arts_faculty = [agent for agent in agents if agent.type == "Faculty" and agent.division == "Arts"]
                for division_faculty in [stem_faculty, humanities_faculty, arts_faculty]:
                    random.shuffle(division_faculty)
                    for count, faculty in enumerate(division_faculty):
                        faculty.leaves[space] = count % SPACE_SUBSPACE_AMOUNT.get(space)
            else:  # Gym or Library space
                random.shuffle(student_agents)
                for count, student in enumerate(student_agents):
                    student.leaves[space] = count % SPACE_SUBSPACE_AMOUNT.get(space)


def screening_test(agents):
    for agent in agents:
        rand_num = random.random()
        if agent.seir in ["S", "E", "R"]:
            if rand_num < FALSE_POSITIVE_RATE:
                agent.screening_result.append("Positive")
            else:
                agent.screening_result.append("Negative")
        elif agent.seir in ["Ia", "Im", "Ie"]:
            if rand_num < FALSE_NEGATIVE_RATE:
                agent.screening_result.append("Negative")
            else:
                agent.screening_result.append("Positive")


def return_screening_result(agents):
    for agent in agents:
        if agent.screening_result[-1] == "Positive":
            agent.bedridden = True
            agent.bedridden_days = 0
        elif agent.screening_result[-1] == "Negative" and agent.bedridden is True:  # if a walk-in test agent received a negative result
            agent.bedridden = False
            agent.bedridden_days = False


def walk_in_test(agents):
    infected_agents = [agent for agent in agents if agent.seir in ["Ie", "Im"]]
    walk_in_agents = []

    for agent in infected_agents:
        if agent.days_in_state < 1 and agent.bedridden is False:
            # k = agent.days_in_state
            rand_num = random.random()
            if rand_num < WALK_IN_PROBABILITY.get(agent.seir):
                walk_in_agents.append(agent)

    screening_test(walk_in_agents)

    for agent in walk_in_agents:
        agent.bedridden = True
        agent.bedridden_days = 0





