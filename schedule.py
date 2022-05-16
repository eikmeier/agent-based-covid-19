import random
import copy
from spaces import Dorm, Academic, TransitSpace, DiningHall, Gym, Library, SocialSpace, Office
from global_constants import DORM_BUILDINGS, ACADEMIC_BUILDINGS, PROBABILITY_G, PROBABILITY_S, PROBABILITY_L, \
    SCHEDULE_DAYS, SCHEDULE_WEEKDAYS

all_transit_spaces = {"A": [], "B": [], "W": []}  # Create transit spaces for each day and for each hour from 8-22
for day in SCHEDULE_DAYS:
    for time in range(15):
        all_transit_spaces[day].append(TransitSpace(day, time))

def create_spaces(space, start_hour=8, end_hour=22, break_times=None, open_days=SCHEDULE_DAYS, division=None):
    """
    Creates spaces from spaces.py with a given space, start_hour, end_hour, break_times, open_days, and division.\n
    By default, start_hour = 8 and end_hour = 22 to represent a full day (8 AM - 10 PM).\n
    break_times is a list of hours where the space is closed, open_days is a list of days where the space is open (of ['A', 'B', 'W']).\n
    Additionally, by default break_times is None and open_days is SCHEDULE_DAYS.\n
    Finally, division is None by default as most spaces do not have a division.\n
    A list of spaces, separated by days and then separated by hours is returned.\n
    Ex: [[DiningHall()], [DiningHall()], [DiningHall()], [DiningHall()], [DiningHall()], [DiningHall()]]
     if space = "DiningHall", start_hour = 13, end_hour = 15, break_times [14].\n
    """
    result = [[[] for j in range(15)] for i in range(3)]
    all_methods = globals().copy()
    space_class = all_methods.get(space)

    open_times = list(range(start_hour, end_hour + 1))

    if break_times is not None:
        for break_time in break_times:
            open_times.remove(break_time)

    for open_day in open_days:
        for hour in open_times:
            if open_day == 'A':
                day_index = 0
            elif open_day == 'B':
                day_index = 1
            elif open_day == 'W':
                day_index = 2
            if division is None:
                result[day_index][hour - 8] = space_class(open_day, hour)
            else:
                result[day_index][hour - 8] = space_class(division, open_day, hour)
    return result


def create_dorms():
    """
    Creates dorm buildings (25 small, 10 medium, 10 large) and returns all dorms in one list.\n
    """
    dorms = []
    for i in range(DORM_BUILDINGS.get("Small")):
        dorms.append(Dorm("Small"))
    for i in range(DORM_BUILDINGS.get("Medium")):
        dorms.append(Dorm("Medium"))
    for i in range(DORM_BUILDINGS.get("Large")):
        dorms.append(Dorm("Large"))
    return dorms

