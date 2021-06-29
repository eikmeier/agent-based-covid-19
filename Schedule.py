import random
import copy
import CovidAgents
from spaces import Dorm, Academic, DiningHall, Gym, Library, SocialSpace
from global_constants import DORM_BUILDINGS, ACADEMIC_BUILDINGS, PROBABILITY_G, PROBABILITY_S, PROBABILITY_L

def initializeLeaves(agents):
    # Dining Hall has 5 leaves for students, 1 for faculty
    # Library has 6 leaves
    # Gym has 6 leaves
    # Social Space has 100 leaves
    random.shuffle(agents)
    student_counter = 0
    # Assign DH Leaves
    for agent in agents:
        if agent.type == "Faculty":
            agent.dhleaf = 5 # 5th to represent Faculty Dining Leaf
        else:
            agent.dhleaf = student_counter % 6
            student_counter += 1

    # Assign L leaves
    random.shuffle(agents)
    total_counter = 0
    for agent in agents:
        agent.lleaf = total_counter % 6
        total_counter += 1

    # Assign G Leaves
    random.shuffle(agents)
    total_counter = 0
    for agent in agents:
        agent.gleaf = total_counter % 6
        total_counter += 1

    # Assign Social Space Leaves
    random.shuffle(agents)
    total_counter = 0
    for agent in agents:
        agent.ssleaf = total_counter % 100
        total_counter += 1

    # Need to figure out where faculty can go to figure out how to distribute the leaves
        # Only need ID for DH, L, G, and Social Space I think
    # All spaces with leaves: DH, L, G, O [6l], Academic [Variable - len(classrooms)], Social Space

def getAvailableHours(start_hour, end_hour, day):
    available_times = []
    for i in range(start_hour, end_hour):
        if(agent.schedule.get(day)[i-8]) == None:
            available_times.append(i-8)
    return available_times

"""
def createSpaces(space):
    result = []
    space_class = getattr(spaces, space) #TODO: Fix this
    for i in range(3):
        for j in range(12):
            day = 'W'
            if i % 3 == 0:
                day = 'A'
            elif i % 3 == 1:
                day = 'B'

            hour = j + 17
            if(j % 4  == 0):
                hour = j + 8
            elif(i % 8 == 0):
                hour = j + 12

            result[i % 3][j % 12] = DiningHall(day, hour)
    return result
"""

# initialize agents - list of agents
agent_list = CovidAgents.Agent().initialize()  # list of all agents
initializeLeaves(agent_list)

on_campus_students = []  # list of students living on-campus and need to be assigned to a dorm room
for agent in agent_list:
    if agent.type == "On-campus Student":
        on_campus_students.append(agent)
random.shuffle(on_campus_students)  # shuffle agents

# DORM ASSIGNMENT ------------------------------------------------------------------------------------------------------------------------------------
# create dorm buildings (25 small, 10 medium, 10 large)
dorms = []
for i in range(DORM_BUILDINGS.get("Small")):
    dorms.append(Dorm("Small"))
for i in range(DORM_BUILDINGS.get("Medium")):
    dorms.append(Dorm("Medium"))
for i in range(DORM_BUILDINGS.get("Large")):
    dorms.append(Dorm("Large"))

# list of available dorms that are not fully occupied
available_dorms = copy.copy(dorms)

# randomly assigns agents(on-campus students) to dorms
for agent in on_campus_students:
    if len(dorms) == 0:  # if there are no available dorms(all dorms are full)
        print("All dorms are fully occupied")
    else:
        agent.dorm_building = random.choice(available_dorms)
        agent.dorm_room = agent.dorm_building.assignAgent(agent)
        if agent.dorm_building.status == "Full":
            available_dorms.remove(agent.dorm_building)
    #  print(agent.dorm_building)
    # print(agent.dorm_room)

# prints all the agents in each dorm
# for dorm in dorms:
#   print(dorm.size + str(dorms.index(dorm) + 1))
#  dorm.returnAgents()

# CLASS ASSIGNMENT ------------------------------------------------------------------------------------------------------------------------------------
# create academic buildings (STEM, Humanities, Arts) for class times ([10AM, 12PM, 14PM, 16PM] - index [2, 4, 6, 8])
# one list of all the classrooms at specific day(A or B) and time (2, 4, 6, 8)
stem_buildings = [[[] for i in range(4)] for i in range(2)] # STEM buildings: 2 small, 2 medium, 3 large
humanities_buildings = [[[] for i in range(4)] for i in range(2)]  # Humanities buildings: 1 small, 2 medium, 1 large
arts_buildings = [[[] for i in range(4)] for i in range(2)]  # Arts buildings: 2 small, 1 medium, 1 large
academic_buildings = [stem_buildings, humanities_buildings, arts_buildings]

