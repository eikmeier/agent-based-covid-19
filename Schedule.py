import random
import copy
import CovidAgents
import spaces
from spaces import Dorm, Academic, DiningHall, Gym, Library, SocialSpace, Office, TransitSpace
from global_constants import DORM_BUILDINGS, ACADEMIC_BUILDINGS, PROBABILITY_G, PROBABILITY_S, PROBABILITY_L, \
    SCHEDULE_DAYS, SCHEDULE_WEEKDAYS, CLASS_TIMES, CLASSROOMS

all_transit_spaces = {"A": [], "B": [], "W": []}  # time range is from 8 ~ 22, which is 15 blocks & class times are at index 2, 4, 6, 8
for day in SCHEDULE_DAYS:
    for time in range(15):
        all_transit_spaces[day].append(spaces.TransitSpace(day, time))

def create_spaces(space, num_hours = 15, division = None):
    """
    Creates spaces from spaces.py with a given space, num_hours, and division.\n
    By default, num_hours = 15 to represent a full day (8 AM - 10 PM) and division is None
     as most spaces do not have a division.\n
    A list of spaces, separated by days and then separated by hours is returned.
     Ex: [[DiningHall()], [DiningHall()], [DiningHall()], [DiningHall()], [DiningHall()], [DiningHall()]]
     if num_hours = 2.\n
    """
    result = [[[] for j in range(num_hours)] for i in range(3)]
    all_methods = globals().copy()
    space_class = all_methods.get(space)
    for i in range(3):
        for j in range(num_hours):
            day = 'W'
            if i % 3 == 0:
                day = 'A'
            elif i % 3 == 1:
                day = 'B'
            if division is None:
                result[i % 3][j % num_hours] = space_class(day, j)
            else:
                result[i % 3][j % num_hours] = space_class(division, day, j)
    return result

def create_dorms():
    # Create dorm buildings (25 small, 10 medium, 10 large)
    dorms = []
    for i in range(DORM_BUILDINGS.get("Small")):
        dorms.append(Dorm("Small"))
    for i in range(DORM_BUILDINGS.get("Medium")):
        dorms.append(Dorm("Medium"))
    for i in range(DORM_BUILDINGS.get("Large")):
        dorms.append(Dorm("Large"))
    return dorms

