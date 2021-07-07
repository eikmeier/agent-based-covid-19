from global_constants import PASSING_TIME, TOTAL_AGENTS, SPACE_CAPACITIES, SPACE_RISK_MULTIPLIERS, \
    SUBSPACE_CAPACITIES, SUBSPACE_RISK_MULTIPLIERS, ACADEMIC_SUBSPACE_CAPACITIES, ACADEMIC_SPACE_CAPACITIES, \
    CLASSROOMS, ACADEMIC_SUBSPACE_SEATS, SPACE_SUBSPACE_AMOUNT, TUNING_PARAMETER
import math
import random

class Space:
    def close_space(self):
        """
        Close a space, setting CV, RV, and numberAssigned to 0.
        """
        self.cv = 0
        self.rv = 0
        self.numberAssigned = 0


class Dorm(Space):
    general_counter = 0
    def __init__(self, size):
        """
        Initialize a dorm space with a size (must be "Small," "Medium," or "Large")\n
        The dorm space will then be given a cv and rv field\n
        Additionally, the space will get a singles field and a doubles field which are a list of the subspaces
         of this particular space. Each of these fields will have subspace dorms created and an agent field declared
         for each element of the list. \n
        Finally, the space has an occupiedSingles field and an occupiedDoubles field that counts how many of
         the rooms have already been assigned to agent(s).\n
        """
        self.status = "Available"
        self.size = size
        self.rv = SPACE_RISK_MULTIPLIERS.get("Dorm")
        if self.size == "Small":
            self.cv = PASSING_TIME * 15
            self.singles = [None] * 5
            self.doubles = [None] * 5
        elif self.size == "Medium":
            self.cv = PASSING_TIME * 45
            self.singles = [None] * 15
            self.doubles = [None] * 15
        elif self.size == "Large":
            self.cv = PASSING_TIME * 75
            self.singles = [None] * 25
            self.doubles = [None] * 25

        for i in range(len(self.singles)):
            self.singles[i] = SubSpace(self, 1, SUBSPACE_RISK_MULTIPLIERS.get("Dorm"))
            self.singles[i].id = random.random()
            self.singles[i].agent = None
        for j in range(len(self.doubles)):
            self.doubles[j] = SubSpace(self, 2, SUBSPACE_RISK_MULTIPLIERS.get("Dorm"))
            self.doubles[j].id = random.random()
            self.doubles[j].agents = [None, None]

        self.occupiedSingles = 0
        self.occupiedDoubles = 0

    def __str__(self):
        return 'Dorm of size ' + self.size
        #return 'Dorm #' + str(self.id)

    def assign_agent(self, agent):
        """
        Assign an agent to this dorm space.\n
        First, any unoccupied singles in the space will be assigned to the agent.\n
        Next, any double that is not fully occupied will be assigned to the agent.\n
        Finally, if there are no available singles or doubles in the dorm space, then
         the entire dorm space is occupied. In this case, the function returns False
         to indicate an agent was not assigned.\n
        Otherwise, if an agent is assigned, their room is returned in the function.\n
        """

        if self.occupiedSingles < len(self.singles):
            self.singles[self.occupiedSingles].agent = agent
            self.occupiedSingles += 1
            return self.singles[self.occupiedSingles - 1]
        elif self.occupiedDoubles < len(self.doubles):
            if self.doubles[self.occupiedDoubles].agents[0] is None:
                self.doubles[self.occupiedDoubles].agents[0] = agent
            else:
                self.doubles[self.occupiedDoubles].agents[1] = agent
                self.occupiedDoubles += 1
            return self.doubles[self.occupiedDoubles - 1]
        else:  # Return False if there are no rooms available
            self.status = "Full"

class TransitSpace(Space):
    def __init__(self):
        """
        Initialize a Transit Space.\n
        The Transit Space will be given a cv and an rv field which are both pre-defined in global_constants.py\n
        """
        self.cv = SPACE_CAPACITIES.get("Transit Space")
        self.rv = SPACE_RISK_MULTIPLIERS.get("Transit Space")

    def __str__(self):
        return 'Transit Space'

