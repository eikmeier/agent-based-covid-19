import random
import copy
import CovidAgents
import spaces
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
    dorms.append(spaces.Dorm("Small"))
for i in range(DORM_BUILDINGS.get("Medium")):
    dorms.append(spaces.Dorm("Medium"))
for i in range(DORM_BUILDINGS.get("Large")):
    dorms.append(spaces.Dorm("Large"))

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
stem_buildings = []  # STEM buildings: 2 small, 2 medium, 3 large
humanities_buildings = []  # Humanities buildings: 1 small, 2 medium, 1 large
arts_buildings = []  # Arts buildings: 2 small, 1 medium, 1 large
academic_buildings = [stem_buildings, humanities_buildings, arts_buildings]

# create STEM buildings
for i in range(2):

    if i == 0:
        day_type = "A"
    if i == 1:
        day_type = "B"

    for j in [2, 4, 6, 8]:
        for building_list in academic_buildings:
            index = academic_buildings.index(building_list)

            if index == 0:
                major = "STEM"
            if index == 1:
                major = "Humanities"
            if index == 2:
                major = "Arts"

            for k in range(ACADEMIC_BUILDINGS.get(major)[0]):
                academic_buildings[index].append(spaces.Academic("Small", day_type, j))
            for k in range(ACADEMIC_BUILDINGS.get(major)[1]):
                academic_buildings[index].append(spaces.Academic("Medium", day_type, j))
            for k in range(ACADEMIC_BUILDINGS.get(major)[2]):
                academic_buildings[index].append(spaces.Academic("Large", day_type, j))

stem_classes = []  # len(stem_classes) = number of classes/subspaces * number of [day, time] = 49 * 8 = 392
humanities_classes = []  # len(humanities_classes) = 24 * 8 = 192
arts_classes = []  # len(arts_classes) = 22 * 8 = 176
all_classes = [stem_classes, humanities_classes, arts_classes]

for building_list in academic_buildings:
    index = academic_buildings.index(building_list)
    for building in building_list:
        for classroom in building.classrooms:
            all_classes[index].append(classroom)


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

    major_index = 0
    if agent.subtype == "STEM":
        major_index = 0
    elif agent.subtype == "Humanities":
        major_index = 1
    elif agent.subtype == "Arts":
        major_index = 2

    i = 0
    class_num = 0  # selecting 1st and 2nd class for agent
    major_classes = []

    while class_num < 2:  # select two classes within agent's major
        class_time = class_times[class_num]  # a specific [day, time] for one class
        class_options = []  # list of major classes at the specific [day,time]
        for classroom in all_classes[major_index]:
            if classroom.space.day == class_time[0] and classroom.space.time == class_time[1]:
                class_options.append(classroom)
        random.shuffle(class_options)  # shuffle list of subspaces/classes for randomization

        # iterate through the shuffled list of classes - check availability starting from the first class.
        # If class is available, assign agent to class. If class is full, move on to next index/class until you find an available class.
        current_class = class_options[i]
        if current_class.status == "Available":
            current_class.space.assignClass(agent, current_class.space, current_class)
            major_classes.append(current_class)
            class_options.pop(i)
            i += 1
            class_num += 1
        else:  # if current_class.status == "Full"
            i += 1
    # print(major_classes)
    # print([major_classes[0].space.day, major_classes[0].space.time])

    if agent.type == "Faculty":
        other_classes = []
    else:  # agent.type = "On-campus Student" or "Off-campus Student"
        i = 0
        class_num = 2  # selecting 3rd and 4th class for agent
        other_classes = []

        while class_num < 4:  # select two classes within agent's major
            class_time = class_times[class_num]  # a specific [day, time] for one class
            class_options = []  # list of any(STEM/Humanities/Arts) classes at the specific [day,time]
            for division in all_classes:
                for classroom in division:
                    if classroom.space.day == class_time[0] and classroom.space.time == class_time[1]:
                        class_options.append(classroom)
            random.shuffle(class_options)  # shuffle list of subspaces/classes for randomization

            # iterate through the shuffled list of classes - check availability starting from the first class.
            # If class is available, assign agent to class. If class is full, move on to next index/class until you find an available class.
            current_class = class_options[i]
            if current_class.status == "Available":
                current_class.space.assignClass(agent, current_class.space, current_class)
                major_classes.append(current_class)
                class_options.pop(i)
                i += 1
                class_num += 1
            else:  # if current_class.status == "Full"
                i += 1
        # print(other_classes)
        # print([major_classes[0].space.day, major_classes[0].space.time])
    class_schedule = major_classes + other_classes
    print(class_schedule)


