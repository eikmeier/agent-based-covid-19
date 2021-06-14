from global_constants import PASSING_TIME, TOTAL_AGENTS, SPACE_CAPACITIES, \
    SPACE_RISK_MULTIPLIERS, SUBSPACE_CAPACITIES, SUBSPACE_RISK_MULTIPLIERS
import math

class Space:
    def __init__(self, type):
        """ 
        Initialize a space with a type. Possible types are: "Transit Space", "Dining Hall", "Library",
        "Gym", "Office", "Large Gatherings", "Academic", and "Dorm".\n
        If the space is a dining hall, gym, library, or office, then the space will be given 6 empty subspaces given in the field leaves.\n
        """
        self.type = type
        if type in {"Dining Hall", "Gym", "Library", "Office"}:
            self.leaves = [SubSpace(self), SubSpace(self), SubSpace(self), SubSpace(self), SubSpace(self), SubSpace(self)]


    def getCV(self):
        """
        Get the capacity of a space.\n
        Note that Office spaces must have a defined division field that says whether they are in STEM, Humanities, or Arts.\n
        Additionally, note that Large Gatherings must have a defined numberAssigned field that counts how many people have been
        assigned to that space.\n
        Finally, Academic or Dorm spaces must have a defined size field with either "Small", "Medium", or "Large" in order to
        get the capacity.
        """
        if self.type in SPACE_CAPACITIES.keys():
            return SPACE_CAPACITIES.get(self.type)
        elif self.type == "Office":
            if self.division == "STEM":
                return PASSING_TIME * 6 * 50
            elif self.division in {"Humanities", "Arts"}:
                return PASSING_TIME * 6 * 25
        elif self.type == "Large Gatherings":
            return 40 * math.ceil(self.numberAssigned / 40.0) 
        elif self.type == "Academic":
            if self.size == "Small":
                return PASSING_TIME * 45
            elif self.size == "Medium":
                return PASSING_TIME * 90
            elif self.size == "Large":
                return PASSING_TIME * 225
        elif self.type == "Dorm":
            if self.size == "Small":
                return PASSING_TIME * 15
            elif self.size == "Medium":
                return PASSING_TIME * 45
            elif self.size == "Large":
                return PASSING_TIME * 75
        else: # If there is an error, return 0
            return 0

    def getRV(self):
        """
        Get the risk multiplier for infection spread in a space
        """
        if self.type in SPACE_RISK_MULTIPLIERS.keys():
            return SPACE_RISK_MULTIPLIERS.get(self.type)
        else: # If there is an error, return 0
            return 0

    def closeSpace(self):
        """
        Closes a space, setting RV and CV to 0.\n
        """
        pass #To be implemented


class SubSpace():
    def __init__(self, space):
        self.space = space
        self.type = space.type
    def getCV(self):
        """
        Get the capacity of a subspace.\n
        Note that Office spaces must have a defined division field that says whether they are in STEM, Humanities, or Arts.\n
        Also note that Classroom or Dorm spaces must have a defined size field with either "Small", "Medium", or "Large" in order to
        get the capacity.
        """
        if self.type in SUBSPACE_CAPACITIES.keys():
            return SUBSPACE_CAPACITIES.get(self.type)
        elif self.type == "Office":
            if self.division == "STEM":
                return 50
            elif self.division in {"Humanities", "Arts"}:
                return 20
        elif self.type == "Classroom":
            if self.size == "Small":
                return 15
            elif self.size == "Medium":
                return 20
            elif self.size == "Large":
                return 30
        elif self.type == "Dorm":
            if self.size == "Single":
                return 1
            elif self.size == "Double":
                return 2
            elif self.size in {"Small", "Medium", "Large"}:
                return self.numberAssigned
            else: # If there is an error, return 0
                return 0
    def getRV(self):
        """
        Get the risk multiplier for infection spread in a subspace
        """
        if self.type in SUBSPACE_RISK_MULTIPLIERS.keys():
            return SUBSPACE_RISK_MULTIPLIERS.get(self.type)
        else: # If there is an error, return 0
            return 0

# ***Below are some notes that need to be addressed, along with some notes for future reference***

"""
** Problems (or so-called problems, more like a running list of stuff for Erik to reference) with the code to fix:
 1. Add in Faculty Dining Leaf - what is the space for this though? Not sure, so it is not included yet
 2. Leaves of spaces is not fully implemented, we just have leaves created for DH, G, L, and O but nothing else
    -Particularly social spaces may be difficult since there are 100 leaves
 3. Documentation for Space initialization does not include all types yet, so quickly add that
 4. Need to figure out what to do with capacity and risk multipliers - there are significant pros and cons to having them as fields vs as methods

 5. Concern about having some types of spaces with unique fields. Is it simple enough to put this information in the documentation
  so people can understand what fields need to be initialized there, or is that too complicated for the project?
    - Not sure the alternative if it is too complicated, but understandable. On my code editor, when I type in the constructor,
     I can see the documentation immediately for the constructor so it is much easier to use. However, I understand that it is
     a special feature and many people will not have that ability.

 6. Are the names too long? I could have opted for the abbreviations in the paper, as used in #3, but I wanted this to be as readable
  as possible (although, funny enough, it ended up just making the code longer). If abbreviations are used, how will it be clear to a
  reader what they are, though? Do we assume they know everything in the paper or would we put a long comment somewhere in the code of
  all the space abbreviations?

 7. Do we need to consider anything else for spaces/subspaces?
    - Building closures, how should that be considered? Perhaps a method that closes a space would be good.
    - How do we know if a space is small/medium/large? Need to look into this / be saved by someone else who remembers
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