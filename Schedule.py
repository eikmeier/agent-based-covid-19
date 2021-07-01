import random
import copy
import CovidAgents
from spaces import Dorm, Academic, DiningHall, Gym, Library, SocialSpace, OffCampus
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

    # Assign Social Space Leaves (Days A & B)
    random.shuffle(agents)
    total_counter = 0
    for agent in agents:
        if agent.type != "Faculty":
            agent.ssleaf = total_counter % 100
            total_counter += 1

    # Assign Social Space Leaves (Day W)
    random.shuffle(agents)
    total_counter = 0
    for agent in agents:
        if agent.type != "Faculty":
            agent.ssleaf_w = total_counter % 100
            total_counter += 1

    # Need to figure out where faculty can go to figure out how to distribute the leaves
        # Only need ID for DH, L, G, and Social Space I think
    # All spaces with leaves: DH, L, G, O [6l], Academic [Variable - len(classrooms)], Social Space

def createSpaces(space, num_hours = 15):
    result = [[[] for j in range(num_hours)] for i in range(3)]
    all_methods = globals().copy()
    space_class = all_methods.get(space)
    for i in range(3):
        for j in range(num_hours):
            day = 'W'
            if i % 3 == 0:
                day = 'A'
            elif i % 3 == 1:
                day = 'B'
            result[i % 3][j % num_hours] = space_class(day, j)
    return result

def assignMeal(agent, day, start_hour, end_hour, dhArr):
    day_index = 0
    if day == 'B':
        day_index = 1
    elif day == 'W':
        day_index = 2
    possibleMealHours = agent.getAvailableHours(start_hour, end_hour, day)
    if possibleMealHours:
        mealHour = random.choice(possibleMealHours)
        dhArr[day_index][mealHour].assignAgent(agent)

# initialize agents - list of agents
agent_list = CovidAgents.Agent().initialize()  # list of all agents
initializeLeaves(agent_list)

on_campus_students = []  # list of students living on-campus and need to be assigned to a dorm room
off_campus_agents = []
for agent in agent_list:
    if agent.type == "On-campus Student":
        on_campus_students.append(agent)
    else:
        off_campus_agents.append(agent)
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

# Assign all off-campus agents (off-campus students or faculty) to off campus space
offCampusSpace = OffCampus()
for agent in off_campus_agents:
    offCampusSpace.assignAgent(agent)
    agent.dorm_room = offCampusSpace #TODO: Decide if to delete/modify this?

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

diningHallSpaces = createSpaces("DiningHall", 13) # We have unused Dining Hall spaces (at time 16) because the hours are not consecutive
    
for agent in agent_list: # Assign dining hall times to all agents
    if agent.type == "Off-campus Student":
        for day in ['A', 'B']:
            assignMeal(agent, day, 12, 15, diningHallSpaces)
    elif agent.type == "Faculty":
        for day in ['A', 'B']:
            assignMeal(agent, day, 11, 13, diningHallSpaces)     
    else:
        for day in ['A', 'B', 'W']:
            assignMeal(agent, day, 8, 11, diningHallSpaces)
            assignMeal(agent, day, 12, 15, diningHallSpaces)
            assignMeal(agent, day, 17, 20, diningHallSpaces)

gymSpaces = createSpaces("Gym")

# Try to assign Gym slots
for agent in agent_list:
    if agent.type != "Faculty":
        for count, day in enumerate(['A', 'B', 'W']):
            if day == 'W' and agent.type == "Off-campus Student":
                break
            rand_prob = random.random()
            if rand_prob < PROBABILITY_G:
                available_times = agent.getAvailableHours(8, 22, day)
                gymHour = random.choice(available_times)
                gymSpaces[count][gymHour].assignAgent(agent)

librarySpaces = createSpaces("Library")
socialSpaces = createSpaces("SocialSpace")
        
# Remaining slots for social spaces, library leaf, or dorm room
for agent in agent_list:
    if agent.type != "Faculty":
        for count, day in enumerate(['A', 'B', 'W']):
            for hour in agent.getAvailableHours(8, 22, day):
                if day == 'W' and agent.type == "Off-campus Student":
                    agent.schedule.get(day)[hour] = "Off-Campus Space"
                    continue
                rand_number = random.random()
                if rand_number < PROBABILITY_S: # Assign social space
                    socialSpaces[count][hour].assignAgent(agent)
                elif rand_number < PROBABILITY_S + PROBABILITY_L: # Assign library space
                    librarySpaces[count][hour].assignAgent(agent)
                else: # Assign dorm room if on-campus, otherwise assign off-campus
                    if agent.type == "On-campus Student":
                        agent.schedule.get(day)[hour] = "Dorm"
                    else:
                        agent.schedule.get(day)[hour] = "Off-Campus Space"
    else:
        for count, day in enumerate(['A', 'B', 'W']):
            for hour in agent.getAvailableHours(8, 22, day):
                if hour == 8 or hour == 9 or hour >= 18 and hour <= 22:
                    agent.schedule.get(day)[hour] = "Off-Campus Space"
                else: # Put into appropriate Division Office vertex
                    pass