import random
import copy
import CovidAgents
from spaces import Dorm, Academic
from global_constants import DORM_BUILDINGS, ACADEMIC_BUILDINGS

# initialize agents - list of agents
agent_list = CovidAgents.Agent().initialize()  # list of all agents

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
    print(classes)
