import random
import CovidAgents
from CovidAgents import change_states, screening_test, return_screening_result
from Schedule import create_spaces, create_dorms, create_academic_spaces, assign_dorms, assign_agents_to_classes, \
    assign_dining_times, assign_gym, assign_remaining_time, all_transit_spaces, doubles_dorm_times
from global_constants import SCHEDULE_HOURS, SCHEDULE_WEEKDAYS, SIMULATION_LENGTH, INITIALLY_INFECTED, INTERVENTIONS, VACCINE_PERCENTAGE, WEEK_SCHEDULE,\
    SCREENING_PERCENTAGE, SCREENING_COMPLIANCE, LATENCY_PERIOD, TESTING_DAY_INDEX, COVID_VARIANTS, VACCINE_SELF, VACCINE_SPREAD, FACE_MASK_SELF, FACE_MASK_SPREAD
from spaces import Dorm, Academic, LargeGatherings
import matplotlib.pyplot as plt
import time
from statistics import stdev
from multiprocessing import Pool, Manager
import pickle
import copy

plt.rcParams.update({'figure.autolayout': True})  # A required line so the bar graph labels stay on the screen

agent_list = []  # list of all agents


def initialize():
    # Initialize agents
    global agent_list
    agent_list = CovidAgents.Agent().initialize()

    # Create spaces
    dorms = create_dorms()
    academic_buildings = create_academic_spaces([[[] for i in range(4)] for i in range(2)],
                                                [[[] for i in range(4)] for i in range(2)], \
                                                [[[] for i in range(4)] for i in range(
                                                    2)])  # Create a list for each day/hour combination for each division (STEM, Humanities, Arts)
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

    return [dining_hall_spaces, gym_spaces, library_spaces, social_spaces, stem_office_spaces, humanities_office_spaces,
            arts_office_spaces, academic_buildings[0], academic_buildings[1], academic_buildings[2], dorms]
            # Return a list containing all the spaces (to be used in update)


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
    data[0]['space_exposures'] = dict(sorted(data[0]['space_exposures'].items(), key=lambda item: item[1], reverse=True)) # TODO: Put back!
    """

    caI = pickle.load(open('pickle_files/interventions.p', 'rb'))
    caVP = pickle.load(open('pickle_files/vaccine_percentage.p', 'rb'))
    faculty_vaccine_percentage = caVP.get("Faculty") * 100
    student_vaccine_percentage = caVP.get("Student") * 100
    face_mask_intervention = caI.get("Face mask")

    number_of_simulations = len(data) - 1
    averaged_data = data[number_of_simulations]

    for day in range(len(data[0]['new_exposures'])):  # Set all days to 0 as default
        averaged_data['new_exposures'].append(0)
        averaged_data['total_infections'].append(0)

    for day in range(len(data[0]['new_exposures'])):  # NOTE: Requires simulation to have been run at least once
        for simulation_num in range(number_of_simulations):
            averaged_data['new_exposures'][day] += data[simulation_num]['new_exposures'][day]
            averaged_data['total_infections'][day] += data[simulation_num]['total_infections'][day]

    # Divide each element of the list by # of simulations to really take thee average
    averaged_data['new_exposures'] = [day / number_of_simulations for day in averaged_data['new_exposures']]
    averaged_data['total_infections'] = [day / number_of_simulations for day in averaged_data['total_infections']]

    ne_stdev = []  # new exposures
    ti_stdev = []  # total infections
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
    plt.title("% of Students Vaccinated: " + str(student_vaccine_percentage) + "\n% of Faculty Vaccinated: " +
              str(faculty_vaccine_percentage) + "\nFacemasks Required?: " + str(
        face_mask_intervention) + "\n# of Simulations: "
              + str(number_of_simulations))
    plt.xlabel("Day #")
    plt.ylabel("New Exposures")
    plt.savefig('images/new_exposures.png')
    plt.figure(1)
    for day in range(len(data[0]['total_infections'])):
        plt.errorbar(day, data[number_of_simulations]['total_infections'][day], yerr=ti_stdev[day], fmt='r^')
    plt.plot(range(len(data[0]['total_infections'])), data[number_of_simulations]['total_infections'])
    plt.title("% of Students Vaccinated: " + str(student_vaccine_percentage) + "\n% of Faculty Vaccinated: " +
              str(faculty_vaccine_percentage) + "\nFacemasks Required?: " + str(
        face_mask_intervention) + "\n# of Simulations: "
              + str(number_of_simulations))
    plt.xlabel("Day #")
    plt.ylabel("Total Infections")
    plt.savefig('images/total_infections.png')
    plt.figure(2)
    for seir_sim_num in range(number_of_simulations):
        plt.plot(range(len(data[seir_sim_num]['seir_states']['s'])), data[seir_sim_num]['seir_states']['s'], color='b')
        plt.plot(range(len(data[seir_sim_num]['seir_states']['e'])), data[seir_sim_num]['seir_states']['e'],
                 color='tab:orange')
        plt.plot(range(len(data[seir_sim_num]['seir_states']['i'])), data[seir_sim_num]['seir_states']['i'], color='r')
        plt.plot(range(len(data[seir_sim_num]['seir_states']['r'])), data[seir_sim_num]['seir_states']['r'], color='m')
    # Adding in plotting labels to legend
    plt.plot([], [], label="Susceptible Agents", color='b')
    plt.plot([], [], label="Exposed Agents", color='tab:orange')
    plt.plot([], [], label="Infected Agents", color='r')
    plt.plot([], [], label="Recovered Agents", color='m')
    plt.title("% of Students Vaccinated: " + str(student_vaccine_percentage) + "\n% of Faculty Vaccinated: " +
              str(faculty_vaccine_percentage) + "\nFacemasks Required?: " + str(
        face_mask_intervention) + "\n# of Simulations: "
              + str(number_of_simulations))
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
    student_list = [agent for agent in agent_list if agent.type != "Faculty"]
    off_campus_agents = [agent for agent in agent_list if agent.type == "Faculty" or agent.type == "Off-campus Student"]
    caI = pickle.load(open('pickle_files/interventions.p', 'rb'))
    screening_intervention = caI.get("Screening")  # whether we use screening test intervention or not ("on" or "off")
    testing_day = 0
    probability_o = 0.125 / len(off_campus_agents)
    sim_data['new_exposures'].append(0)
    sim_data['total_infections'].append(INITIALLY_INFECTED)

    for space in spaces:
        if "Dorm" in str(space):
            update_dorms = space

    # Infection spread in chronological order
    for week in range(SIMULATION_LENGTH):

        for day_of_week_index, day in enumerate(WEEK_SCHEDULE):  # ['A', 'B', 'A', 'B', 'W', 'W', 'S']
            day_index = 0  # Default day is 'A'
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
                    # WEEKLY SCREENING TEST EVERY MONDAY MORNING
                    if day_of_week_index == TESTING_DAY_INDEX and hour == 8 and screening_intervention is True:

                        # SCREENING TEST ON FIRST DAY OF SIMULATION
                        if week == 0:  # on the first day of the simulation, screening test all agents(including both student and faculty)
                            screening_test(agent_list)

                        else:  # week != 0:  # for each Monday, test a certain proportion of student agents
                            if week == 1:  # all agents got tested on the first week, so on the first week we need to select who will be screened from the list of all the student agents
                                not_tested = copy.copy(student_list)
                            else:  # starting from the second week, we exclude agents that were tested on the previous week
                                not_tested = [agent for agent in student_list if agent.screening_result[-1] == "Not tested" and agent.bedridden is False]

                            if len(not_tested) < int(len(student_list) * SCREENING_PERCENTAGE):  # if (# of agents not tested the previous week) < (# of agents that need to be tested each week)
                                weekly_testing_agents = not_tested + random.sample([agent for agent in student_list if agent not in not_tested],  # fill up the remaining number of agents
                                                                                   k=int(len(student_list) * SCREENING_PERCENTAGE) - len(not_tested))  # with agents that were tested the previous week

                            else:
                                weekly_testing_agents = random.sample(not_tested, k=int(len(student_list) * SCREENING_PERCENTAGE))

                            for agent in weekly_testing_agents:
                                if agent.seir in ["S", "E", "Ia"]:  # if agent doesn't have symptoms,
                                    rand_num = random.random()
                                    if rand_num < (1 - SCREENING_COMPLIANCE):  # agent may not comply with screening test by probability (1 - SCREENING_COMPLIANCE)
                                        weekly_testing_agents.remove(agent)

                            screening_test(weekly_testing_agents)  # selected and compliant agents do the screening test

                            for agent in student_list:  # for agents that weren't selected for screening tests, add "Not tested" to their result
                                if agent not in weekly_testing_agents:
                                    agent.screening_result.append("Not tested")

                    if day_of_week_index == TESTING_DAY_INDEX + LATENCY_PERIOD and hour == 8 and screening_intervention is True:
                        return_screening_result(agent_list)



                    all_transit_spaces.get(day)[hour - 8].spread_infection_core()
                    for space in spaces:
                        if "Dorm" in str(space):
                            for dorm in space:
                                if hour != 8 or hour != 22:
                                    dorm.spread_infection_core(day_index, hour - 8)
                                dorm.spread_infection_core(day_index, hour - 8)

                            for double_dorms in doubles_dorm_times[day_index][hour - 8]:
                                double_dorms.spread_infection()  # Spread infection in just the dorm

                        elif "Academic" in str(space):
                            if day in SCHEDULE_WEEKDAYS and hour in range(10, 18):  # hour needs to be in range(10, 18)
                                if hour % 2 == 1:
                                    hour -= 1  # Academic spaces only stored in the even indices
                                for academic_building in space[day_index][int((hour / 2) - 5)]:  # To turn hour into indices for the list of academic_buildings
                                    academic_building.spread_in_space()

                        else:
                            if type(space[day_index][hour - 8]) is list:
                                for s in space[day_index][hour - 8]:
                                    s.spread_in_space()
                            else:
                                space[day_index][hour - 8].spread_in_space()

            else:  # if day == 'S'
                for hour in SCHEDULE_HOURS:  # Spread in the dorms for each hour (dorm spaces and then each double dorm)
                    for dorm in update_dorms:
                        dorm.spread_infection_core(3, hour - 8)
                        if hour != 8 or hour != 22:
                            dorm.spread_infection_core(3, hour - 8)
                        for doubles_dorm in dorm.doubles:
                            doubles_dorm.spread_infection()

                large_gatherings = [LargeGatherings(), LargeGatherings(), LargeGatherings()]
                for large_gathering in large_gatherings:
                    large_gathering.assign_agents(random.sample([agent for agent in agent_list if agent.social is True], k=random.randrange(20, 60)))
                    large_gathering.spread_infection()

            sim_data['new_exposures'].append(len([agent for agent in agent_list if agent.seir == "E" and agent.days_in_state == 0]))
            infected_agents = [agent for agent in agent_list if agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie" or agent.seir == "R"]
            #infected_oncampus = [agent for agent in infected_agents if agent.type == "On-campus Student"]
            #infected_offcampus = [agent for agent in infected_agents if agent.type == "Off-campus Student"]
            #infected_faculty = [agent for agent in infected_agents if agent.type == "Faculty"]

            sim_data['total_infections'].append(len(infected_agents))
            sim_data['seir_states']['s'].append(len([agent for agent in agent_list if agent.seir == "S"]))
            sim_data['seir_states']['e'].append(len([agent for agent in agent_list if agent.seir == "E"]))
            sim_data['seir_states']['i'].append(
                len([agent for agent in agent_list if agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie"]))
            sim_data['seir_states']['r'].append(len([agent for agent in agent_list if agent.seir == "R"]))
            change_states(agent_list)
            data[simulation_number] = sim_data

            print("Day " + day + ", Week " + str(week) + ", # of Infected Agents: " + str(len(infected_agents)))

    vaccinated_agents = [agent for agent in agent_list if agent.vaccinated is True]
    # print(len(vaccinated_agents))
    #print([len(infected_oncampus), len(infected_offcampus), len(infected_faculty)])


    # Count infections in each space
    dhI, gI, lI, lgI, ssI, oI, aI, dI, tsI, ocI, other, nonI = (0,) * 12
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
        elif agent.exposed_space is not None:
            other += 1
        else:
            nonI += 1
    """
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


    print("Simulation finished.")