def create_academic_spaces(stem_buildings, humanities_buildings, arts_buildings):
    # create academic buildings (STEM, Humanities, Arts) for class times ([10AM, 12PM, 14PM, 16PM] - index [2, 4, 6, 8])
    # one list of all the classrooms at specific day(A or B) and time (2, 4, 6, 8)

    # create all buildings at all day and times -> First list is split up by Day A and then Day B. Then list is split up by times (10, 12, 14, 16). Then,
    # finally, each entry at a specific day and time contains all academic buildings.
    academic_buildings = [stem_buildings, humanities_buildings, arts_buildings]
    for i in range(8):
        for index, building_list in enumerate(academic_buildings):
            if i // 4 == 0:
                day_type = 'A'
            else:
                day_type = 'B'

            if index == 0:
                division = "STEM"
            elif index == 1:
                division = "Humanities"
            else: # index == 2
                division = "Arts"

            for j in range(ACADEMIC_BUILDINGS.get(division)[0]):
                building_list[i // 4][i % 4].append(Academic("Small", day_type, 2 + 2 * (i % 4)))
            for k in range(ACADEMIC_BUILDINGS.get(division)[1]):
                building_list[i // 4][i % 4].append(Academic("Medium", day_type, 2 + 2 * (i % 4)))
            for l in range(ACADEMIC_BUILDINGS.get(division)[2]):
                building_list[i // 4][i % 4].append(Academic("Large", day_type, 2 + 2 * (i % 4)))
    return academic_buildings

def assign_meal(agent, day, start_hour, end_hour, dhArr):
    """
    Assigns a meal to an agent on a given day, start_hour, and end_hour.\n
    Takes in a day (a character that is either 'A', 'B', or 'W'), a start_hour and an end hour
     (a number between 8-20 to represent when agents are doing activities)
     and a Dining Hall array that is storing the spaces used to assign agents to the Dining Hall.
    """
    day_index = 0
    if day == 'B':
        day_index = 1
    elif day == 'W':
        day_index = 2
    possible_meal_hours = agent.get_available_hours(start_hour, end_hour, day)
    if possible_meal_hours:
        meal_hour = random.choice(possible_meal_hours)
        dhArr[day_index][meal_hour].assign_agent(agent)
        if agent.schedule[day][meal_hour - 1] != "Dining Hall":  # If previous agent's location is not Dining Hall,
            all_transit_spaces[day][meal_hour].agents.append(agent)  # assign agent to transit space at corresponding [day, time]

doubles_students = []
temp_doubles_dorm_times = [[[] for j in range(15)] for i in range(3)]
doubles_dorm_times = [[[] for j in range(15)] for i in range(3)]

def assign_dorms(dorms, agent_list):
    # randomly assigns agents(on-campus students) to dorms
    on_campus_students = [agent for agent in agent_list if agent.type == "On-campus Student"]
    off_campus_agents = [agent for agent in agent_list if agent.type != "On-campus Student"]
    for agent in on_campus_students:
        for day in SCHEDULE_DAYS:  # For on-campus students, each day begins and ends in their assigned dorm room at 8 and 22.
            agent.schedule[day][0] = "Dorm"
            agent.schedule[day][14] = "Dorm"
        random.shuffle(dorms)
        for dorm_building in dorms:
            agent.dorm_room = dorm_building.assign_agent(agent)
            if agent.dorm_room != False:
                if agent.dorm_room in dorm_building.doubles:
                    doubles_students.append(agent)
                    # Put in all double rooms with two agents living in the dorm to doubles_dorm_times at both 8 and 22, since we know
                    #  all agents will be in their room at those times
                    if agent.dorm_room not in temp_doubles_dorm_times[0][0]: 
                        for day in range(len(SCHEDULE_DAYS)):
                            temp_doubles_dorm_times[day][0].append(agent.dorm_room)
                            temp_doubles_dorm_times[day][14].append(agent.dorm_room)
                    else:
                        for day in range(len(SCHEDULE_DAYS)):
                            doubles_dorm_times[day][0].append(agent.dorm_room)
                            doubles_dorm_times[day][14].append(agent.dorm_room)
                break

    for agent in off_campus_agents:  # For off-campus students, A and B days begin and end at their off-campus house at times 8, 9 and 18–22.
        for day in SCHEDULE_WEEKDAYS:
            for hour in range(15):
                if hour == 0 or hour == 1 or 10 <= hour <= 14:  # hour >= 10 and hour <= 14:
                    agent.schedule[day][hour] = "Off-Campus Space"
                agent.schedule['W'][hour] = "Off-Campus Space" # Off-Campus agents remain off-campus for the entire day
            
# CLASS ASSIGNMENT ------------------------------------------------------------------------------------------------------------------------------------

def assign_agents_to_classes(academic_buildings, agent_list):
    faculty = [agent for agent in agent_list if agent.type == "Faculty"]
    students = [agent for agent in agent_list if agent.type != "Faculty"]

    assign_faculty_classes(academic_buildings, faculty)
    assign_student_classes(academic_buildings, students)

def assign_faculty_classes(academic_buildings, faculty_list):
    # list of faculty by division
    stem_faculty = [faculty for faculty in faculty_list if faculty.division == "STEM"]
    humanities_faculty = [faculty for faculty in faculty_list if faculty.division == "Humanities"]
    arts_faculty = [faculty for faculty in faculty_list if faculty.division == "Arts"]
    faculty_by_division = [stem_faculty, humanities_faculty, arts_faculty]
    remaining_buildings = []

    for division in academic_buildings:
        division_index = academic_buildings.index(division)
        division_faculty = faculty_by_division[division_index]

        for day in division:
            for time in day:
                for building in time:
                    class_num = len(building.classrooms)  # number of classrooms in building
                    select_faculty = []
                    zero_class_faculty = [faculty for faculty in division_faculty if faculty.num_of_classes == 0]
                    one_class_faculty = [faculty for faculty in division_faculty if faculty.num_of_classes == 1]
                    random.shuffle(zero_class_faculty)
                    random.shuffle(one_class_faculty)
                    for faculty in copy.copy(zero_class_faculty + one_class_faculty):
                        if len(select_faculty) == class_num:
                            break
                        elif faculty.num_of_classes == 1:
                            # if faculty is already assigned to one class with the same [day, time] as the current building, exclude from selection
                            if faculty.schedule.get(building.day)[building.time] == None:
                                select_faculty.append(faculty)
                        else:
                            select_faculty.append(faculty)
                    for faculty in select_faculty:
                        building.assign_agent(faculty)  # assign agent to a classroom
                        if faculty.schedule.get(building.day)[building.time + 2] == building: # If the agent is in the same Academic space in 2 hours (after this class finishes)
                            all_transit_spaces[building.day][building.time].agents.remove(faculty) # Remove agent from being in the transit space during this hour
                        elif faculty.schedule.get(building.day)[building.time - 1] != building:  # If the agent is in a different space in the previous hour
                            all_transit_spaces[building.day][building.time].agents.append(faculty)  # assign agent to transit space at corresponding [day, time]
                        if faculty.num_of_classes == 2:  # if agent is already assigned to 2 classes, remove them from list
                            division_faculty.remove(faculty)

                    if len(select_faculty) < class_num:  # after assigning all selected faculty, if building is not full (with faculty) and has remaining classrooms that need faculty assigned
                        remaining_buildings.append(building)

    remaining_faculty = [faculty for division in faculty_by_division for faculty in division]

    for faculty in copy.copy(remaining_faculty):
        for building in copy.copy(remaining_buildings):
            if faculty.schedule.get(building.day)[building.time] == None:
                classroom = building.assign_agent(faculty)  # assign agent to a classroom
                if faculty.schedule.get(building.day)[building.time + 2] == building: # If the agent is in the same Academic space in 2 hours (after this class finishes)
                    all_transit_spaces[building.day][building.time].agents.remove(faculty) # Remove agent from being in the transit space during this hour
                elif faculty.schedule.get(building.day)[building.time - 1] != building:  # If the agent is in a different space in the previous hour
                    all_transit_spaces[building.day][building.time].agents.append(faculty)  # assign agent to transit space at corresponding [day, time]
                if classroom == None:
                    remaining_buildings.remove(building)
                else:
                    remaining_faculty.remove(faculty)
                    break # No need to go through the other buildings for this faculty since they have been successfully assigned

def assign_student_classes(academic_buildings, student_list):
    time_range = [2, 4, 6, 8]  # index of time slots for classes
    day_time = [[day, time] for day in SCHEDULE_WEEKDAYS for time in time_range] # [day, time] combinations for classes
    # First randomly assign an agent's 2 division classes
    for agent in student_list:
        # Class assignment for each day & time
        agent.class_times = random.sample(day_time, k=4)
        division_index = agent.get_division_index()

        while agent.num_of_classes < 2:  # select two classes within agent's division
            class_time = agent.class_times[agent.num_of_classes]

            # We want to get a building from this division, at the time and day we have been given, and then assign an agent to that space.
            day = 0
            if class_time[0] == 'B':
                day = 1
            
            division_spaces = academic_buildings[division_index][day][int((class_time[1] - 2) / 2)]
            for space in copy.copy(division_spaces):
                classroom = space.assign_agent(agent)
                if classroom != None:
                    if agent.schedule.get(class_time[0])[class_time[1] + 2] == space: # If the agent is in the same Academic space in 2 hours (after this class finishes)
                        all_transit_spaces[class_time[0]][class_time[1]].agents.remove(agent) # Remove agent from being in the transit space during this hour
                    elif agent.schedule.get(class_time[0])[class_time[1] - 1] != space:  # If the agent is in a different space in the previous hour
                        all_transit_spaces[class_time[0]][class_time[1]].agents.append(agent)  # assign agent to transit space at corresponding [day, time]
                    break

    # Next, randomly assign 2 non-division classes
    for agent in student_list:
        while agent.num_of_classes < 4:  # select two classes regardless of agent's division
            class_time = agent.class_times[agent.num_of_classes]
            # We want to get a building from this division, at the time and day we have been given, and then assign an agent to that space.
            day = 0 # Day is by default 'A'
            if class_time[0] == 'B':
                day = 1
            other_spaces = academic_buildings[random.randint(0, 2)][day][int((class_time[1] - 2) / 2)]
            for space in other_spaces:
                classroom = space.assign_agent(agent)
                if classroom is not None:
                    if agent.schedule.get(class_time[0])[class_time[1] + 2] == space: # If the agent is in the same Academic space in 2 hours (after this class finishes)
                        all_transit_spaces[class_time[0]][class_time[1]].agents.remove(agent) # Remove agent from being in the transit space during this hour
                    elif agent.schedule.get(class_time[0])[class_time[1] - 1] != space:  # If the agent is in a different space in the previous hour
                        all_transit_spaces[class_time[0]][class_time[1]].agents.append(agent)  # assign agent to transit space at corresponding [day, time]
                    break

# DINING HALL / GYM / LIBRARY ####################################################################################################################
def assign_dining_times(dining_hall_space, agent_list):
    for agent in agent_list:  # Assign dining hall times to all agents
        if agent.type == "Off-campus Student":
            for day in SCHEDULE_WEEKDAYS:
                assign_meal(agent, day, 12, 15, dining_hall_space)
        elif agent.type == "Faculty":
            for day in SCHEDULE_WEEKDAYS:
                assign_meal(agent, day, 11, 13, dining_hall_space)
        else:
            for day in SCHEDULE_DAYS:
                assign_meal(agent, day, 8, 11, dining_hall_space)
                assign_meal(agent, day, 12, 15, dining_hall_space)
                assign_meal(agent, day, 17, 20, dining_hall_space)

def assign_gym(agent_list, gym_spaces):
    # Try to assign Gym slots
    for agent in agent_list:
        if agent.type != "Faculty":
            for count, day in enumerate(SCHEDULE_DAYS):
                if day == 'W' and agent.type == "Off-campus Student":
                    break
                rand_prob = random.random()
                if rand_prob < PROBABILITY_G:
                    available_times = agent.get_available_hours(8, 22, day)
                    if available_times: # Assign the time as long as the agent has any available times to go to the gym during the day
                        gym_hour = random.choice(available_times)
                        gym_spaces[count][gym_hour].assign_agent(agent)
                        all_transit_spaces[day][gym_hour].agents.append(agent)


# Remaining slots for social spaces, library leaf, or dorm room
def assign_remaining_time(agent_list, library_spaces, social_spaces, stem_office_spaces, humanities_office_spaces, arts_office_spaces):
    for agent in agent_list:
        if agent.type != "Faculty":
            for count, day in enumerate(SCHEDULE_DAYS):
                for hour in agent.get_available_hours(8, 22, day):
                    if day == 'W' and agent.type == "Off-campus Student":
                        break
                    rand_number = random.random()
                    if rand_number < PROBABILITY_S:  # Assign social space
                        social_spaces[count][hour].assign_agent(agent)
                        if agent.schedule[day][hour - 1] != "Social Space":
                            all_transit_spaces[day][hour].agents.append(agent)

                    elif rand_number < PROBABILITY_S + PROBABILITY_L:  # Assign library space
                        library_spaces[count][hour].assign_agent(agent)
                        if agent.schedule[day][hour - 1] != "Library":
                            all_transit_spaces[day][hour].agents.append(agent)

                    else:  # Assign dorm room if on-campus, otherwise assign off-campus
                        if agent.type == "On-campus Student":
                            agent.schedule.get(day)[hour] = "Dorm"
                            agent.dorm_room.space.assign_agent_during_day(agent, day, hour)
                            if agent in doubles_students:
                                if agent.dorm_room in temp_doubles_dorm_times[count][hour]:
                                    doubles_dorm_times[count][hour].append(agent.dorm_room)
                                else:
                                    temp_doubles_dorm_times[count][hour].append(agent.dorm_room)
                            if agent.schedule[day][hour - 1] != "Dorm":
                                all_transit_spaces[day][hour].agents.append(agent)
                        else:
                            agent.schedule[day][hour] = "Off-Campus Space"
                            if agent.schedule[day][hour - 1] != "Off-Campus Space":
                                all_transit_spaces[day][hour].agents.append(agent)

            # Show that an agent has to go into the transit vertex to go back to their place of residence for the rest of the day
            if agent.type == "On-campus Student":
                for day in SCHEDULE_DAYS:
                    if agent.schedule[day][13] != "Dorm":
                        all_transit_spaces[day][14].agents.append(agent) 
            else:  # if agent.type == "Off-campus Student"
                for day in SCHEDULE_WEEKDAYS:
                    if agent.schedule[day][9] != "Off-Campus Space":
                        all_transit_spaces[day][10].agents.append(agent)
        else:
            for count, day in enumerate(SCHEDULE_WEEKDAYS):
                all_transit_spaces[day][10].agents.append(agent) # All faculty must enter the transit vertex at time 10 in order to get back to their off-campus space
                for hour in agent.get_available_hours(8, 22, day):
                    # Put into appropriate Division Office vertex
                    if agent.division == "STEM":
                        stem_office_spaces[count][hour].assign_agent(agent)
                    elif agent.division == "Arts":
                        arts_office_spaces[count][hour].assign_agent(agent)
                    else:  # Agent's division is Humanities
                        humanities_office_spaces[count][hour].assign_agent(agent)
                    if agent.schedule[day][hour - 1] != "Office":
                        all_transit_spaces[day][hour].agents.append(agent)
