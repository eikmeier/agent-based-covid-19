import random
import CovidAgents
from CovidAgents import initialize_leaves, change_states
from Schedule import create_spaces, create_dorms, create_academic_spaces, assign_dorms, assign_agents_to_classes, assign_dining_times, assign_gym, \
    assign_remaining_time, all_transit_spaces, doubles_dorm_times
from global_constants import DORM_BUILDINGS, ACADEMIC_BUILDINGS, CLASSROOMS, SIMULATION_LENGTH, SCHEDULE_DAYS
from spaces import Dorm, Academic, LargeGatherings
from Schedule import all_transit_spaces
import matplotlib.pyplot as plt

# Initialize agents
agent_list = CovidAgents.Agent().initialize() 


def initialize():
    # Create spaces
    dorms = create_dorms()
    academic_buildings = create_academic_spaces([[[] for i in range(4)] for i in range(2)], [[[] for i in range(4)] for i in range(2)], \
        [[[] for i in range(4)] for i in range(2)]) # Create a list for each day/hour combination for each division (STEM, Humanities, Arts)
    dining_hall_spaces = create_spaces("DiningHall", 13)  # We have unused Dining Hall spaces (at time 16) because the hours are not consecutive
    gym_spaces = create_spaces("Gym")
    library_spaces = create_spaces("Library")
    social_spaces = create_spaces("SocialSpace")
    stem_office_spaces = create_spaces("Office", 10, "STEM")
    arts_office_spaces = create_spaces("Office", 10, "Arts")
    humanities_office_spaces = create_spaces("Office", 10, "Humanities")

    # Assign agents to spaces
    assign_dorms(dorms, agent_list)
    assign_agents_to_classes(academic_buildings, agent_list)
    assign_dining_times(dining_hall_spaces, agent_list)

    assign_gym(agent_list, gym_spaces)
    assign_remaining_time(agent_list, library_spaces, social_spaces, stem_office_spaces, arts_office_spaces, humanities_office_spaces)

    # CODE TO CHECK IF TRANSIT SPACE ASSIGNMENT IS DONE PROPERLY
    for agent in agent_list:
        for day in SCHEDULE_DAYS:
            for i in range(14):
                day_schedule = agent.schedule.get(day)
                if day_schedule[i] != day_schedule[i + 1]:
                    # print("there should be transit space")
                    if agent not in all_transit_spaces[day][i + 1].agents:  # if agent is not assigned to a transit space that they are supposed to be assigned to
                        print(agent.type + " ... NOT IN TRANSIT SPACE: " + str(day_schedule[i]) + ", "  + str(day_schedule[i + 1]) + " [" + str(i) + ", " + str(i+1) + "]")

    return [dining_hall_spaces, gym_spaces, library_spaces, social_spaces, stem_office_spaces, humanities_office_spaces, arts_office_spaces , \
        academic_buildings[0], academic_buildings[1], academic_buildings[2], dorms] # Return a list containing all the spaces (to be used in update)

def observe(data):
    # Figure out the spaces where everyone got exposed
    data['space_exposures'] = {"Dining Hall": 0, "Gym": 0, "Library": 0, "Large Gatherings": 0, "Social Space": 0, "Office": 0,
                               "Academic": 0, "Dorm": 0, "Transit Space": 0, "Off-Campus": 0, "Other": 0}
    for agent in [agent for agent in agent_list if agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie" or agent.seir == "R"]:
        if "Dining Hall" in str(agent.exposed_space):
            data['space_exposures']["Dining Hall"] += 1
        elif "Gym" in str(agent.exposed_space):
            data['space_exposures']["Gym"] += 1
        elif "Library" in str(agent.exposed_space):
            data['space_exposures']["Library"] += 1
        elif "Large Gatherings" in str(agent.exposed_space):
            data['space_exposures']["Large Gatherings"] += 1
        elif "Social Space" in str(agent.exposed_space):
            data['space_exposures']["Social Space"] += 1
        elif "Office" in str(agent.exposed_space):
            data['space_exposures']["Office"] += 1
        elif "Academic" in str(agent.exposed_space):
            data['space_exposures']["Academic"] += 1
        elif "Dorm" in str(agent.exposed_space):
            data['space_exposures']["Dorm"] += 1
        elif "Transit Space" in str(agent.exposed_space):
            data['space_exposures']["Transit Space"] += 1
        elif "Off-Campus" in str(agent.exposed_space):
            data['space_exposures']["Off-Campus"] += 1
        elif agent.exposed_space != None:
            data['space_exposures']["Other"] += 1

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4)
    fig.suptitle('Looking at new exposures and total infections over 14 weeks')
    ax1.set_ylabel("New Exposures")
    ax2.set_ylabel("Total Infections")
    ax3.set_ylabel("# of Infections")
    ax4.set_ylabel("# of Agents")
    ax1.set_xlabel("Day #")
    ax2.set_xlabel("Day #")
    ax3.set_xlabel("Spaces")
    ax4.set_xlabel("Day #")
    ax1.plot(range(len(data['new_exposures'])), data['new_exposures'])
    ax2.plot(range(len(data['total_infections'])), data['total_infections'])
    ax3.bar(data['space_exposures'].keys(), data['space_exposures'].values(), color=['palegreen', 'olivedrab', 'forestgreen',
        'limegreen', 'darkgreen', 'green', 'seagreen', 'springgreen', 'yellowgreen', 'lawngreen', 'turquoise', 'teal', 'olive'])
    ax4.plot(range(len(data['seir_states']['s'])), data['seir_states']['s'], label = "Susceptible Agents")
    ax4.plot(range(len(data['seir_states']['e'])), data['seir_states']['e'], label = "Exposed Agents")
    ax4.plot(range(len(data['seir_states']['i'])), data['seir_states']['i'], label = "Infected Agents")
    ax4.plot(range(len(data['seir_states']['r'])), data['seir_states']['r'], label = "Recovered Agents")
    plt.legend()
    plt.show()

