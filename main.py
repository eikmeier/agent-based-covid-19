import random
import CovidAgents
from CovidAgents import initialize_leaves, change_states
from Schedule import create_spaces, create_dorms, create_academic_spaces, assign_dorms, assign_agents_to_classes, assign_dining_times, \
    assign_gym, assign_remaining_time, all_transit_spaces, doubles_dorm_times
from global_constants import CLASS_TIMES, DORM_BUILDINGS, ACADEMIC_BUILDINGS, CLASSROOMS, SCHEDULE_HOURS, SCHEDULE_WEEKDAYS, SIMULATION_LENGTH, SCHEDULE_DAYS, \
    INITIALLY_INEFCTED, TOTAL_AGENTS
from spaces import Dorm, Academic, LargeGatherings
from Schedule import all_transit_spaces
import matplotlib.pyplot as plt
import time
from statistics import stdev
from multiprocessing import Pool, Manager

plt.rcParams.update({'figure.autolayout': True}) # A required line so the bar graph labels stay on the screen

agent_list = [] # list of all agents

def initialize():
    # Initialize agents
    global agent_list
    agent_list = CovidAgents.Agent().initialize()

    # Create spaces
    dorms = create_dorms()
    academic_buildings = create_academic_spaces([[[] for i in range(4)] for i in range(2)], [[[] for i in range(4)] for i in range(2)], \
        [[[] for i in range(4)] for i in range(2)]) # Create a list for each day/hour combination for each division (STEM, Humanities, Arts)
    dining_hall_spaces = create_spaces("DiningHall", 9, 20, [16])
    gym_spaces = create_spaces("Gym")
    library_spaces = create_spaces("Library")
    social_spaces = create_spaces("SocialSpace")
    stem_office_spaces = create_spaces("Office", 10, 17, None, SCHEDULE_WEEKDAYS, "STEM")
    arts_office_spaces = create_spaces("Office", 10, 17, None, SCHEDULE_WEEKDAYS, "Arts")
    humanities_office_spaces = create_spaces("Office", 10, 17, None, SCHEDULE_WEEKDAYS, "Humanities")

    # Assign agents to spaces
    assign_dorms(dorms, agent_list)
    assign_agents_to_classes(academic_buildings, agent_list)
    assign_dining_times(dining_hall_spaces, agent_list)

    assign_gym(agent_list, gym_spaces)
    assign_remaining_time(agent_list, library_spaces, social_spaces, stem_office_spaces, arts_office_spaces,
                          humanities_office_spaces)

    return [dining_hall_spaces, gym_spaces, library_spaces, social_spaces, stem_office_spaces, humanities_office_spaces, arts_office_spaces , \
        academic_buildings[0], academic_buildings[1], academic_buildings[2], dorms] # Return a list containing all the spaces (to be used in update)

