from global_constants import PASSING_TIME, TOTAL_AGENTS, SPACE_CAPACITIES, SPACE_RISK_MULTIPLIERS, \
    SUBSPACE_CAPACITIES, SUBSPACE_RISK_MULTIPLIERS, ACADEMIC_SUBSPACE_CAPACITIES, ACADEMIC_SPACE_CAPACITIES, \
    CLASSROOMS, ACADEMIC_SUBSPACE_SEATS
import math
import random

class Space:
    def closeSpace(self):
        """
        Close a space, setting CV, RV, and numberAssigned to 0.
        """
        self.cv = 0
        self.rv = 0
        self.numberAssigned = 0


class Dorm(Space):
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
            self.singles[i].agent = None
        for j in range(len(self.doubles)):
            self.doubles[j] = SubSpace(self, 2, SUBSPACE_RISK_MULTIPLIERS.get("Dorm"))
            self.doubles[j].agents = [None, None]

        self.occupiedSingles = 0
        self.occupiedDoubles = 0

    def __str__(self):
        return 'Dorm of size ' + self.size

    def assignAgent(self, agent):
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
    def __init__(self):
        """
        Initialize a Dining Hall space.\n
        The Dining Hall space will be given a cv and rv which are both pre-defined in global_constants.py\n
        Additionally, the Dining Hall will be given 6 subspaces in a leaves field, the last subspace being
         the Faculty Dining Leaf. Each of these leaves will be given the pre-defined cv and rv fields as given
         in global_constants.py\n
        """
        self.cv = SPACE_CAPACITIES.get("Dining Hall")
        self.rv = SPACE_RISK_MULTIPLIERS.get("Dining Hall")
        self.leaves = [SubSpace(self, SUBSPACE_CAPACITIES.get("Dining Hall"),
                                SUBSPACE_RISK_MULTIPLIERS.get("Dining Hall"))] * 5
        self.leaves.append(SubSpace(self, SUBSPACE_CAPACITIES.get("Faculty Dining Leaf"),
                                    SUBSPACE_RISK_MULTIPLIERS.get("Faculty Dining Leaf")))
    def __str__(self):
        return 'Dining Hall'

class Library(Space):
    def __init__(self):
        """
        Initialize a Library Space.\n
        The Library will be given a cv and an rv field which are both pre-defined in global_constants.py\n
        Additionally, the Library will get a leaves field which is a list of 6 subspaces of the Library, each of the subspaces
         with a cv and rv field that is pre-defined in global_constants.py\n
        """
        self.cv = SPACE_CAPACITIES.get("Library")
        self.rv = SPACE_RISK_MULTIPLIERS.get("Library")
        self.leaves = [SubSpace(self, SUBSPACE_CAPACITIES.get("Library"), SUBSPACE_RISK_MULTIPLIERS.get("Library"))] * 6

    def __str__(self):
        return 'Library'

class Gym(Space):
    def __init__(self):
        """
        Initialize a Gym Space.\n
        The Gym will be given a cv and an rv field which are both pre-defined in global_constants.py\n
        Additionally, the Gym will get a leaves field which is a list of 6 subspaces of the Gym, each of the subspaces
         with a cv and rv field that is pre-defined in global_constants.py\n
        """
        self.cv = SPACE_CAPACITIES.get("Gym")
        self.rv = SPACE_RISK_MULTIPLIERS.get("Gym")
        self.leaves = [SubSpace(self, SUBSPACE_CAPACITIES.get("Gym"), SUBSPACE_RISK_MULTIPLIERS.get("Gym"))] * 6

    def __str__(self):
        return 'Gym'

class Office(Space):
    def __init__(self, division):
        """
        Initialize an Office Space with a given division (must be either "STEM," "Humanities," or "Arts").\n
        The Gym will be given a cv field based on the division the Office space is in and an rv that is pre-defined in
         global_constants.py\n
        Additionally, the Gym will get a leaves field which is a list of 6 subspaces of the Office, each of the subspaces
         with a cv that is based on the division the Office space is in and and an rv field that is pre-defined in
         global_constants.py\n
        """
        self.division = division
        if self.division == "STEM":
            self.cv = PASSING_TIME * 6 * 50
            self.subcv = 50
        elif self.division in {"Humanities", "Arts"}:
            self.cv = PASSING_TIME * 6 * 25
            self.subcv = 20
        self.rv = SPACE_RISK_MULTIPLIERS.get("Office")
        self.leaves = [SubSpace(self, self.subcv, SUBSPACE_RISK_MULTIPLIERS.get("Office"))] * 6

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

    def assignAgent(self, agent):
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
    def __init__(self, size, day, time):
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
        return 'Academic of size ' + self.size

    def __repr__(self):
        return 'Academic building of size ' + self.size

    def assignAgent(self, agent):
        if agent.type == "Faculty":
            return self.assignFaculty(agent)
        else:
            return self.assignStudent(agent)

    def assignStudent(self, agent):  # academic = academic building (Academic class) / classroom = SubSpace within Academic.classrooms
        random.shuffle(self.classrooms)
        for classroom in self.classrooms:
            if len(classroom.agents) < classroom.seats:
                classroom.agents.append(agent)
                return classroom
        return None

    def assignFaculty(self, agent):
        for classroom in self.classrooms:
            if classroom.faculty is None:
                classroom.faculty = agent
                return classroom
        return None

class SocialSpace(Space):
    def __init__(self):
        """
        Initialize a Social Space.\n
        The Social Space only has a leaves field, a list of 100 subspaces each initialized with a cv and rv field that is pre-defined in
         global_constants.py. The space itself does not have a cv or rv because the core social space has no actual meaning.\n
        """
        self.leaves = [SubSpace(self, SUBSPACE_CAPACITIES.get("Social Space"),
                                SUBSPACE_RISK_MULTIPLIERS.get("Social Space"))] * 100

    def __str__(self):
        return 'Social Space'

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
        return 'Subspace of ' + self.space.__str__()

    def __repr__(self):
        return 'Subspace of ' + self.space.__str__()

    def closeSubspace(self):
        """
        Close a subspace, setting CV, RV, and numberAssigned to 0.
        """
        self.cv = 0
        self.rv = 0
        self.numberAssigned = 0

    def getSpace(self):
        """
        Return the space that contains this subspace
        """
        return self.space

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