from global_constants import TOTAL_AGENTS, SPACE_SUBSPACE_AMOUNT, PROBABILITY_E, PROBABILITY_A
import random

# n = 10  # number of agents
# n = 2380, on-campus: 1500, off-campus: 500, faculty: 380
n = TOTAL_AGENTS

vaccine_percentage = 0.5
face_mask_comp = 0.5
screening_comp = 0.5
type_ratio = [500/2380.0, 380/2380.0]  # proportion of ["Off-campus Students", "Faculty"] - default value is "On-campus Student"
major_ratio = [0.25, 0.25]  # proportion of ["Humanities", "Arts"] - default value is "STEM"
initial_infection = 10/2380.0  # proportion of students initially in the exposed state - should we make it number of students or a proportion?
social_ratio = 0.5  # proportion of students that are social

# ------------------------------------------------------------------------
class Agent:
    def initialize(self):
        # global agents
        agents = []
        for i in range(n):
            ag = Agent()
            #ag.vaccinated = 0  # vaccination status (0 = not vaccinated, 1 = vaccinated)
            ag.face_mask = 0  # face_mask compliance
            ag.screening = 0  # screening test compliance
            ag.type = "On-campus Student"
            ag.major = "STEM"  # agent subtype/major (either STEM, Humanities, or Arts)
            ag.seir = "S"  # agent infection states (either "S", "E", "Ia", "Im", "Ie", "R")
            ag.exposed_space = None # By default, agents do not have a space that exposed them
            ag.classes = []  # list of subspaces/classrooms
            ag.class_times = []  # list of [[day, time], major_index]
            ag.social = False  # default value is that an agent is not social
            ag.schedule = {"A": [None] * 15, "B": [None] * 15, "W": [None] * 15}  # time range is from 8 ~ 22, which is 15 blocks & class times are at index 2, 4, 6, 8
            ag.days_in_state = 0
            ag.bedridden = False
            ag.num_of_classes = 0
            # Initialize leaves - the first social space leaf is for A & B days and the second is for W days
            ag.leaves = {"Dining Hall": -1, "Library": -1, "Gym": -1, "Social Space": [-1, -1], "Office": -1}

            agents.append(ag)

        # VACCINATION: randomly select and assign vaccination to certain proportion of agents
        #select_vaccine = random.sample(agents, k=int(n * vaccine_percentage))
        #for ag in select_vaccine:
        #    ag.vaccinated = 1

        # FACE MASK COMPLIANCE: randomly select and assign face mask compliance to certain proportion of agents
        select_face_mask = random.sample(agents, k=int(n * face_mask_comp))
        for ag in select_face_mask:
            ag.face_mask = 1

        #  SCREENING TEST COMPLIANCE: randomly select and assign screening test compliance to certain proportion of agents
        select_screening = random.sample(agents, k=int(n * screening_comp))
        for ag in select_screening:
            ag.screening = 1

        # TYPE (ON-CAMPUS/OFF-CAMPUS/FACULTY): randomly select and assign a certain proportion of agents as "Off-campus Student" and "Faculty"
        select_type = random.sample(agents, k=int(n * (type_ratio[0] + type_ratio[1])))
        i = 0
        while i < (len(select_type) * (type_ratio[0] / (type_ratio[0] + type_ratio[1]))):
            select_type[i].type = "Off-campus Student"
            i += 1
        while i < len(select_type):
            select_type[i].type = "Faculty"
            i += 1

        # MAJOR (STEM/HUMANITIES/ARTS): randomly select and assign a certain proportion of agents as "Humanities" and "Arts"
        faculty_list = []
        student_list = []
        for ag in agents:
            if ag.type == "Faculty":
                faculty_list.append(ag)
            else:  # if agent is a student
                student_list.append(ag)

        select_major_faculty = random.sample(faculty_list, k=int(len(faculty_list) * (major_ratio[0] + major_ratio[1])))
        select_major_student = random.sample(student_list, k=int(len(student_list) * (major_ratio[0] + major_ratio[1])))
        select_major = [select_major_faculty, select_major_student]

        for select in select_major:
            i = 0
            while i < (len(select) * (major_ratio[0] / (major_ratio[0] + major_ratio[1]))):
                select[i].major = "Humanities"
                i += 1
            while i < len(select):
                select[i].major = "Arts"
                i += 1

        # INITIAL INFECTION: randomly select and assign agents that are initially infected
        #no_vaccine = []  # list of agents that haven't been vaccinated
        #for ag in agents:
        #    if ag.vaccinated == 0:
        #        no_vaccine.append(ag)
        select_seir = random.sample(agents, k=int(
            n * initial_infection))  # randomly select initial number of agents (that haven't been vaccinated)
        for ag in select_seir:
            ag.seir = random.choice(["Ia", "Im", "Ie"])  # randomly assign one of the infected states to agents

        select_social = random.sample(student_list, k=int(n * social_ratio))  # list of all social agents
        for ag in select_social:
            ag.social = True

        # print all agents and their attributes
        # for ag in agents:
            # print([ag.vaccinated, ag.face_mask, ag.screening, ag.type, ag.major, ag.seir, ag.social, ag.schedule])
            # print([ag.type, ag.major])

        initialize_leaves(agents)
        return agents

    def change_state(self, state):
        """
        Changes an agent seir field to state and also sets an agent's days_in_state field to 0
        """
        self.seir = state
        self.days_in_state = 0

    def get_major_index(self):
        """
        Returns a number, 0-2, representing the major of an agent.\n
        0 is returned if an agent is in the STEM major.\n
        1 is returned if an agent is in the Humanities major.\n
        2 is returned if an agent is in the Arts major.\n
        """
        if self.major == "STEM":
            return 0
        elif self.major == "Humanities":
            return 1
        else:  # self.major == "Arts"
            return 2

    def __str__(self):
        return 'Agent:' + self.type + '/' + self.major + '/' + self.seir

    def __repr__(self):
        return 'Agent:' + self.type + '/' + self.major + '/' + self.seir


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
         their division/major (STEM, Humanities, Arts), and their seir state (S, E, Ia, Im, Ie, R).\n
        """
        return 'Agent: ' + self.type + '/' + self.major + '/' + self.seir
    """
    def __repr__(self):
        return 'Agent:' + self.type + '/' + self.major + '/' + self.seir
    """
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
            for count, student in enumerate(student_agents):
                student.leaves[space][1] = count % SPACE_SUBSPACE_AMOUNT.get(space)
        else:
            if space == "Office":
                stem_faculty = [agent for agent in agents if agent.type == "Faculty" and agent.major == "STEM"]
                humanities_faculty = [agent for agent in agents if agent.type == "Faculty" and agent.major == "Humanities"]
                arts_faculty = [agent for agent in agents if agent.type == "Faculty" and agent.major == "Arts"]
                for major_faculty in [stem_faculty, humanities_faculty, arts_faculty]:
                    random.shuffle(major_faculty)
                    for count, faculty in enumerate(major_faculty):
                        faculty.leaves[space] = count % SPACE_SUBSPACE_AMOUNT.get(space)
            else:  # Gym or Library space
                random.shuffle(student_agents)
                for count, student in enumerate(student_agents):
                    student.leaves[space] = count % SPACE_SUBSPACE_AMOUNT.get(space)