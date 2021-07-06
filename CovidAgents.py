from global_constants import TOTAL_AGENTS, SPACE_SUBSPACE_AMOUNT, PROBABILITY_E, PROBABILITY_A
import random

# n = 10  # number of agents
# n = 2380, on-campus: 1500, off-campus: 500, faculty: 380
n = TOTAL_AGENTS

vaccine_percentage = 0.5
face_mask_comp = 0.5
screening_comp = 0.5
type_ratio = [0.21, 0.16]  # proportion of ["Off-campus Students", "Faculty"] - default value is "On-campus Student"
subtype_ratio = [0.25, 0.25]  # proportion of ["Humanities", "Arts"] - default value is "STEM"
initial_infection = 0.4  # proportion of students initially in the exposed state - should we make it number of students or a proportion?
social_ratio = 0.5  # proportion of students that are social

# ------------------------------------------------------------------------
class Agent:
    def initialize(self):
        # global agents
        agents = []
        for i in range(n):
            ag = Agent()
            ag.vaccinated = 0  # vaccination status (0 = not vaccinated, 1 = vaccinated)
            ag.face_mask = 0  # face_mask compliance
            ag.screening = 0  # screening test compliance
            ag.type = "On-campus Student"
            ag.subtype = "STEM"  # agent subtype/major (either STEM, Humanities, or Arts)
            ag.seir = "S"  # agent infection states (either "S", "E", "Ia", "Im", "Ie", "R")
            ag.days_in_state = 0
            ag.bedridden = False
            ag.schedule = {"A": [None] * 15, "B": [None] * 15, "W": [None] * 15}  # class times are at index 2, 4, 6, 8
            ag.num_of_classes = 0
            ag.social = "Not Social"
            # Initialize leaves - the first social space leaf is for A & B days and the second is for W days
            ag.leaves = {"Dining Hall": -1, "Library": -1, "Gym": -1, "Social Space": [-1, -1], "Office": -1}
            agents.append(ag)

        # VACCINATION: randomly select and assign vaccination to certain proportion of agents
        select_vaccine = random.sample(agents, k=int(n * vaccine_percentage))
        for ag in select_vaccine:
            ag.vaccinated = 1

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

        # SUBTYPE (STEM/HUMANITIES/ARTS): randomly select and assign a certain proportion of agents as "Humanities" and "Arts"
        select_subtype = random.sample(agents, k=int(n * (subtype_ratio[0] + subtype_ratio[1])))
        i = 0
        while i < (len(select_subtype) * (subtype_ratio[0] / (subtype_ratio[0] + subtype_ratio[1]))):
            select_subtype[i].subtype = "Humanities"
            i += 1
        while i < len(select_subtype):
            select_subtype[i].subtype = "Arts"
            i += 1

        # INITIAL INFECTION: randomly select and assign agents that are initially infected
        no_vaccine = []  # list of agents that haven't been vaccinated
        for ag in agents:
            if ag.vaccinated == 0:
                no_vaccine.append(ag)
        select_seir = random.sample(no_vaccine, k=int(n * initial_infection))  # randomly select initial number of agents (that haven't been vaccinated)
        for ag in select_seir:
                ag.seir = random.choice(["Ia", "Im", "Ie"])  # randomly assign one of the infected states to agents

        select_social = random.sample(agents, k=int(n * social_ratio))  # list of all social agents
        for ag in select_social:
            ag.social = "Social"
        initialize_leaves(agents)
        return agents

    def changeState(self, state):
        self.seir = state
        self.days_in_state = 0

    def get_major_index(self):
        if self.subtype == "STEM":
            return 0
        elif self.subtype == "Humanities":
            return 1
        else: # self.subtype == "Arts"
            return 2

    def get_available_hours(self, start_hour, end_hour, day):
        available_times = []
        for i in range(start_hour, end_hour + 1):
            if self.schedule.get(day)[i-8] == None:
                available_times.append(i-8)
        return available_times

    def __str__(self):
        return 'Agent: ' + self.type + '/' + self.subtype + '/' + self.seir

def change_states(agents):
    for agent in agents:
        if agent.days_in_state == 2:
            if agent.seir == "Ia":
                rand_num = random.random()
                if rand_num < PROBABILITY_E:
                    agent.changeState("Ie")
                elif rand_num < PROBABILITY_E + PROBABILITY_A:
                    agent.changeState("Ia")
                else: # An agent transitions from Ia -> Im with a probability 1 - (a + e)
                    agent.changeState("Im")
            elif agent.seir == "E":
                agent.changeState("Ia")
        elif agent.days_in_state == 10 and "I" in agent.seir:
            agent.changeState("R")
            agent.bedridden = False
        elif agent.days_in_state == 5 and agent.seir == "Ie": # After 5 days, agents in state Ie is bed-ridden and does not leave their room
            agent.bedridden = True

def initialize_leaves(agents):
    spaces = agents[0].leaves.keys()
    for space in spaces:
        random.shuffle(agents)
        if space == "Dining Hall":
            for count, agent in enumerate(agents):
                if agent.type == "Faculty":
                    agent.leaves[space] = SPACE_SUBSPACE_AMOUNT.get(space) - 1 # Assign all faculty to the faculty dining leaf
                else:
                    agent.leaves[space] = count % (SPACE_SUBSPACE_AMOUNT.get(space) - 1) # We cannot assign students to the last DH space, which is faculty dining
        elif space == "Social Space":
            for count, agent in enumerate(agents):
                agent.leaves[space][0] = count % SPACE_SUBSPACE_AMOUNT.get(space)
            random.shuffle(agents)
            for count, agent in enumerate(agents):
                agent.leaves[space][1] = count % SPACE_SUBSPACE_AMOUNT.get(space)
        else: # Gym, Library, Office spaces
            for count, agent in enumerate(agents):
                agent.leaves[space] = count % SPACE_SUBSPACE_AMOUNT.get(space)
