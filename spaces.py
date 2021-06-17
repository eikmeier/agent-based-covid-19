from global_constants import PASSING_TIME, TOTAL_AGENTS, SPACE_CAPACITIES, \
    SPACE_RISK_MULTIPLIERS, SUBSPACE_CAPACITIES, SUBSPACE_RISK_MULTIPLIERS
import math

class Space:
    def __init__(self):
        """ 
        Initialize a space with a type and, if applicable, a size or a division.\n
        Possible types are: "Transit Space", "Dining Hall", "Library",
        "Gym", "Office", "Large Gatherings", "Academic", and "Dorm".\n
        Possible sizes are: "Small", "Medium", and "Large". Only Academic or Dorm spaces must have a size.\n
        Possible divisions are: "STEM", "Humanities", and "Arts". Only Office spaces must have a division.\n
        If the space is a dining hall, gym, library, or office, then the space will be given 6 empty subspaces given in the field leaves.\n
        """

    def closeSpace(self):
        """
        Closes a space, setting RV and CV to 0.
        """
        self.cv = 0
        self.rv = 0
        self.numberAssigned = 0

class Dorm(Space):
    def __init__(self, size):
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

        for i in range(len(singles)):
            singles[i] = SubSpace(self, 1, SUBSPACE_RISK_MULTIPLIERS.get("Dorm"))
        for j in range(len(doubles)):
            doubles[j] = SubSpace(self, 2, SUBSPACE_RISK_MULTIPLIERS.get("Dorm"))

class TransitSpace(Space):
    def __init__(self):
        self.cv = SPACE_CAPACITIES.get("Transit Space")
        self.rv = SPACE_RISK_MULTIPLIERS.get("Transit Space")

class DiningHall(Space):
    def __init__(self):
        self.cv = SPACE_CAPACITIES.get("Dining Hall")
        self.rv = SPACE_RISK_MULTIPLIERS.get("Dining Hall")
        self.leaves = [SubSpace(self, SUBSPACE_CAPACITIES.get("Dining Hall"), SUBSPACE_RISK_MULTIPLIERS.get("Dining Hall"))] * 5
        self.leaves.append(SubSpace(self, SUBSPACE_CAPACITIES.get("Faculty Dining Leaf"), SUBSPACE_RISK_MULTIPLIERS.get("Faculty Dining Leaf")))

class Library(Space):
    def __init__(self):
        self.cv = SPACE_CAPACITIES.get("Library")
        self.rv = SPACE_RISK_MULTIPLIERS.get("Library")
        self.leaves = [SubSpace(self, SUBSPACE_CAPACITIES.get("Library"), SUBSPACE_RISK_MULTIPLIERS.get("Library"))] * 6

class Gym(Space):
    def __init__(self):
        self.cv = SPACE_CAPACITIES.get("Gym")
        self.rv = SPACE_RISK_MULTIPLIERS.get("Gym")
        self.leaves = [SubSpace(self, SUBSPACE_CAPACITIES.get("Gym"), SUBSPACE_RISK_MULTIPLIERS.get("Gym"))] * 6

class Office(Space):
    def __init__(self, division):
        if self.division == "STEM":
            self.cv = PASSING_TIME * 6 * 50
            self.subcv = 50
        elif self.division in {"Humanities", "Arts"}:
            self.cv = PASSING_TIME * 6 * 25
            self.subcv = 20
        self.rv = SPACE_RISK_MULTIPLIERS.get("Office")
        self.leaves = [SubSpace(self, self.subcv, SUBSPACE_RISK_MULTIPLIERS.get("Office"))] * 6

class LargeGatherings(Space):
    def __init__(self):
        self.cv = 0
        self.numberAssigned = 0
        self.rv = SPACE_RISK_MULTIPLIERS.get("Large Gatherings")

    def assign_agent(self, agent):
        self.numberAssigned += 1
        self.cv = 40 * math.ceil(self.numberAssigned / 40.0) 
        self.agents.append(agent)

class Academic(Space):
    small_classroom_cv = 15
    medium_classroom_cv = 20
    large_classroom_cv = 30
    def __init__(self, size):
        if self.size == "Small":
            self.cv = PASSING_TIME * 45
            self.classrooms = [SubSpace(self, small_classroom_cv, SUBSPACE_RISK_MULTIPLIERS.get("Classroom"))] * 3
        elif self.size == "Medium":
            self.cv = PASSING_TIME * 90
            self.classrooms = [SubSpace(self, small_classroom_cv, SUBSPACE_RISK_MULTIPLIERS.get("Classroom"))] * 2 + \
                                [SubSpace(self, medium_classroom_cv, SUBSPACE_RISK_MULTIPLIERS.get("Classroom"))] * 3
        elif self.size == "Large":
            self.cv = PASSING_TIME * 225
            self.classrooms = [SubSpace(self, small_classroom_cv, SUBSPACE_RISK_MULTIPLIERS.get("Classroom"))] * 5 + \
                                [SubSpace(self, medium_classroom_cv, SUBSPACE_RISK_MULTIPLIERS.get("Classroom"))] * 3 + \
                                [SubSpace(self, large_classroom_cv, SUBSPACE_RISK_MULTIPLIERS.get("Classroom"))] * 3
        self.rv = SPACE_RISK_MULTIPLIERS.get("Academic")
    pass

class SocialSpace(Space):
    def __init__(self):
        self.leaves = [SubSpace(self, SUBSPACE_CAPACITIES.get("Social Space"), SUBSPACE_RISK_MULTIPLIERS.get("Social Space"))] * 100

class SubSpace():
    def __init__(self, space, cv, rv):
        self.space = space
        self.cv = cv
        self.rv = rv

        # Initialize CV (Capacity) of the subspace
        if self.space.type in SUBSPACE_CAPACITIES.keys():
            self.cv = SUBSPACE_CAPACITIES.get(self.space.type)
        else: # If there is an error, return 0
            self.cv = 0

        # Initialize RV (risk multiplier) of the subspace
        if self.space.type in SUBSPACE_RISK_MULTIPLIERS.keys():
            self.rv = SUBSPACE_RISK_MULTIPLIERS.get(self.space.type)
        else: # If there is an error, return 0
            return 0
    
    def closeSubspace(self):
        """
        Closes a subspace, setting RV and CV to 0.
        """
        self.cv = 0
        self.rv = 0
        self.numberAssigned = 0

# ***Below are some notes that need to be addressed, along with some notes for future reference***

"""
** Problems (or so-called problems, more like a running list of stuff for Erik to reference) with the code to fix:
 1. Add in functionality to add agents to spaces (move from spaces to subspaces and vice versa as well...)
 2. Consider adding in closing spaces (gym/library/dining hall/large gatherings) based on h? Or to have this elsewhere

 3. Unique fields of spaces and subspaces need to be clear to whoever is referring to this code

 4. Consider allowing abbreviated names along with long names (ex. DH and Dining Hall both work)
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