class DiningHall(Space):
    def __init__(self, day, time):
        """
        Initialize a Dining Hall space.\n
        The Dining Hall space will be given a cv and rv which are both pre-defined in global_constants.py\n
        Additionally, the Dining Hall will be given 6 subspaces in a leaves field, the last subspace being
         the Faculty Dining Leaf. Each of these leaves will be given the pre-defined cv and rv fields as given
         in global_constants.py\n
        """
        self.day = day
        self.time = time
        self.cv = SPACE_CAPACITIES.get("Dining Hall")
        self.rv = SPACE_RISK_MULTIPLIERS.get("Dining Hall")
        self.leaves = [SubSpace(self, SUBSPACE_CAPACITIES.get("Dining Hall"),
                                SUBSPACE_RISK_MULTIPLIERS.get("Dining Hall"))] * 5
        self.leaves.append(SubSpace(self, SUBSPACE_CAPACITIES.get("Faculty Dining Leaf"),
                                    SUBSPACE_RISK_MULTIPLIERS.get("Faculty Dining Leaf")))

    def assign_agent(self, agent):
        self.leaves[agent.leaves.get("Dining Hall")].agents.append(agent)
        agent.schedule.get(self.day)[self.time] = "Dining Hall"

    def __str__(self):
        return 'Dining Hall'

class Library(Space):
    def __init__(self, day, time):
        """
        Initialize a Library Space.\n
        The Library will be given a cv and an rv field which are both pre-defined in global_constants.py\n
        Additionally, the Library will get a leaves field which is a list of 6 subspaces of the Library, each of the subspaces
         with a cv and rv field that is pre-defined in global_constants.py\n
        """
        self.day = day
        self.time = time
        self.cv = SPACE_CAPACITIES.get("Library")
        self.rv = SPACE_RISK_MULTIPLIERS.get("Library")
        self.leaves = [SubSpace(self, SUBSPACE_CAPACITIES.get("Library"), SUBSPACE_RISK_MULTIPLIERS.get("Library"))] * SPACE_SUBSPACE_AMOUNT.get("Library")

    def assign_agent(self, agent):
        self.leaves[agent.leaves.get("Library")].agents.append(agent)
        agent.schedule.get(self.day)[self.time] = "Library"

    def __str__(self):
        return 'Library'

class Gym(Space):
    def __init__(self, day, time):
        """
        Initialize a Gym Space.\n
        The Gym will be given a cv and an rv field which are both pre-defined in global_constants.py\n
        Additionally, the Gym will get a leaves field which is a list of 6 subspaces of the Gym, each of the subspaces
         with a cv and rv field that is pre-defined in global_constants.py\n
        """
        self.cv = SPACE_CAPACITIES.get("Gym")
        self.rv = SPACE_RISK_MULTIPLIERS.get("Gym")
        self.leaves = [SubSpace(self, SUBSPACE_CAPACITIES.get("Gym"), SUBSPACE_RISK_MULTIPLIERS.get("Gym"))] * SPACE_SUBSPACE_AMOUNT.get("Gym")
        self.day = day
        self.time = time

    def assign_agent(self, agent):
        self.leaves[agent.leaves.get("Gym")].agents.append(agent)
        agent.schedule.get(self.day)[self.time] = "Gym"

    def __str__(self):
        return 'Gym'