def create_academic_spaces():
    """
    Create academic buildings (STEM, Humanities, Arts) for class times (10 AM, 12 PM, 2 PM, 4 PM).\n
    Returns a list of academic buildings split up first by day ('A', 'B'), then by hour ('10', '12', '14', 16').\n
    The list looks like the following:
     [[[List of Buildings], [List of Buildings], [List of Buildings], [List of Buildings]], [[List of Buildings], [List of Buildings], [List of Buildings], [List of Buildings]]]
    """
    academic_buildings = [[[[] for i in range(4)] for j in range(2)] for k in range(3)]
    for i in range(8):
        for index, building_list in enumerate(academic_buildings):
            day_type = 'A'  # Default, if i // 4 == 0
            if i // 4 == 1:
                day_type = 'B'

            division = "STEM"  # Default, if index == 0
            if index == 1:
                division = "Humanities"
            elif index == 2:
                division = "Arts"

            for building_size in range(len(ACADEMIC_BUILDINGS.get(division))):
                for k in range(ACADEMIC_BUILDINGS.get(division)[building_size]):  # k is unused
                    size = "Small"  # By default, size is small (building_size == 0)
                    if building_size == 1:
                        size = "Medium"
                    elif building_size == 2:
                        size = "Large"
                    building_list[i // 4][i % 4].append(Academic(size, day_type, 2 + 2 * (i % 4)))
    return academic_buildings

def assign_meal(agent, day, start_hour, end_hour, dh_list):
    """
    Assigns a meal to an agent on a given day, start_hour, and end_hour.\n
    Takes in a day (a character that is either 'A', 'B', or 'W'), a start_hour and an end hour
     (a number between 8-20 to represent when agents are doing activities)
     and a Dining Hall array that is storing the spaces used to assign agents to the Dining Hall.
    """
    day_index = 0  # By default, if day == 'A'
    if day == 'B':
        day_index = 1
    elif day == 'W':
        day_index = 2
    possible_meal_hours = agent.get_available_hours(start_hour, end_hour, day)
    if possible_meal_hours:
        meal_hour = random.choice(possible_meal_hours)
        dh_list[day_index][meal_hour].assign_agent(agent)
        if agent.schedule[day][meal_hour - 1] != "Dining Hall":  # If agent's last location is not Dining Hall...
            all_transit_spaces[day][meal_hour].agents.append(
                agent)  # assign agent to transit space at corresponding [day, time]

doubles_students = []
# List of doubles dorm rooms when at least one student is in it at a specific day, time combination
temp_doubles_dorm_times = [[[] for j in range(15)] for i in range(3)]
# List of doubles dorm rooms when both students are in it at a specific day, time combination
doubles_dorm_times = [[[] for j in range(15)] for i in range(3)]

def assign_dorms(dorms, agent_list):
    """
    Takes in a list of dorms and a list of all agents.\n
    Randomly assigns on-campus students to dorms and subsequently assigns off_campus_agents to an off campus space.\n
    """
    on_campus_students = [agent for agent in agent_list if agent.student and not agent.off_campus]
    off_campus_agents = [agent for agent in agent_list if agent.off_campus]
    for agent in on_campus_students:
        for day in SCHEDULE_DAYS:  # For on-campus students, each day begins and ends in their assigned dorm room at 8 and 22.
            agent.schedule[day][0] = "Dorm"
            agent.schedule[day][14] = "Dorm"
        random.shuffle(dorms)
        for dorm_building in dorms:
            agent.dorm_room = dorm_building.assign_agent(agent)
            if agent.dorm_room:
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
                agent.schedule['W'][hour] = "Off-Campus Space"  # Off-Campus agents remain off-campus for the entire day

# CLASS ASSIGNMENT ------------------------------------------------------------------------------------------------------------------------------------
def assign_agents_to_classes(academic_buildings, agent_list):
    """
    Takes in a list of academic_buildings, ideally created from create_academic_buildings(), and a list of agents.\n
    Assigns students and faculty each to classes.\n
    """
    faculty = [agent for agent in agent_list if not agent.student]
    assign_faculty_classes(academic_buildings, faculty)
    students = [agent for agent in agent_list if agent.student]
    assign_student_classes(academic_buildings, students)

def assign_faculty_classes(academic_buildings, faculty_list):
    """
    Takes in a list of academic_buildings, ideally created from create_academic_buildings(), and a list of faculty.\n
    Assigns faculty to two classes.\n
    """
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
                        if faculty.schedule.get(building.day)[
                            building.time + 2] == building:  # If the agent is in the same Academic space in 2 hours (after this class finishes)
                            all_transit_spaces[building.day][building.time].agents.remove(
                                faculty)  # Remove agent from being in the transit space during this hour
                        elif faculty.schedule.get(building.day)[
                            building.time - 1] != building:  # If the agent is in a different space in the previous hour
                            all_transit_spaces[building.day][building.time].agents.append(
                                faculty)  # assign agent to transit space at corresponding [day, time]
                        if faculty.num_of_classes == 2:  # if agent is already assigned to 2 classes, remove them from list
                            division_faculty.remove(faculty)

                    if len(select_faculty) < class_num:  # after assigning all selected faculty, if building is not full (with faculty) and has remaining classrooms that need faculty assigned
                        remaining_buildings.append(building)

    remaining_faculty = [faculty for division in faculty_by_division for faculty in division]

    for faculty in copy.copy(remaining_faculty):
        for building in copy.copy(remaining_buildings):
            if faculty.schedule.get(building.day)[building.time] == None:
                classroom = building.assign_agent(faculty)  # assign agent to a classroom
                if faculty.schedule.get(building.day)[building.time + 2] == building:  # If the agent is in the same Academic space in 2 hours (after this class finishes)
                    all_transit_spaces[building.day][building.time].agents.remove(
                        faculty)  # Remove agent from being in the transit space during this hour
                elif faculty.schedule.get(building.day)[building.time - 1] != building:  # If the agent is in a different space in the previous hour
                    all_transit_spaces[building.day][building.time].agents.append(
                        faculty)  # assign agent to transit space at corresponding [day, time]
                if classroom == None:
                    remaining_buildings.remove(building)
                else:
                    remaining_faculty.remove(faculty)
                    break  # No need to go through the other buildings for this faculty since they have been successfully assigned

def assign_student_classes(academic_buildings, student_list):
    """
    Takes in a list of academic_buildings, ideally created from create_academic_buildings(), and a list of students.\n
    Assigns students to four classes.\n
    """
    time_range = [2, 4, 6, 8]  # index of time slots for classes
    day_time = [[day, time] for day in SCHEDULE_WEEKDAYS for time in time_range]  # [day, time] combinations for classes
    # First randomly assign an agent's 2 division classes
    for agent in student_list:
        # Class assignment for each day & time
        agent.class_times = random.sample(day_time, k=4)
        division_index = agent.get_division_index()

        while agent.num_of_classes < 2:  # select two classes within agent's division
            class_time = agent.class_times[agent.num_of_classes]

            # We want to get a building from this division, at the time and day we have been given, and then assign an agent to that space.
            day = 0  # By default, if day (class_time[0]) == 'A'
            if class_time[0] == 'B':
                day = 1

            division_spaces = academic_buildings[division_index][day][int((class_time[1] - 2) / 2)]
            for space in copy.copy(division_spaces):
                classroom = space.assign_agent(agent)
                if classroom != None:
                    if agent.schedule.get(class_time[0])[class_time[
                                                             1] + 2] == space:  # If the agent is in the same Academic space after this class finishes
                        all_transit_spaces[class_time[0]][class_time[1]].agents.remove(
                            agent)  # Remove agent from being in the transit space during this hour
                    elif agent.schedule.get(class_time[0])[
                        class_time[1] - 1] != space:  # If the agent is in a different space in the previous hour
                        all_transit_spaces[class_time[0]][class_time[1]].agents.append(
                            agent)  # assign agent to transit space at corresponding [day, time]
                    break

    # Next, randomly assign 2 non-division classes
    for agent in student_list:
        while agent.num_of_classes < 4:  # select two classes regardless of agent's division
            class_time = agent.class_times[agent.num_of_classes]
            # We want to get a building from this division, at the time and day we have been given, and then assign an agent to that space.
            day = 0  # Day is by default 'A'
            if class_time[0] == 'B':
                day = 1
            other_spaces = academic_buildings[random.randint(0, 2)][day][int((class_time[1] - 2) / 2)]
            for space in other_spaces:
                classroom = space.assign_agent(agent)
                if classroom is not None:
                    if agent.schedule.get(class_time[0])[class_time[
                                                             1] + 2] == space:  # If the agent is in the same Academic space in 2 hours (after this class finishes)
                        all_transit_spaces[class_time[0]][class_time[1]].agents.remove(
                            agent)  # Remove agent from being in the transit space during this hour
                    elif agent.schedule.get(class_time[0])[
                        class_time[1] - 1] != space:  # If the agent is in a different space in the previous hour
                        all_transit_spaces[class_time[0]][class_time[1]].agents.append(
                            agent)  # assign agent to transit space at corresponding [day, time]
                    break

def assign_dining_times(dining_hall_spaces, agent_list):
    """
    Takes in a list of dining hall spaces and a list of agents.\n
    Assigns each agent times to eat in the Dining Hall, utilizing the assign_meal() method.\n
    """
    for agent in agent_list:  # Assign dining hall times to all agents
        if agent.off_campus:
            for day in SCHEDULE_WEEKDAYS:
                assign_meal(agent, day, 12, 15, dining_hall_spaces)
        elif not agent.student:
            for day in SCHEDULE_WEEKDAYS:
                assign_meal(agent, day, 11, 13, dining_hall_spaces)
        else:
            for day in SCHEDULE_DAYS:
                assign_meal(agent, day, 8, 11, dining_hall_spaces)
                assign_meal(agent, day, 12, 15, dining_hall_spaces)
                assign_meal(agent, day, 17, 20, dining_hall_spaces)

def assign_gym(gym_spaces, agent_list):
    """
    Takes in a list of gym spaces and a list of agents.\n
    Randomly assigns students to the gym based on their pre-existing schedule.\n
    """
    for student in [agent for agent in agent_list if agent.student]:
        for count, day in enumerate(SCHEDULE_DAYS):
            if day == 'W' and student.off_campus:
                break
            rand_prob = random.random()
            if rand_prob < PROBABILITY_G:
                available_times = student.get_available_hours(8, 22, day)
                if available_times:  # Assign the time as long as the agent has any available times to go to the gym during the day
                    gym_hour = random.choice(available_times)
                    gym_spaces[count][gym_hour].assign_agent(student)
                    all_transit_spaces[day][gym_hour].agents.append(student)

def assign_remaining_time(library_spaces, social_spaces, stem_office_spaces, humanities_office_spaces,
                          arts_office_spaces, agent_list):
    """
    Takes in a list of library spaces, social spaces, STEM office spaces, Humanities office spaces, Arts office spaces,
     and a list of agents.\n
    Assigns all agents to the aforementioned spaces based on their pre-existing schedule.\n
    """
    for agent in agent_list:
        if agent.student:
            for count, day in enumerate(SCHEDULE_DAYS):
                for hour in agent.get_available_hours(8, 22, day):
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
                        if agent.student and not agent.off_campus:
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
            if agent.off_campus:
                for day in SCHEDULE_DAYS:
                    if agent.schedule[day][9] != "Off-Campus Space":
                        all_transit_spaces[day][10].agents.append(agent)
            else:  # if agent is an on-campus student
                for day in SCHEDULE_DAYS:
                    if agent.schedule[day][13] != "Dorm":
                        all_transit_spaces[day][14].agents.append(agent)
        else:
            for count, day in enumerate(SCHEDULE_WEEKDAYS):
                all_transit_spaces[day][10].agents.append(
                    agent)  # All faculty must enter the transit vertex at time 10 in order to get back to their off-campus space
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