import random
import CovidAgents
from CovidAgents import initialize_leaves, change_states
from Schedule import create_spaces, create_dorms, create_academic_spaces, assign_dorms, assign_agents_to_classes, assign_dining_times, assign_gym, \
    assign_remaining_time, all_transit_spaces, doubles_dorm_times
from global_constants import DORM_BUILDINGS, ACADEMIC_BUILDINGS, CLASSROOMS, SIMULATION_LENGTH, SCHEDULE_DAYS
from spaces import Dorm, Academic, LargeGatherings
from Schedule import all_transit_spaces

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

    return [dining_hall_spaces, gym_spaces, library_spaces, social_spaces, stem_office_spaces, humanities_office_spaces, arts_office_spaces , \
        academic_buildings[0], academic_buildings[1], academic_buildings[2], dorms] # Return a list containing all the spaces (to be used in update)


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
                    #print(space)
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
                exposed_agents = [agent for agent in agent_list if agent.seir == "E"]
                #print("# of Exposed Agents: " + str(len(exposed_agents)))
            change_states(agent_list)
            infected_agents = [agent for agent in agent_list if agent.seir == "Ia" or agent.seir == "Im" or agent.seir == "Ie" or agent.seir == "R"]
            print("Day " + day + ", Week " + str(week) + ", # of Infected Agents: " + str(len(infected_agents)))


update()


