from global_constants import PASSING_TIME, TOTAL_AGENTS, SPACE_CAPACITIES, \
    SPACE_RISK_MULTIPLIERS, SUBSPACE_CAPACITIES, SUBSPACE_RISK_MULTIPLIERS
import math


class Space:
    def __init__(self, type, size = None, division = None):
        """ 
        Initialize a space with a type and, if applicable, a size or a division.\n
        Possible types are: "Transit Space", "Dining Hall", "Library",
        "Gym", "Office", "Large Gatherings", "Academic", and "Dorm".\n
        Possible sizes are: "Small", "Medium", and "Large". Only Academic or Dorm spaces must have a size.\n
        Possible divisions are: "STEM", "Humanities", and "Arts". Only Office spaces must have a division.\n
        If the space is a dining hall, gym, library, or office, then the space will be given 6 empty subspaces given in the field leaves.\n
        """
        self.type = type
        if size is not None:
            self.size = size

        # Initialize CV (Capacity) of the space
        if self.type in SPACE_CAPACITIES.keys():
            self.cv = SPACE_CAPACITIES.get(self.type)
        elif self.type == "Office":
            if self.division == "STEM":
                self.cv = PASSING_TIME * 6 * 50
            elif self.division in {"Humanities", "Arts"}:
                self.cv = PASSING_TIME * 6 * 25
        elif self.type == "Academic":
            if self.size == "Small":
                self.cv = PASSING_TIME * 45
            elif self.size == "Medium":
                self.cv = PASSING_TIME * 90
            elif self.size == "Large":
                self.cv = PASSING_TIME * 225
        elif self.type == "Dorm":
            if self.size == "Small":
                self.cv = PASSING_TIME * 15
            elif self.size == "Medium":
                self.cv = PASSING_TIME * 45
            elif self.size == "Large":
                self.cv = PASSING_TIME * 75
        else: # Large Gatherings will initially have a capacity of 0 until students are assigned
            self.cv = 0

        # Initialize RV (risk multiplier) of the space
        if self.type in SPACE_RISK_MULTIPLIERS.keys():
            self.rv = SPACE_RISK_MULTIPLIERS.get(self.type)
        else: # If there is an error, set RV to 0
            self.cv = 0

        if type in {"Dining Hall", "Gym", "Library", "Office"}:
            self.leaves = [SubSpace(self), SubSpace(self), SubSpace(self), SubSpace(self), SubSpace(self), SubSpace(self)]

    def getCV(self):
        """
        Get the capacity of a space.\n
        Note that Large Gatherings must have a defined numberAssigned field that counts how many people have been
        assigned to that space.
        """
        if self.type == "Large Gatherings":
            return 40 * math.ceil(self.numberAssigned / 40.0) 
        else:
            return self.cv

    def getRV(self):
        """
        Get the risk multiplier for infection spread in a space
        """
        return self.rv

    def closeSpace(self):
        """
        Closes a space, setting RV and CV to 0.
        """
        self.cv = 0
        self.rv = 0
        self.numberAssigned = 0


class Dorm(Space):
    def __init__(self, size):
        self.rv = 2
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
            self.singles[i] = SubSpace(1, 3)
        for j in range(len(self.doubles)):
            self.doubles[j] = SubSpace(2, 3)

# small_dorms = [Dorm("Small"), Dorm("Small")... Dorm("Small")]


class SubSpace():
    def __init__(self, space):
        self.space = space

        # Initialize CV (Capacity) of the subspace
        if self.space.type in SUBSPACE_CAPACITIES.keys():
            self.cv = SUBSPACE_CAPACITIES.get(self.space.type)
        elif self.space.type == "Office":
            if self.space.division == "STEM":
                self.cv = 50
            elif self.space.division in {"Humanities", "Arts"}:
                self.cv = 20
        elif self.space.type == "Classroom":
            if self.space.size == "Small":
                self.cv = 15
            elif self.space.size == "Medium":
                self.cv = 20
            elif self.space.size == "Large":
                self.cv = 30
        elif self.space.type == "Dorm":
            if self.space.size == "Single":
                self.cv = 1
            elif self.space.size == "Double":
                self.cv = 2
            else:  # If dorm is small, medium, or large
                self.cv = 0
        else:  # If there is an error, return 0
            self.cv = 0

        # Initialize RV (risk multiplier) of the subspace
        if self.space.type in SUBSPACE_RISK_MULTIPLIERS.keys():
            self.rv = SUBSPACE_RISK_MULTIPLIERS.get(self.space.type)
        else: # If there is an error, return 0
            return 0


    def getCV(self):
        """
        Get the capacity of a subspace.
        """
        if self.space.type == "Dorm" and self.space.size in {"Small", "Medium", "Large"}:
            return self.numberAssigned
        else:
            return self.cv
       
    def getRV(self):
        """
        Get the risk multiplier for infection spread in a subspace.
        """
        return self.rv
    
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
 1. Add in Faculty Dining Leaf - what is the space for this though? Not sure, so it is not included yet
 2. Figure out whether leaves of spaces should be implemented here or elsewhere in the code.
    -If here, need to add in the 100 social space leaves
 3. Initializer is confusing, need to clean up. Current approach is not really complete

 4. Unique fields of spaces and subspaces need to be clear to whoever is referring to this code

 5. Consider allowing abbreviated names along with long names (ex. DH and Dining Hall both work)
"""

# Our network has one gym, one library, one dining hall, and three faculty offices.

# Social spaces - core has no meaning but is included for sake of consistency

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