def observe(data):
    # Figure out the spaces where everyone got exposed
    """
    data[0]['space_exposures'] = {"Dining Hall": 0, "Gym": 0, "Library": 0, "Large Gatherings": 0, "Social Space": 0, "Office": 0, 
                               "Academic": 0, "Dorm": 0, "Transit Space": 0, "Off-Campus": 0}
    for agent in [agent for agent in agent_list if agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie" or agent.seir == "R"]:
        if "Dining Hall" in str(agent.exposed_space):
            data[0]['space_exposures']["Dining Hall"] += 1
        elif "Gym" in str(agent.exposed_space):
            data[0]['space_exposures']["Gym"] += 1
        elif "Library" in str(agent.exposed_space):
            data[0]['space_exposures']["Library"] += 1
        elif "Large Gatherings" in str(agent.exposed_space):
            data[0]['space_exposures']["Large Gatherings"] += 1
        elif "Social Space" in str(agent.exposed_space):
            data[0]['space_exposures']["Social Space"] += 1
        elif "Office" in str(agent.exposed_space):
            data[0]['space_exposures']["Office"] += 1
        elif "Academic" in str(agent.exposed_space):
            data[0]['space_exposures']["Academic"] += 1
        elif "Dorm" in str(agent.exposed_space):
            data[0]['space_exposures']["Dorm"] += 1
        elif "Transit Space" in str(agent.exposed_space):
            data[0]['space_exposures']["Transit Space"] += 1
        elif "Off-Campus" in str(agent.exposed_space):
            data[0]['space_exposures']["Off-Campus"] += 1 # TODO: Put back as well!
    print(data[0])
    data[0]['space_exposures'] = dict(sorted(data[0]['space_exposures'].items(), key=lambda item: item[1], reverse = True)) # TODO: Put back!
    """
    number_of_simulations = len(data) - 1
    averaged_data = data[number_of_simulations]

    for day in range(len(data[0]['new_exposures'])): # Set all days to 0 as default
        averaged_data['new_exposures'].append(0)
        averaged_data['total_infections'].append(0)

    for day in range(len(data[0]['new_exposures'])): #NOTE: Requires simulation to have been run at least once
        for simulation_num in range(number_of_simulations):
            averaged_data['new_exposures'][day] += data[simulation_num]['new_exposures'][day]
            averaged_data['total_infections'][day] += data[simulation_num]['total_infections'][day]

    # Divide each element of the list by # of simulations to really take thee average
    averaged_data['new_exposures'] = [day / number_of_simulations for day in averaged_data['new_exposures']]
    averaged_data['total_infections'] = [day / number_of_simulations for day in averaged_data['total_infections']]

    ne_stdev = []
    ti_stdev = []
    # Calculate STDEV for each day
    for day in range(len(data[0]['new_exposures'])):
        day_list_ne = []
        day_list_ti = []
        for sim_1 in range(number_of_simulations):
            day_list_ne.append(data[sim_1]['new_exposures'][day])
            day_list_ti.append(data[sim_1]['total_infections'][day])
        std_ne = stdev(day_list_ne)
        std_ti = stdev(day_list_ti)
        ne_stdev.append(std_ne)
        ti_stdev.append(std_ti)

    data[number_of_simulations] = averaged_data
    plt.figure(0)
    for day in range(len(data[0]['new_exposures'])):
        plt.errorbar(day, data[number_of_simulations]['new_exposures'][day], yerr=ne_stdev[day], fmt='r^')
    plt.plot(range(len(data[0]['new_exposures'])), data[number_of_simulations]['new_exposures'])

    plt.xlabel("Day #")
    plt.ylabel("New Exposures")
    plt.savefig('images/new_exposures.png')
    plt.figure(1)
    for day in range(len(data[0]['total_infections'])):
        plt.errorbar(day, data[number_of_simulations]['total_infections'][day], yerr=ti_stdev[day], fmt='r^')
    plt.plot(range(len(data[0]['total_infections'])), data[number_of_simulations]['total_infections'])
    plt.xlabel("Day #")
    plt.ylabel("Total Infections")
    plt.savefig('images/total_infections.png')
    plt.figure(2)
    for seir_sim_num in range(number_of_simulations):
        plt.plot(range(len(data[seir_sim_num]['seir_states']['s'])), data[seir_sim_num]['seir_states']['s'], color='b')
        plt.plot(range(len(data[seir_sim_num]['seir_states']['e'])), data[seir_sim_num]['seir_states']['e'], color='tab:orange')
        plt.plot(range(len(data[seir_sim_num]['seir_states']['i'])), data[seir_sim_num]['seir_states']['i'], color='r')
        plt.plot(range(len(data[seir_sim_num]['seir_states']['r'])), data[seir_sim_num]['seir_states']['r'], color='m')
    # Adding in plotting labels to legend
    plt.plot([], [], label = "Susceptible Agents", color='b')
    plt.plot([], [], label = "Exposed Agents", color='tab:orange')
    plt.plot([], [], label = "Infected Agents", color='r')
    plt.plot([], [], label = "Recovered Agents", color='m')
    plt.xlabel("Day #")
    plt.ylabel("# of Agents")
    plt.legend()
    plt.savefig('images/seir_states.png')
    # Spaces Bar Graph
    """
    plt.figure(3)
    plt.xlabel("Spaces")
    plt.ylabel("# of Infections")
    plt.xticks(rotation=45, ha="right")
    plt.bar(data[0]['space_exposures'].keys(), data[0]['space_exposures'].values())
    """
    plt.show()