class Office(Space):
    def __init__(self, division, day, time):
        """
        Initialize an Office Space with a given division (must be either "STEM," "Humanities," or "Arts").\n
        The Gym will be given a cv field based on the division the Office space is in and an rv that is pre-defined in
         global_constants.py\n
        Additionally, the Office will get a leaves field which is a list of 6 subspaces of the Office, each of the subspaces
         with a cv that is based on the division the Office space is in and and an rv field that is pre-defined in
         global_constants.py\n
        """
        self.division = division
        self.day = day
        self.time = time
        if self.division == "STEM":
            self.cv = PASSING_TIME * 6 * 50
            self.subcv = 50
        elif self.division in {"Humanities", "Arts"}:
            self.cv = PASSING_TIME * 6 * 25
            self.subcv = 20
        self.rv = SPACE_RISK_MULTIPLIERS.get("Office")
        self.leaves = [SubSpace(self, self.subcv, SUBSPACE_RISK_MULTIPLIERS.get("Office"))] * SPACE_SUBSPACE_AMOUNT.get("Office")

    def assign_agent(self, agent):
        self.leaves[agent.leaves.get("Office")].agents.append(agent)
        agent.schedule.get(self.day)[self.time] = "Office"

    def __str__(self):
        return self.division + ' Office'

class LargeGatherings(Space):
    def __init__(self):
        """
        Initialize a Large Gatherings space.\n
        The Large Gatherings space will be given an rv field which is pre-defined in global_constants.py\n
        Additionally, the Large Gatherings space will be given a cv field and a numberAssigned field, both initialized to 0.\n
        Finally, the Large Gatherings space will also initialize an agents field as an empty list.\n
        """
        self.cv = 0
        self.numberAssigned = 0
        self.rv = SPACE_RISK_MULTIPLIERS.get("Large Gatherings")
        self.agents = []

    def __str__(self):
        return 'Large Gatherings'

    def assign_agent(self, agent):
        """
        Assign an agent to the Large Gatherings space.\n
        The numberAssigned field of the space will be increased by one and the cv field will be
         re-calculated as a result of the new agent added to the space.\n
        Additionally, the agent will be appended to the agents field of the space.\n
        """
        self.numberAssigned += 1
        self.cv = 40 * math.ceil(self.numberAssigned / 40.0)
        self.agents.append(agent)

