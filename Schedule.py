import random
import CovidAgents
import spaces
from global_constants import DORM_BUILDINGS


# initialize agents - list of agents
agent_list = CovidAgents.Agent().initialize()  # list of all agents

on_campus_students = []  # list of students living on-campus and need to be assigned to a dorm room
for agent in agent_list:
    if agent.type == "On-campus Student":
        on_campus_students.append(agent)
random.shuffle(on_campus_students)  # shuffle agents
print(len(on_campus_students))




# DORM ASSIGNMENT ------------------------------------------------------------------------------------------------------------------------------------
# create dorm buildings (25 small, 10 medium, 10 large)
small_dorms = []
medium_dorms = []
large_dorms = []

i = 0
for i in range(DORM_BUILDINGS.get("Small")):
    small_dorms.append(spaces.Dorm("Small"))
    i += 1
i = 0
for i in range(DORM_BUILDINGS.get("Medium")):
    medium_dorms.append(spaces.Dorm("Medium"))
    i += 1
i = 0
for i in range(DORM_BUILDINGS.get("Large")):
    large_dorms.append(spaces.Dorm("Large"))
    i += 1


# print("---------------------------------------------------------------")
# randomly assign agents to dorm buildings & dorm rooms
for agent in on_campus_students:
    # list of available dorms that are not fully occupied
    available_small = []
    available_medium = []
    available_large = []
    for dorm in small_dorms:
        if dorm.status == "Available":
            available_small.append(dorm)
    for dorm in medium_dorms:
        if dorm.status == "Available":
            available_medium.append(dorm)
    for dorm in large_dorms:
        if dorm.status == "Available":
            available_large.append(dorm)

    # remove dorm sizes that are fully occupied
    dorm_sizes = ["Small", "Medium", "Large"]
    if len(available_small) == 0:  # there are no available small dorms
        dorm_sizes.remove("Small")
    if len(available_medium) == 0:  # there are no available medium dorms
        dorm_sizes.remove("Medium")
    if len(available_large) == 0:  # there are no available large dorms
        dorm_sizes.remove("Large")


    if len(dorm_sizes) == 0:  #if there are no available dorms(all dorms are full)
        print("All dorms are fully occupied")
    else:
        dorm_size = random.choice(dorm_sizes)  # randomly select a size for dorm building
        if dorm_size == "Small":
            agent.dorm_building = available_small[random.choice(range(len(available_small)))]  # randomly select one of the available small dorms
            agent.dorm_room = agent.dorm_building.assignAgent(agent)
        elif dorm_size == "Medium":
            agent.dorm_building = available_medium[random.choice(range(len(available_medium)))]  # randomly select one of the available medium dorms
            agent.dorm_room = agent.dorm_building.assignAgent(agent)
        elif dorm_size == "Large":
            agent.dorm_building = available_large[random.choice(range(len(available_large)))]  # randomly select one of the available large dorms
            agent.dorm_room = agent.dorm_building.assignAgent(agent)
        # print(agent.dorm_building)
        # print(agent.dorm_room)


# prints the list of agents for all the dorms
# print("---------------------------------------------------------------------------------------------------------------------------")
for dorm in small_dorms:
    dorm.returnAgents()
print("---------------------------------------------------------------------------------------------------------------------------")
for dorm in medium_dorms:
    dorm.returnAgents()
print("---------------------------------------------------------------------------------------------------------------------------")
for dorm in large_dorms:
    dorm.returnAgents()





# CLASS ASSIGNMENT ------------------------------------------------------------------------------------------------------------------------------------

