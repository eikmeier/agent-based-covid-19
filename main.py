import random
import matplotlib.pyplot as plt
import time
from multiprocessing import Pool, Manager
import pickle
import numpy as np
import os
import csv
from covid_agents import change_states, Agent
from schedule import create_spaces, create_dorms, create_academic_spaces, assign_dorms, assign_agents_to_classes, assign_dining_times, \
    assign_gym, assign_remaining_time, all_transit_spaces, doubles_dorm_times
from global_constants import SCHEDULE_HOURS, SCHEDULE_WEEKDAYS, SIMULATION_LENGTH, INITIALLY_INFECTED, INTERVENTIONS, VACCINE_PERCENTAGE
from spaces import LargeGatherings

agent_list = [] # list of all agents

def initialize():
    # Initialize agents
    global agent_list
    agent_list = Agent().initialize()

    # Create spaces
    dorms = create_dorms()
    academic_buildings = create_academic_spaces() # Create a list for each day/hour combination for each division (STEM, Humanities, Arts)
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
    assign_remaining_time(agent_list, library_spaces, social_spaces, stem_office_spaces, arts_office_spaces, humanities_office_spaces)

    return [dining_hall_spaces, gym_spaces, library_spaces, social_spaces, stem_office_spaces, humanities_office_spaces, arts_office_spaces , \
        academic_buildings[0], academic_buildings[1], academic_buildings[2], dorms] # Return a list containing all the spaces (to be used in update)

