import random
import CovidAgents
from CovidAgents import initialize_leaves, change_states
from Schedule import create_spaces, create_dorms, create_academic_spaces, assign_dorms, assign_agents_to_classes, assign_dining_times, assign_gym, assign_remaining_time
from global_constants import DORM_BUILDINGS, ACADEMIC_BUILDINGS, CLASSROOMS, SIMULATION_LENGTH, SCHEDULE_DAYS
from spaces import Dorm, Academic, LargeGatherings
from Schedule import all_transit_spaces

# Initialize agents
agent_list = CovidAgents.Agent().initialize()


def initialize():
    # Create spaces
    dorms = create_dorms()
    academic_buildings = create_academic_spaces([[[] for i in range(4)] for i in range(2)], [[[] for i in range(4)] for i in range(2)],
                                                [[[] for i in range(4)] for i in range(2)])  # Create a list for each day/hour combination for each division (STEM, Humanities, Arts)
    dining_hall_spaces = create_spaces("DiningHall", 13)  # We have unused Dining Hall spaces (at time 16) because the hours are not consecutive
    gym_spaces = create_spaces("Gym")
    library_spaces = create_spaces("Library")
    social_spaces = create_spaces("SocialSpace")
    stem_office_spaces = create_spaces("Office", 10, "STEM")
    arts_office_spaces = create_spaces("Office", 10, "Arts")
    humanities_office_spaces = create_spaces("Office", 10, "Humanities")
    off_campus_space = create_spaces("OffCampus")

    # Assign agents to spaces
    assign_dorms(dorms, agent_list)
    assign_agents_to_classes(academic_buildings, agent_list)
    assign_dining_times(agent_list, dining_hall_spaces)
    assign_gym(agent_list, gym_spaces)
    assign_remaining_time(agent_list, library_spaces, social_spaces, stem_office_spaces, arts_office_spaces, humanities_office_spaces, off_campus_space)


    """
    for day in social_spaces:
        print("New Day")
        for time in day:
            print("New Time")
            for social_space in time.leaves:
                print(len(social_space.agents))
    """

    """
    for agent in agent_list:
        print(agent.type)
        print(agent.schedule)

        transit_spaces = []

        for day in SCHEDULE_DAYS:
            for time in range(15):
                transit = all_transit_spaces[day][time]
                if agent in transit.agents:
                    transit_spaces.append([transit.day, transit.time])
        print(transit_spaces)
        print("----------------------------------------------------------------------------------------------------------------")

    # CODE TO CHECK IF TRANSIT SPACE ASSIGNMENT IS DONE PROPERLY
    for agent in agent_list:
        for day in SCHEDULE_DAYS:
            for i in range(14):
                day_schedule = agent.schedule.get(day)
                if day_schedule[i] != day_schedule[i + 1]:
                    # print("there should be transit space")
                    if agent not in all_transit_spaces[day][i + 1].agents:  # if agent is not assigned to a transit space that they are supposed to be assigned to
                        print("NOT IN TRANSIT SPACE")
    """
    return [dining_hall_spaces, gym_spaces, library_spaces, social_spaces, stem_office_spaces, humanities_office_spaces, arts_office_spaces,
            academic_buildings[0], academic_buildings[1], academic_buildings[2]] # Return a list containing all the spaces (to be used in update)


def update():
    # TODO: Add dorms (and an off-campus space)
    spaces = initialize()

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

            # TODO: Add special rule for off-campus space (each space is distinct with a day/time, but we want to spread infection with all of them at 8 AM)
            # TODO: Add special rule for Dorm spaces (they each hold an array of the agents in that space, separated by day and hour). Q: How do we send that over to update()?

            for space in spaces:
                if day_index < len(space):  # If the space is open on this day, then spread the infection [NOTE: This requires spaces in the array always be separated by A, B, and W in order]
                    for space_in_time in space[day_index]:
                        if type(space_in_time) is list:
                            for space in space_in_time:
                                space.spread_in_space()
                        else:
                            space_in_time.spread_in_space()
                exposed_agents = [agent for agent in agent_list if agent.seir == "E"]
                # print("# of Exposed Agents: " + str(len(exposed_agents)))
                # exit(0)
            change_states(agent_list)
            infected_agents = [agent for agent in agent_list if agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie" or agent.seir == "R"]
            print("Day " + day + ", Week " + str(week) + ", # of Infected Agents: " + str(len(infected_agents)))


update()