class Academic(Space):
    def __init__(self, size, major, day, time):
        """
        Initialize an Academic space with a size (must be "Small," "Medium," or "Large")\n
        The Academic space will then be given a cv field, based on the given size field\n
        Additionally, the Academic Space will be given an rv field as pre-defined in global_constants.py\n
        Finally, the Academic Space is given a classrooms field that is a list of all the subspaces of classrooms.\n
         A small Academic space will have 3 small classrooms.\n
         A medium Academic space will have 2 small classrooms and 3 medium classrooms.\n
         A large Academic space will have 5 small classrooms, 3 medium classrooms, and 3 large classrooms.\n
        Each of these elements of the classrooms field has a cv field and rv field which is pre-defined in global_constants.py\n
        """

        self.size = size
        self.day = day
        self.time = time
        self.cv = ACADEMIC_SPACE_CAPACITIES.get(self.size)
        self.rv = SPACE_RISK_MULTIPLIERS.get("Academic")
        self.classrooms = []
        self.major = major
        self.status = "Available"

        for i in range(CLASSROOMS.get(self.size)[0]): # Insert small classrooms
            self.classrooms.append(SubSpace(self, ACADEMIC_SUBSPACE_CAPACITIES.get("Small"), SUBSPACE_RISK_MULTIPLIERS.get("Classroom")))
            self.classrooms[i].seats = ACADEMIC_SUBSPACE_SEATS.get("Small")
            self.classrooms[i].faculty = None

        for j in range(CLASSROOMS.get(self.size)[1]): # Insert medium classrooms
            self.classrooms.append(SubSpace(self, ACADEMIC_SUBSPACE_CAPACITIES.get("Medium"), SUBSPACE_RISK_MULTIPLIERS.get("Classroom")))
            self.classrooms[j + CLASSROOMS.get(self.size)[0]].seats = ACADEMIC_SUBSPACE_SEATS.get("Medium")
            self.classrooms[j + CLASSROOMS.get(self.size)[0]].faculty = None

        for k in range(CLASSROOMS.get(self.size)[2]): # Insert large classrooms
            self.classrooms.append(SubSpace(self, ACADEMIC_SUBSPACE_CAPACITIES.get("Large"), SUBSPACE_RISK_MULTIPLIERS.get("Classroom")))
            self.classrooms[k + CLASSROOMS.get(self.size)[0] + + CLASSROOMS.get(self.size)[1]].seats = ACADEMIC_SUBSPACE_SEATS.get("Large")
            self.classrooms[k + CLASSROOMS.get(self.size)[0] + + CLASSROOMS.get(self.size)[1]].faculty = None


    def __str__(self):
        return 'Academic building: ' + self.size + '/' + self.day + '/' + str(self.time)

    def assign_agent(self, agent):
        # Put the class (for two hours) into the agent's schedule
        if agent.type == "Faculty":
            classroom = self.assign_faculty(agent)
        else:
            classroom = self.assign_student(agent)
        if classroom != None:
            agent.num_of_classes += 1
            # agent.schedule.get(self.day)[self.time] = "Class"
            # agent.schedule.get(self.day)[self.time + 1] = "Class"
        return classroom


    def assign_faculty(self, agent):
        for classroom in self.classrooms:
            if len(classroom.agents) == 0:  # classroom.faculty is None:  # if there is no assigned faculty yet
                classroom.faculty = agent
                classroom.agents.append(agent)
                classroom.status = "Faculty assigned"

                if all(classroom.status == "Faculty assigned" for classroom in self.classrooms):  # if all classes have faculty assigned
                    self.status = "All classes have assigned faculty"
                return classroom
            else:  # if there is an assigned faculty in the current classroom already
                continue  # move onto next classroom in the list
        return None


    def assign_student(self, agent):  # academic = academic building (Academic class) / classroom = SubSpace within Academic.classrooms
        random.shuffle(self.classrooms)
        for classroom in self.classrooms:
            if len(classroom.agents) < (classroom.seats + 1):  # if there are available seats in the classroom (should have +1 because it includes faculty)
                classroom.agents.append(agent)

                if len(classroom.agents) == (classroom.seats + 1):  # if classroom becomes full after assigning the current agent, change classroom.status to "Full"
                    classroom.status = "Full"
                if all(room.status == "Full" for room in self.classrooms):  # if all the classrooms in the building are full, change academic building status to "Full"
                    self.status = "Full"
                return classroom
            else:  # when classroom is full (no more seats)
                continue


"""
    def assignStudent(self, agent):  # academic = academic building (Academic class) / classroom = SubSpace within Academic.classrooms
        random.shuffle(self.classrooms)
        for classroom in self.classrooms:
            if len(classroom.agents) <= classroom.seats and agent.schedule.get(self.day)[self.time] == None:
                classroom.agents.append(agent)
                return classroom
        return None

    def assignFaculty(self, agent):
        for classroom in self.classrooms: 
            if classroom.faculty is None: # if there is no assigned faculty yet, assign agent to classroom
                classroom.agents.append(agent)
                classroom.faculty = agent
                return classroom
        return None
"""
class SocialSpace(Space):
    def __init__(self, day, time):
        """
        Initialize a Social Space.\n
        The Social Space only has a leaves field, a list of 100 subspaces each initialized with a cv and rv field that is pre-defined in
         global_constants.py. The space itself does not have a cv or rv because the core social space has no actual meaning.\n
        """
        self.leaves = [SubSpace(self, SUBSPACE_CAPACITIES.get("Social Space"),
                                SUBSPACE_RISK_MULTIPLIERS.get("Social Space"))] * SPACE_SUBSPACE_AMOUNT.get("Social Space")
        self.day = day
        self.time = time

    def assign_agent(self, agent):
        if self.day == 2:
            self.leaves[agent.leaves.get("Social Space")[1]].agents.append(agent)
            agent.schedule.get(self.day)[self.time] = "Social Space"
        else:
            self.leaves[agent.leaves.get("Social Space")[0]].agents.append(agent)
            agent.schedule.get(self.day)[self.time] = "Social Space"

    def __str__(self):
        return 'Social Space'