def update(data, simulation_number):
    update_dorms = []
    sim_data = data[simulation_number]
    spaces = initialize()
    off_campus_agents = [agent for agent in agent_list if agent.type == "Faculty" or agent.type == "Off-campus Student"]
    probability_o = 0.125 / len(off_campus_agents)
    sim_data['new_exposures'].append(0)
    sim_data['total_infections'].append(0)

    for space in spaces:
        if "Dorm" in str(space):
            update_dorms = space

    # Infection spread in chronological order
    for week in range(SIMULATION_LENGTH):
        for day in ['A', 'B', 'A', 'B', 'W', 'W', 'S']:
            day_index = 0 # Default day is 'A'
            if day == 'B':
                day_index = 1
            elif day == 'W':
                day_index = 2

            # Off-Campus infection spread, happens every day for all off-campus agents
            for off_campus_agent in [agent for agent in off_campus_agents if agent.seir == "S"]:
                rand_num = random.random()
                probability_o *= off_campus_agent.vaccinated_risk_multiplier
                if rand_num < probability_o:
                    off_campus_agent.change_state("E")
                    off_campus_agent.exposed_space = "Off-Campus"
            
            if day != 'S':
                for hour in SCHEDULE_HOURS:
                    all_transit_spaces.get(day)[hour-8].spread_infection_core()
                    for space in spaces:
                        if "Dorm" in str(space):
                            for dorm in space:
                                if hour != 8 or hour != 22:
                                    dorm.spread_infection_core(day_index, hour-8)
                                dorm.spread_infection_core(day_index, hour-8)
                            
                            for double_dorms in doubles_dorm_times[day_index][hour-8]:
                                double_dorms.spread_infection() # Spread infection in just the dorm

                        elif "Academic" in str(space):
                            if day in SCHEDULE_WEEKDAYS and hour in range(10, 18): # hour needs to be in range(10, 18)
                                if hour % 2 == 1:
                                    hour -= 1 # Academic spaces only stored in the even indices
                                for academic_building in space[day_index][int((hour / 2) - 5)]: #To turn hour into indices for the list of academic_buildings
                                    academic_building.spread_in_space()

                        else:
                            if type(space[day_index][hour-8]) is list:
                                for s in space[day_index][hour-8]:
                                    s.spread_in_space()
                            else:
                                space[day_index][hour-8].spread_in_space()

            else: # if day == 'S'
                for hour in SCHEDULE_HOURS: # Spread in the dorms for each hour (dorm spaces and then each double dorm)
                    for dorm in update_dorms:
                        dorm.spread_infection_core(3, hour-8) 
                        if hour != 8 or hour != 22:
                            dorm.spread_infection_core(3, hour-8) 
                        for doubles_dorm in dorm.doubles:
                            doubles_dorm.spread_infection()

                large_gatherings = [LargeGatherings(), LargeGatherings(), LargeGatherings()]
                for large_gathering in large_gatherings:
                    large_gathering.assign_agents(random.sample([agent for agent in agent_list if agent.social == True], k=random.randrange(20, 60)))
                    large_gathering.spread_infection()

            sim_data['new_exposures'].append(len([agent for agent in agent_list if agent.seir == "E" and agent.days_in_state == 0]))
            infected_agents = [agent for agent in agent_list if agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie" or agent.seir == "R"]
            sim_data['total_infections'].append(len(infected_agents))
            sim_data['seir_states']['s'].append(len([agent for agent in agent_list if agent.seir == "S"]))
            sim_data['seir_states']['e'].append(len([agent for agent in agent_list if agent.seir == "E"]))
            sim_data['seir_states']['i'].append(len([agent for agent in agent_list if agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie"]))
            sim_data['seir_states']['r'].append(len([agent for agent in agent_list if agent.seir == "R"]))
            change_states(agent_list)
            data[simulation_number] = sim_data
            #print("Day " + day + ", Week " + str(week) + ", # of Infected Agents: " + str(len(infected_agents)))
    print("Simulation finished.")

def input_stuff():
    print("How many simulations would you like to run with these interventions?")
    number_of_simulations = int(input())
    return number_of_simulations

if __name__ == "__main__":
    number_of_simulations = input_stuff()
    start_time = time.time()
    manager = Manager()
    data = manager.dict()
    data.update({sim_num: {} for sim_num in range(number_of_simulations + 1)})
    for i in range(number_of_simulations + 1):
        sim = data[i]
        sim['new_exposures'] = []
        sim['total_infections'] = []
        sim['seir_states'] = {'s': [], 'e': [], 'i': [], 'r': []}
        data[i] = sim
    pool = Pool() # creates an amount of processes from # of CPUs user has
    for sim_num in range(number_of_simulations):
        pool.apply_async(update, args=(data, sim_num))
    pool.close()
    pool.join()
    print("The program took " + str(time.time() - start_time) + " seconds to run")
    observe(data)