def update():
    spaces = initialize()
    current_exposed = 0
    data = {}
    data['new_exposures'] = [0]
    data['total_infections'] = [0]
    data['seir_states'] = {'s': [], 'e': [], 'i': [], 'r': []}

    for week in range(SIMULATION_LENGTH):
        for day in ['A', 'B', 'A', 'B', 'A', 'W', 'S']:
            day_index = 0  # Default day is 'A'
            if day == 'B':
                day_index = 1
            elif day == 'W':
                day_index = 2
            elif day == 'S':
                large_gatherings = [LargeGatherings(), LargeGatherings(), LargeGatherings()]
                for large_gathering in large_gatherings:
                    large_gathering.assign_agents(random.sample([agent for agent in agent_list if agent.social == True], k=random.randrange(20, 60)))
                    large_gathering.spread_infection()
                break

            for day in all_transit_spaces:
                for transit_space in all_transit_spaces.get(day):
                    transit_space.spread_infection_core()

            # Off-Campus infection spread
            off_campus_agents = [agent for agent in agent_list if agent.type == "Faculty" or agent.type == "Off-campus Student"]
            probability_o = 0.125 / len(off_campus_agents)
            for agent in [agent for agent in off_campus_agents if agent.seir == "S"]:
                rand_num = random.random()
                if rand_num < probability_o:
                    agent.change_state("E")
                    agent.exposed_space = "Off-Campus"

            for space in spaces:
                if day_index < len(space): # If the space is open on this day, then spread the infection [NOTE: This requires spaces in the array always be separated by A, B, and W in order]
                    if "Dorm" in str(space):
                        for dorm in space:
                            for day_count, dorm_day in enumerate(dorm.agents):
                                for dorm_time, agents_in_time in enumerate(dorm_day):
                                    if dorm_time != 8 or dorm_time != 22:
                                        dorm.spread_infection_core(day_count, dorm_time)
                                    dorm.spread_infection_core(day_count, dorm_time)

                        for double_dorm_day in doubles_dorm_times:
                            for double_dorms in double_dorm_day:
                                for double_dorm in double_dorms:
                                    double_dorm.spread_infection() # Spreads the infection in the dorm room when both agents are inside
                    else:
                        for space_in_time in space[day_index]:
                            if type(space_in_time) is list:
                                for space in space_in_time:
                                    space.spread_in_space()
                            else:
                                space_in_time.spread_in_space()

            change_states(agent_list)
            exposed_agents = [agent for agent in agent_list if agent.seir == "E" or agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie" or agent.seir == "R"]
            data['new_exposures'].append(len(exposed_agents) - current_exposed)
            current_exposed = len(exposed_agents)
            infected_agents = [agent for agent in agent_list if agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie" or agent.seir == "R"]
            data['total_infections'].append(len(infected_agents))
            data['seir_states']['s'].append(len([agent for agent in agent_list if agent.seir == "S"]))
            data['seir_states']['e'].append(len([agent for agent in agent_list if agent.seir == "E"]))
            data['seir_states']['i'].append(len([agent for agent in agent_list if agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie"]))
            data['seir_states']['r'].append(len([agent for agent in agent_list if agent.seir == "R"]))
            print("Day " + day + ", Week " + str(week) + ", # of Infected Agents: " + str(len(infected_agents)))
    observe(data)


update()

"""
# Count infections in each space
dhI, gI, lI, lgI, ssI, oI, aI, dI, tsI, ocI, other, nonI = (0,)*12
for agent in agent_list:
    if "Dining Hall" in str(agent.exposed_space):
        dhI += 1
    elif "Gym" in str(agent.exposed_space):
        gI += 1
    elif "Library" in str(agent.exposed_space):
        lI += 1
    elif "Large Gatherings" in str(agent.exposed_space):
        lgI += 1
    elif "Social Space" in str(agent.exposed_space):
        ssI += 1
    elif "Office" in str(agent.exposed_space):
        oI += 1
    elif "Academic" in str(agent.exposed_space):
        aI += 1
    elif "Dorm" in str(agent.exposed_space):
        dI += 1
    elif "Transit Space" in str(agent.exposed_space):
        tsI += 1
    elif "Off-Campus" in str(agent.exposed_space):
        ocI += 1
    elif agent.exposed_space != None:
        other += 1
    else: 
        nonI += 1

print("# Infected in Dining Hall: " + str(dhI))
print("# Infected in Gym: " + str(gI))
print("# Infected in Library: " + str(lI))
print("# Infected in Large Gatherings: " + str(lgI))
print("# Infected in Social Space: " + str(ssI))
print("# Infected in Office: " + str(oI))
print("# Infected in Academic Spaces: " + str(aI))
print("# Infected in Dorms: " + str(dI))
print("# Infected in Transit Space: " + str(tsI))
print("# Infected in Off-Campus: " + str(ocI))
print("# Infected in 'Other': " + str(other))
print("# Not Infected: " + str(nonI))
"""

"""
 For large gatherings, half of the student agents (both on- and off-campus) are denoted as “social.” 
 We simulate large informal gatherings (e.g., parties or organized social events) by drawing three 
 random subsets G1, G2, G3 of agents designated as social at the end of each week.  Each Gi has size 
 uniformly and independently sampled from [20,60].  The Gi are sampled independently and are not 
 necessarily disjoint.  Each susceptible agent at a large gathering becomes infected according to (2) 
 with rv= 3 and Cv= 40d|Gi|/40e, i.e., Cv= 40 if|Gi|≤40, andCv= 80 if|Gi|>40.
"""