def input_stuff():

    # DETERMINE COVID VARIANT
    print("What COVID variant do you want? (A for Alpha/ D for Delta/ O for other)")
    covid_variant = input()
    while covid_variant not in ['A', 'D', 'O']:
        print("input should be either (A for Alpha/ D for Delta/ O for other)")
        covid_variant = input()
    if covid_variant == 'A':
        COVID_VARIANTS["Alpha"] = True
    elif covid_variant == 'D':
        COVID_VARIANTS["Delta"] = True
    elif covid_variant == 'O':
        COVID_VARIANTS["Other"] = True

    # VACCINE INTERVENTION
    print("Do you want to add vaccinated agents to the model? (Y/N)")
    vaccines = input()
    while vaccines not in ['Y', 'N']:
        print("input should be either (Y for Yes / N for No)")
        vaccines = input()
    if vaccines == 'Y':
        if covid_variant == 'O':  # if covid variant is neither alpha or delta, user needs to set the effectiveness of their own covid variant
            print("How effective are vaccines in preventing a susceptible agent from getting infected? (0 to 100)")
            vaccine_self = input()
            while not vaccine_self.isnumeric():
                print("input should be an integer between 0 and 100")
                vaccine_self = input()
            VACCINE_SELF["Other"] = int(vaccine_self) / 100.0
            print("How effective are vaccines in preventing an infected agent from spreading infection? (0 to 100)")
            vaccine_spread = input()
            while not vaccine_spread.isnumeric():
                print("input should be an integer between 0 and 100")
                vaccine_spread = input()
            VACCINE_SPREAD["Other"] = int(vaccine_spread) / 100.0

        INTERVENTIONS["Vaccine"] = True
        print("What percentage of students should be vaccinated? (0 to 100)")
        students_vax = input()
        VACCINE_PERCENTAGE["Student"] = int(students_vax) / 100.0
        print("What percentage of faculty should be vaccinated? (0 to 100)")
        faculty_vax = input()
        VACCINE_PERCENTAGE["Faculty"] = int(faculty_vax) / 100.0

    # FACE MASK INTERVENTION
    print("Do you want to add the face mask intervention to the model? (Y/N)")
    face_masks = input()
    while face_masks not in ['Y', 'N']:
        print("input should be either (Y for Yes / N for No)")
        face_masks = input()
    if face_masks == 'Y':
        INTERVENTIONS["Face mask"] = True
        if covid_variant == 'O':  # if covid variant is neither alpha or delta, user needs to set the effectiveness of their own covid variant
            print("How effective are face masks in preventing a susceptible agent from getting infected? (0 to 100)")
            face_mask_self = input()
            while not face_mask_self.isnumeric():
                print("input should be an integer between 0 and 100")
                face_mask_self = input()
            FACE_MASK_SELF["Other"] = int(face_mask_self) / 100.0
            print("How effective are face masks in preventing an infected agent from spreading infection? (0 to 100)")
            face_mask_spread = input()
            while not face_mask_spread.isnumeric():
                print("input should be an integer between 0 and 100")
                face_mask_spread = input()
            FACE_MASK_SPREAD["Other"] = int(face_mask_spread) / 100.0

    # SCREENING TEST INTERVENTION
    print("Do you want to add the screening test intervention to the model? (Y/N)")
    screening = input()
    while screening not in ['Y', 'N']:
        print("input should be either (Y for Yes / N for No)")
        screening = input()
    if screening == 'Y':
        INTERVENTIONS["Screening"] = True

    # NUMBER OF SIMULATIONS
    print("How many simulations would you like to run with these interventions? (positive integer)")
    num_of_simulations = input()
    while not num_of_simulations.isnumeric():
        print("input should be an integer larger than 0")
        num_of_simulations = input()

    pickle.dump([COVID_VARIANTS, [VACCINE_SELF, VACCINE_SPREAD], [FACE_MASK_SELF, FACE_MASK_SPREAD]], open('pickle_files/covid_variants.p', 'wb'))
    pickle.dump(INTERVENTIONS, open('pickle_files/interventions.p', 'wb'))
    pickle.dump(VACCINE_PERCENTAGE, open('pickle_files/vaccine_percentage.p', 'wb'))
    return num_of_simulations


if __name__ == "__main__":
    number_of_simulations = int(input_stuff())
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
    pool = Pool()  # creates an amount of processes from # of CPUs user has
    for sim_num in range(number_of_simulations):
        pool.apply_async(update, args=(data, sim_num))
    pool.close()
    pool.join()
    print("The program took " + str(time.time() - start_time) + " seconds to run")
    observe(data)