# create all buildings at all day and times -> First list is split up by Day A and then Day B. Then list is split up by times (10, 12, 14, 16). Then,
 # finally, each entry at a specific day and time contains all academic buildings.

for i in range(8):
    for index, building_list in enumerate(academic_buildings):
        if i // 4 == 0:
            day_type = 'A'
        else:
            day_type = 'B'

        if index == 0:
            major = "STEM"
        elif index == 1:
            major = "Humanities"
        else:
            major = "Arts"

        for j in range(ACADEMIC_BUILDINGS.get(major)[0]):
            building_list[i // 4][i % 4].append(Academic("Small", day_type, 2 + 2 * (i % 4)))
        for k in range(ACADEMIC_BUILDINGS.get(major)[1]):
            building_list[i // 4][i % 4].append(Academic("Medium", day_type, 2 + 2 * (i % 4)))
        for l in range(ACADEMIC_BUILDINGS.get(major)[2]):
            building_list[i // 4][i % 4].append(Academic("Large", day_type, 2 + 2 * (i % 4)))

# Class assignment for each day & time
day_range = ["A", "B"]  # days for classes
time_range = [2, 4, 6, 8]  # index of time slots for classes
day_time = []  # [day, time] combinations for classes
for i in day_range:
    for j in time_range:
        day_time.append([i, j])

# randomly assign four classes
for agent in agent_list:
    class_times = random.sample(day_time, k=4)
    major_index = agent.getMajorIndex()
    class_num = 0  # selecting 1st and 2nd class for agent
    classes = []

    while class_num < 2:  # select two classes within agent's major
        class_time = class_times[class_num]  # a specific [day, time] for one class

        # We want to get a building from this major, at the time and day we have been given, and then assign an agent to that space.
        day = 0
        if class_time[0] == 'B':
            day = 1
        
        major_spaces = academic_buildings[major_index][day][int((class_time[1] - 2) / 2)]
        for space in major_spaces:
            classroom = space.assignAgent(agent)
            if classroom is None:
                continue
            
        class_num += 1
        classes.append(classroom)

    while class_num < 4 and agent.type != "Faculty":  # select two classes within agent's major
        class_time = class_times[class_num]  # a specific [day, time] for one class

        # We want to get a building from this major, at the time and day we have been given, and then assign an agent to that space.
        day = 0
        if class_time[0] == 'B':
            day = 1
        other_spaces = academic_buildings[random.randint(0, 2)][day][int((class_time[1] - 2) / 2)]
        for space in other_spaces:
            classroom = space.assignAgent(agent)
            if classroom is None:
                continue
                
        class_num += 1
        classes.append(classroom)

diningHallSpaces = [[[] for i in range(12)] for i in range(3)]
for i in range(3):
    for j in range(12):
        day = 'W'
        if i % 3 == 0:
            day = 'A'
        elif i % 3 == 1:
            day = 'B'

        hour = j + 17
        if(j % 4  == 0):
            hour = j + 8
        elif(i % 8 == 0):
            hour = j + 12

        diningHallSpaces[i % 3][j % 12] = DiningHall(day, hour)
    
for agent in agent_list:
    if agent.type == "Off-campus Student":
        aLunchHours = getAvailableHours(12, 15, 'A')
        aLunch = random.choice(aLunchHours)
        diningHallSpaces[0][aLunch].assignAgent(agent)

        bLunchHours = getAvailableHours(12, 15, 'B')
        bLunch = random.choice(bLunchHours)
        diningHallSpaces[0][bLunch].assignAgent(agent)
    elif agent.type == "Faculty":
        aLunchHours = getAvailableHours(11, 13, 'A')
        aLunch = random.choice(aLunchHours)
        diningHallSpaces[0][aLunch].assignAgent(agent)

        bLunchHours = getAvailableHours(11, 13, 'B')
        bLunch = random.choice(bLunchHours)
        diningHallSpaces[0][bLunch].assignAgent(agent)
    else:
        # First do W days, that is very simple since there will be no conflicts for any agents
        wBreakfast = random.randrange(0, 4)
        diningHallSpaces[2][wBreakfast].assignAgent(agent)
        wLunch = random.randrange(5, 8)
        diningHallSpaces[2][wLunch].assignAgent(agent)
        wDinner = random.randrange(9, 12)
        diningHallSpaces[2][wDinner].assignAgent(agent)

        # A - Breakfast
        aBreakfastHours = getAvailableHours(8, 11, 'A')
        aBreakfast = random.choice(aBreakfastHours)
        diningHallSpaces[0][aBreakfast].assignAgent(agent)
        # A - Lunch
        aLunchHours = getAvailableHours(12, 15, 'A')
        aLunch = random.choice(aLunchHours)
        diningHallSpaces[0][aLunch].assignAgent(agent)
        # A - Dinner
        aDinnerHours = getAvailableHours(17, 20, 'A')
        aDinner = random.choice(aDinnerHours)
        diningHallSpaces[0][aDinner].assignAgent(agent)
        # B - Breakfast
        bBreakfastHours = getAvailableHours(8, 11, 'B')
        bBreakfast = random.choice(aBreakfastHours)
        diningHallSpaces[0][bBreakfast].assignAgent(agent)
        # B - Lunch
        bLunchHours = getAvailableHours(12, 15, 'B')
        bLunch = random.choice(bLunchHours)
        diningHallSpaces[0][bLunch].assignAgent(agent)
        # B - Dinner
        bDinnerHours = getAvailableHours(17, 20, 'B')
        bDinner = random.choice(bDinnerHours)
        diningHallSpaces[0][bDinner].assignAgent(agent)

gymSpaces = [[[] for j in range(15)] for i in range(3)]
for i in range(3):
    for j in range(15):
        day = 'W'
        if i % 3 == 0:
            day = 'A'
        elif i % 3 == 1:
            day = 'B'

        gymSpaces[i % 3][j % 15] = Gym(day, j + 8)

# Try to assign Gym slots
for agent in agent_list:
    if agent.type != "Faculty":
        rand_chance_a = random.random()
        if rand_chance_a < PROBABILITY_G:
            #print("Agent assigned on A!")
            available_times_A = getAvailableHours(8, 22, 'A')
            hour = random.choice(available_times_A)
            gymSpaces[0][hour].assignAgent(agent)
        rand_chance_b = random.random()
        if rand_chance_b < PROBABILITY_G:
            #print("Agent assigned on B!")
            available_times_B = getAvailableHours(8, 22, 'B')
            hour = random.choice(available_times_B)
            gymSpaces[1][hour].assignAgent(agent)
        if agent.type == "On-campus Student":
            rand_chance_w = random.random()
            if rand_chance_w < PROBABILITY_G:
                print("Agent assigned on W!")
                available_times_W = getAvailableHours(8, 22, 'W')
                hour = random.choice(available_times_W)
                gymSpaces[2][hour].assignAgent(agent)

librarySpaces = [[[] for j in range(15)] for i in range(3)]
for i in range(3):
    for j in range(15):
        day = 'W'
        if i % 3 == 0:
            day = 'A'
        elif i % 3 == 1:
            day = 'B'

        librarySpaces[i % 3][j % 15] = Library(day, j + 8)

socialSpaces = [[[] for j in range(15)] for i in range(3)]
for i in range(3):
    for j in range(15):
        day = 'W'
        if i % 3 == 0:
            day = 'A'
        elif i % 3 == 1:
            day = 'B'

        socialSpaces[i % 3][j % 15] = SocialSpace(day, j + 8)
        
# Remaining slots for social spaces, library leaf, or dorm room
for agent in agent_list:
    if agent.type != "Faculty":
        for hour in getAvailableHours(8, 22, 'A'):
            rand_number = random.random()
            if rand_number < PROBABILITY_S: # Assign social space
                socialSpaces[0][hour].assignAgent(agent)
            elif rand_number < PROBABILITY_S + PROBABILITY_L: # Assign library space
                librarySpaces[0][hour].assignAgent(agent)
            else: # Assign dorm room if on-campus, otherwise assign off-campus
                pass
        for hour in getAvailableHours(8, 22, 'B'):
            rand_number = random.random()
            if rand_number < PROBABILITY_S: # Assign social space
                socialSpaces[1][hour].assignAgent(agent)
            elif rand_number < PROBABILITY_S + PROBABILITY_L: # Assign library space
                librarySpaces[1][hour].assignAgent(agent)
            else: # Assign dorm room if on-campus, otherwise assign off-campus
                pass
        if agent.type == "On-campus Student":
            for hour in getAvailableHours(8, 22, 'W'):
                rand_number = random.random()
                if rand_number < PROBABILITY_S: # Assign social space
                    socialSpaces[2][hour].assignAgent(agent)
                elif rand_number < PROBABILITY_S + PROBABILITY_L: # Assign library space
                    librarySpaces[2][hour].assignAgent(agent)
                else: # Assign dorm room
                    pass
        else:
            # Assign off-campus students to off-campus vertex for entire day
    else:
        # Faculty are in off campus vertex at times 8, 9, 18-22
        # Otherwise, appropriate Division Office vertex