def observe(data):
    # Figure out the spaces where everyone got exposed
    plt.rcParams.update({'figure.autolayout': True}) # A required line so the bar graph labels stay on the screen
    caI = pickle.load(open('pickle_files/interventions.p', 'rb'))
    caVP = pickle.load(open('pickle_files/vaccine_percentage.p', 'rb'))
    faculty_vaccine_percentage = caVP.get("Faculty") * 100
    student_vaccine_percentage = caVP.get("Student") * 100
    face_mask_intervention = caI.get("Face mask")
    number_of_simulations = len(data) - 1
    plot_parameters_str = "% of Students Vaccinated: " + str(student_vaccine_percentage) + "\n% of Faculty Vaccinated: " + str(faculty_vaccine_percentage) +\
    "\nFacemasks Required?: " + str(face_mask_intervention) + "\n# of Simulations: " + str(number_of_simulations)

    # Calculate medians
    median_data = data[number_of_simulations]
    for day in range(len(data[0]['new_exposures'])): # Set all days to 0 as default
        median_data['new_exposures'].append(0)
        median_data['total_infections'].append(0)
    for space_str in median_data['exposed_spaces'].keys(): # Set all spaces to 0 as default
        median_data['exposed_spaces'][space_str] = 0
    for day in range(len(data[0]['new_exposures'])):  # Calculate real median values for each day
        median_data['new_exposures'][day] = np.median(np.array([data[simulation_num]['new_exposures'][day] for simulation_num in range(number_of_simulations)]))
        median_data['total_infections'][day] = np.median(np.array([data[simulation_num]['total_infections'][day] for simulation_num in range(number_of_simulations)]))
    for space_str in data[0]['exposed_spaces'].keys(): # Calculate real median values for each space
        median_data['exposed_spaces'][space_str] = np.median(np.array([data[es_sim_num]['exposed_spaces'][space_str] for es_sim_num in range(number_of_simulations)]))
    median_data['exposed_spaces'] = dict(sorted(median_data['exposed_spaces'].items(), key=lambda item: item[1], reverse = True))

    ne_intervals = []  # new exposures
    ti_intervals = []  # total infections
    se_intervals = {}
    for space_str in data[0]['exposed_spaces'].keys():
        se_intervals.update({space_str : []})

    # Calculate Quartiles for each day
    for day in range(len(data[0]['new_exposures'])):
        day_list_ne = []
        day_list_ti = []
        for sim_1 in range(number_of_simulations):
            day_list_ne.append(data[sim_1]['new_exposures'][day])
            day_list_ti.append(data[sim_1]['total_infections'][day])
        ne_intervals.append((median_data['new_exposures'][day] - np.quantile(day_list_ne, .25), 
            np.quantile(day_list_ne, .75) - median_data['new_exposures'][day]))
        ti_intervals.append((median_data['total_infections'][day] - np.quantile(day_list_ti, .25), 
            np.quantile(day_list_ti, .75) - median_data['total_infections'][day]))

    for space_str in se_intervals.keys():
        space_exposures = []
        for sim_2 in range(number_of_simulations):
            space_exposures.append(data[sim_2]['exposed_spaces'][space_str])
        se_intervals[space_str].append((median_data['exposed_spaces'][space_str] - np.quantile(space_exposures, .25), 
            np.quantile(space_exposures, .75) - median_data['exposed_spaces'][space_str]))
    
    data[number_of_simulations] = median_data

    plt.figure(0) # Graph New Exposures
    plt.plot(range(len(data[0]['new_exposures'])), data[number_of_simulations]['new_exposures'], marker = '*', color = 'red')
    plt.errorbar(range(len(data[number_of_simulations]['new_exposures'])), data[number_of_simulations]['new_exposures'], yerr=np.array(ne_intervals).T,
     alpha=0.5, fmt='k', capsize=2)
    plt.title(plot_parameters_str)
    plt.xlabel("Day #")
    plt.ylabel("New Exposures")
    plt.grid(axis='y')
    plt.yticks(list(plt.yticks()[0])[1:] + [(plt.yticks()[0][1] - plt.yticks()[0][0]) + plt.yticks()[0][len(plt.yticks()[0]) - 1]])
    plt.savefig('images/new_exposures.png')

    plt.figure(1) # Graph Total Exposures
    plt.errorbar(range(len(data[number_of_simulations]['total_infections'])), data[number_of_simulations]['total_infections'], yerr=np.array(ti_intervals).T,
     alpha=0.5, fmt='k', capsize=2)
    plt.plot(range(len(data[0]['total_infections'])), data[number_of_simulations]['total_infections'], marker = '*', color = 'red')
    plt.title(plot_parameters_str)
    plt.xlabel("Day #")
    plt.ylabel("Total Infections")
    plt.grid(axis='y')
    plt.yticks(list(plt.yticks()[0])[1:] + [(plt.yticks()[0][1] - plt.yticks()[0][0]) + plt.yticks()[0][len(plt.yticks()[0]) - 1]])
    plt.savefig('images/total_infections.png')

    plt.figure(2) # Graph SEIR States
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
    plt.title(plot_parameters_str)
    plt.xlabel("Day #")
    plt.ylabel("# of Agents")
    plt.grid(axis='y')
    plt.yticks(list(plt.yticks()[0])[1:] + [(plt.yticks()[0][1] - plt.yticks()[0][0]) + plt.yticks()[0][len(plt.yticks()[0]) - 1]])
    plt.legend()
    plt.savefig('images/seir_states.png')

    plt.figure(3) # Graph exposures per space
    plt.xlabel("Spaces")
    plt.ylabel("# of Infections")
    plt.grid(axis='y', zorder=0)
    plt.xticks(rotation=45, ha="right")
    for space_str in se_intervals.keys():
        plt.errorbar(list(data[number_of_simulations]['exposed_spaces'].keys()).index(space_str), data[number_of_simulations]['exposed_spaces'][space_str], 
        yerr=np.array(se_intervals[space_str]).T, alpha=0.5, ecolor='black', capsize=4, zorder=4)
    plt.title(plot_parameters_str)
    plt.bar(data[number_of_simulations]['exposed_spaces'].keys(), data[number_of_simulations]['exposed_spaces'].values(), zorder=3)
    plt.yticks(list(plt.yticks()[0])[1:] + [(plt.yticks()[0][1] - plt.yticks()[0][0]) + plt.yticks()[0][len(plt.yticks()[0]) - 1]])
    plt.savefig('images/space_exposures.png')

    # Save median data (except for seir states which have no median calculated) to data file
    parameter_tuples = [("Faculty Vaccine %", faculty_vaccine_percentage), ("Student Vaccine %", student_vaccine_percentage), 
     ("Face Mask Intervention?", face_mask_intervention), ("Number of Simulations", number_of_simulations)]
    
    for data_section in data[0].keys():
        with open('data/' + str(data_section) + '.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(parameter_tuples)
            if data_section == 'seir_states':
                for sim_number in range(number_of_simulations):
                    for seir_state in data[number_of_simulations][data_section]:
                            writer.writerow(data[sim_number][data_section][seir_state])
            elif data_section == 'exposed_spaces':
                for space_tuple in list(data[number_of_simulations][data_section].items()):
                    writer.writerow(space_tuple)
            else:
                writer.writerow(data[number_of_simulations][data_section])

    plt.show()

def update(data, simulation_number):
    update_dorms = []
    sim_data = data[simulation_number]
    spaces = initialize()
    off_campus_agents = [agent for agent in agent_list if agent.off_campus]
    probability_o = 0.125 / len(off_campus_agents)
    sim_data['new_exposures'].append(0)
    sim_data['total_infections'].append(INITIALLY_INFECTED)

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
                probability_o *= off_campus_agent.vaccinated_self_risk_multiplier
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

            new_exposed_agents = [agent for agent in agent_list if agent.seir == "E" and agent.days_in_state == 0]
            sim_data['new_exposures'].append(len(new_exposed_agents))
            infected_agents = [agent for agent in agent_list if agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie" or agent.seir == "R"]
            sim_data['total_infections'].append(len(infected_agents))
            sim_data['seir_states']['s'].append(len([agent for agent in agent_list if agent.seir == "S"]))
            sim_data['seir_states']['e'].append(len([agent for agent in agent_list if agent.seir == "E"]))
            sim_data['seir_states']['i'].append(len([agent for agent in agent_list if agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie"]))
            sim_data['seir_states']['r'].append(len([agent for agent in agent_list if agent.seir == "R"]))
            for agent in new_exposed_agents:
                if str(agent.exposed_space) in sim_data['exposed_spaces']:
                    sim_data['exposed_spaces'][str(agent.exposed_space)] += 1
            change_states(agent_list)
            data[simulation_number] = sim_data
    print("Simulation finished.")

def input_stuff():
    print("Do you want to add vaccinated agents to the model? (Y/N)")
    vaccines = input()
    if vaccines == 'Y':
        INTERVENTIONS["Vaccine"] = True
        print("What percentage of students should be vaccinated? (0 to 100)")
        students_vax = input()
        VACCINE_PERCENTAGE["Student"] = int(students_vax) / 100.0
        print("What percentage of faculty should be vaccinated? (0 to 100)")
        faculty_vax = input()
        VACCINE_PERCENTAGE["Faculty"] = int(faculty_vax) / 100.0
    print("Do you want to add the facemask intervention to the model? (Y/N)")
    facemasks = input()
    if facemasks == 'Y':
        INTERVENTIONS["Face mask"] = True
    print("How many simulations would you like to run with these interventions?")
    number_of_simulations = int(input())
    pickle.dump(INTERVENTIONS, open('pickle_files/interventions.p', 'wb'))
    pickle.dump(VACCINE_PERCENTAGE, open('pickle_files/vaccine_percentage.p', 'wb'))
    return number_of_simulations

def create_directories():
    current_dir = os.getcwd()
    images_dir = current_dir + ('\images')
    pickle_dir = current_dir + ('\pickle_files')
    data_dir = current_dir + ('\data')
    directories = [images_dir, pickle_dir, data_dir]
    for dir in directories:
        if not os.path.exists(dir):
            os.makedirs(dir)

if __name__ == "__main__":
    create_directories()
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
        sim['exposed_spaces'] = {'Dorm': 0, 'Office': 0, 'Transit Space': 0, 'Dining Hall': 0, 'Library': 0, 'Gym': 0, 'Large Gatherings': 0, 
         'Academic': 0, 'Social Space': 0, 'Off-Campus': 0}
        data[i] = sim
    pool = Pool() # creates an amount of processes from # of CPUs user has
    for sim_num in range(number_of_simulations):
        pool.apply_async(update, args=(data, sim_num))
    pool.close()
    pool.join()
    print("The program took " + str(time.time() - start_time) + " seconds to run")
    observe(data)