class OffCampus(Space):
    def __init__(self, day, time):
        """
        Initialize an Off Campus Space.\n
        The Off Campus Space only has a list of agents, as it has no leaves or a defined capacity or risk multiplier.\n
        """
        self.agents = []
        self.day = day
        self.time = time
    
    def assign_agent(self, agent):
        self.agents.append(agent)
        agent.schedule.get(self.day)[self.time] = "Off-Campus Space"

class SubSpace():
    def __init__(self, space, cv, rv):
        """
        Initialize a subspace with a given parent space, the cv of the subspace, and the rv of the subspace.\n
        Parent space must be either a dorm, a transit space, a dining hall, a library, a gym, an office,
         a large gatherings space, an academic space, or a social space.\n
        """
        self.space = space
        self.cv = cv
        self.rv = rv

        """I added this - status of whether space is available/full & the list of agents in the space"""
        self.status = "Available"
        self.agents = []

    def __str__(self):
        return 'Subspace of cv:' + str(self.cv) + " of " + self.space.__str__()
        # return 'Subspace of ' + self.space.__str__()

    def __repr__(self):
        return 'Subspace of cv:' + str(self.cv) + " of " + self.space.__str__()

    def close_subspace(self):
        """
        Close a subspace, setting CV, RV, and numberAssigned to 0.
        """
        self.cv = 0
        self.rv = 0
        self.numberAssigned = 0

    def get_agents(self):
        result = []
        for agent in self.agents:
            if agent.bedridden == False: # Bed-ridden agents stay in their room and do not follow the schedule
                result.append(agent)
        return result

    def get_space(self):
        """
        Return the space that contains this subspace
        """
        return self.space

    def get_infected(self):
        """
        Return the number of infected agents in this subspace
        """
        n = 0
        for agent in self.agents:
            if agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie":
                n += 1
        return n

    def get_agents(self, state):
        result = []
        for agent in self.agents:
            if agent.seir == state:
                result.append(agent)
        return result

    def get_infection_prob(self):
        return self.rv * ((len(self.get_agents("Ie")) + len(self.get_agents("Im")) + 0.5 * len(self.get_agents("Ia")))
                           / self.cv) * TUNING_PARAMETER

    def spread_infection(self):
        susceptible_agents = [agent for agent in self.agents if agent.seir == "S"]
        infection_prob = self.get_infection_prob() / 100.0
        for agent in susceptible_agents:
            rand_num = random.random()
            if rand_num < infection_prob: # Agent is now exposed
                agent.change_state("E")


# ***Below are some notes that need to be addressed, along with some notes for future reference***

"""
** Problems (or so-called problems, more like a running list of stuff for Erik to reference) with the code to fix:
 1. Add in functionality to add agents to spaces (move from spaces to subspaces and vice versa as well...)
 2. Consider adding in closing spaces (gym/library/dining hall/large gatherings) based on h? Or to have this elsewhere
"""

# Our network has one gym, one library, one dining hall, and three faculty offices.

# We close the gym, library, and dining hall with h = 0.50 and h = 1
# h = 0.50, close gym and library
# h = 0.75, close gym, library, dining hall, and large gatherings
# h = 1, close gym, library, dining hall, office, and large gatherings

# If L/DH are closed, time spent at space is replaced with student's dorm or off-campus
# When facing a building closure, faculties spend that time in their
#  office instead
# When O are closed, we assume faculty only spend time in the classes they teach

# Some abbreviations used in the paper
# D - Dorm, DH - Dining Hall, Ci - ith class,
# S - Social Space, L - Library, G - Gym,
# OC - Off Campus, O - Office
