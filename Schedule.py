import random
import CovidAgents
import spaces
from global_constants import DORM_BUILDINGS

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


# initialize agents - list of agents
agent_list = CovidAgents.Agent().initialize()
random.shuffle(agent_list)  # shuffle agents

# print("---------------------------------------------------------------")
# randomly assign agents to dorm buildings
for agent in agent_list:
    dorm_size = random.choice(["Small", "Medium", "Large"])
    if dorm_size == "Small":
        # index = random.choice(range(DORM_BUILDINGS.get("Small")))
        # agent.dorm_building = ["Small", index]
        agent.dorm_building = small_dorms[random.choice(range(DORM_BUILDINGS.get("Small")))]
    if dorm_size == "Medium":
        # index = random.choice(range(DORM_BUILDINGS.get("Medium")))
        # agent.dorm_building = ["Medium", index]
        agent.dorm_building = medium_dorms[random.choice(range(DORM_BUILDINGS.get("Medium")))]
    if dorm_size == "Large":
        # index = random.choice(range(DORM_BUILDINGS.get("Large")))
        # agent.dorm_building = ["Large", index]
        agent.dorm_building = large_dorms[random.choice(range(DORM_BUILDINGS.get("Large")))]
    # print(agent.dorm_building)


# randomly assign agents to dorm rooms
for agent in agent_list:
    agent.dorm_room = agent.dorm_building.assignAgent(agent)
    # print(agent.dorm_room)



# prints the list of agents for all the dorms
for dorm in small_dorms:
    for room in dorm.singles:
        print(room.agent)
    for room in dorm.doubles:
        print(room.agents)

for dorm in medium_dorms:
    for room in dorm.singles:
        print(room.agent)
    for room in dorm.doubles:
        print(room.agents)

for dorm in large_dorms:
    for room in dorm.singles:
        print(room.agent)
    for room in dorm.doubles:
        print(room.agents[0])
