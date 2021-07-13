import random
import copy
import CovidAgents
import spaces
from spaces import Dorm, Academic, DiningHall, Gym, Library, SocialSpace, OffCampus, Office, TransitSpace
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


def assign_dorms(dorms, on_campus_students, off_campus_students):
    # list of available dorms that are not fully occupied
    available_dorms = copy.copy(dorms)

def assign_dorms(dorms, agent_list):
    # randomly assigns agents(on-campus students) to dorms
    on_campus_students = [agent for agent in agent_list if agent.type == "On-campus Student"]
    off_campus_students = [agent for agent in agent_list if agent.type == "Off-campus Student"]
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
                break

    for agent in off_campus_students:  # For off-campus students, A and B days begin and end at their off-campus house at times 8, 9 and 18–22.
        for day in SCHEDULE_WEEKDAYS:
            for hour in range(15):
                if hour == 0 or hour == 1 or 10 <= hour <= 14:  # hour >= 10 and hour <= 14:
                    agent.schedule[day][hour] = "Off-Campus Space"


# CLASS ASSIGNMENT ------------------------------------------------------------------------------------------------------------------------------------
def assign_faculty_classes(day_time, academic_buildings, faculty_by_major):
    # dictionary of number of available classrooms for each timeslot for each major
    stem_available_timeslots = {}  # {'A2': 49, 'A4': 49, 'A6': 49, 'A8': 49, 'B2': 49, 'B4': 49, 'B6': 49, 'B8': 49}
    humanities_available_timeslots = {}  # {'A2': 24, 'A4': 24, 'A6': 24, 'A8': 24, 'B2': 24, 'B4': 24, 'B6': 24, 'B8': 24}
    arts_available_timeslots = {}  # {'A2': 22, 'A4': 22, 'A6': 22, 'A8': 22, 'B2': 22, 'B4': 22, 'B6': 22, 'B8': 22}
    available_timeslots = [stem_available_timeslots, humanities_available_timeslots, arts_available_timeslots]
    for major in available_timeslots:
        major_index = available_timeslots.index(major)

        if major_index == 0:
            major_timeslots = "STEM"
        elif major_index == 1:
            major_timeslots = "Humanities"
        else:  # if major_index == 2
            major_timeslots = "Arts"

        # list of the number of small/medium/large buildings for each major
        num_of_buildings = ACADEMIC_BUILDINGS.get(major_timeslots)
        # total number of classrooms for each major
        num_of_classrooms = num_of_buildings[0] * sum(CLASSROOMS.get("Small")) + num_of_buildings[1] * sum(
            CLASSROOMS.get("Medium")) + num_of_buildings[2] * sum(CLASSROOMS.get("Large"))

        for dt in day_time:
            available_timeslots[major_index].update({dt[0] + str(dt[1]): num_of_classrooms})

    # assign faculty to two timeslots until there are no more timeslots in the agent's major
    remaining_faculty = []  # list of faculty who can't get a class of their major (because the major classrooms are out of space)

    for major in available_timeslots:
        num_of_classrooms = list(major.values())[
            0]  # number of classrooms for every timeslot (they're all the same for same majors)
        major_index = available_timeslots.index(major)
        major_faculty = copy.copy(faculty_by_major[major_index])
        major_timeslots = available_timeslots[major_index]

        for i in range(num_of_classrooms):
            class_day_time = copy.copy(day_time)

            if len(major_faculty) < 4:
                four_faculty = copy.copy(major_faculty)
            else:
                four_faculty = random.sample(major_faculty, k=4)

            for faculty in four_faculty:
                two_classes = random.sample(class_day_time, k=2)
                for classes in two_classes:
                    class_day_time.remove(classes)
                    timeslot = classes[0] + str(classes[1])
                    major_timeslots[timeslot] -= 1
                    faculty.class_times.append([classes,
                                                major_index])  # appending [[day, time], major] of classroom because there will be agents who are assigned to classes that are not of their major

                major_faculty.remove(faculty)

        for faculty in major_faculty:
            remaining_faculty.append(faculty)
    # print(available_timeslots)

    remaining_majors = copy.copy(available_timeslots)  # list of major buildings that still have available timeslots
    for major in remaining_majors:
        if all(elem == 0 for elem in major.values()):
            remaining_majors.remove(major)
    random.shuffle(remaining_majors)

    # assign remaining faculty to timeslots of different majors that have available timeslots
    for major in remaining_majors:
        major_index = remaining_majors.index(major)
        major_timeslots = remaining_majors[major_index]

        for i in range(max(major.values())):
            available_times = []  # list of available timeslots in the major building
            for time in major.keys():
                if major.get(time) != 0:
                    available_times.append(time)

            if len(remaining_faculty) < (len(available_times) // 2):
                other_major_faculty = copy.copy(remaining_faculty)
            else:
                other_major_faculty = random.sample(remaining_faculty, k=(len(available_times) // 2))

            for faculty in other_major_faculty:

                two_timeslots = random.sample(available_times, k=2)
                for timeslot in two_timeslots:
                    available_times.remove(timeslot)
                    faculty.class_times.append([[timeslot[0], int(timeslot[1])], available_timeslots.index(
                        major)])  # appending [[day, time], major] of classroom
                    major_timeslots[timeslot] -= 1

                remaining_faculty.remove(faculty)
    # print(available_timeslots)

    # now assign all faculty to classes of corresponding major and [day, time]
    for major in academic_buildings:
        for day in major:
            for time in day:

                major_index = academic_buildings.index(major)
                day_index = major.index(day)
                if day_index == 0:
                    class_day = "A"
                else:  # day_index == 1:
                    class_day = "B"
                time_index = (day.index(time) + 1) * 2

                class_faculty = []
                # for faculty in faculty_list:
                #   if faculty.class_times[0] == [[class_day, time_index], major_index] or faculty.class_times[1] == [[class_day, time_index], major_index]:
                #      class_faculty.append(faculty)
                for major_faculty in faculty_by_major:
                    for faculty in major_faculty:
                        if faculty.class_times[0] == [[class_day, time_index], major_index] or faculty.class_times[1] == [[class_day, time_index], major_index]:
                            class_faculty.append(faculty)

                for building in time:
                    if len(class_faculty) < len(building.classrooms):
                        class_num = len(class_faculty)
                    else:
                        class_num = len(building.classrooms)

                    for i in range(class_num):
                        classroom = building.assign_agent(class_faculty[0])
                        class_faculty[0].classes.append(classroom)
                        class_faculty.remove(class_faculty[0])

    # if order of class times and classroom may not match, switch the order of first and second classroom to make it match
    for major_faculty in faculty_by_major:
        for faculty in major_faculty:
            if [faculty.classes[0].space.day, faculty.classes[0].space.time] != faculty.class_times[0][0]:
                second_class = faculty.classes[0]
                faculty.classes.remove(second_class)
                faculty.classes.append(second_class)  # remove and then append again to organize order


# -----------------------------------------------------------------------------------------------------------------------------------
def assign_student_classes(day_time, academic_buildings, student_by_major):
    # assign two major classes to student agents
    for major_student in student_by_major:
        for agent in major_student:
            # for agent in student_list:
            day_time_copy = copy.copy(day_time)
            class_times = random.sample(day_time_copy, k=2)
            day_time_copy.remove(class_times[0])
            day_time_copy.remove(class_times[1])
            class_num = 0

            while class_num < 2:
                class_time = class_times[class_num]
                other_majors = [0, 1, 2]
                major_index = agent.get_major_index()
                other_majors.remove(major_index)

                if class_time[0] == "A":
                    day_index = 0
                else:  # if class_time[0] == "B"
                    day_index = 1
                time_index = class_time[1] // 2 - 1

                major_buildings = academic_buildings[major_index][day_index][
                    time_index]  # list of buildings at the corresponding [day, time]
                random.shuffle(major_buildings)

                while all(building.status == "Full" for building in major_buildings):
                    major_index = random.choice(other_majors)
                    major_buildings = academic_buildings[major_index][day_index][time_index]
                    other_majors.remove(major_index)

                for building in major_buildings:
                    if building.status == "Full":
                        continue
                    else:
                        classroom = building.assign_agent(agent)
                        agent.classes.append(classroom)
                        agent.class_times.append([class_time, major_index])
                        break

                class_num += 1

    # assign two other classes (not necessarily of their major) to student agents
    for major_student in student_by_major:
        for agent in major_student:
            # for agent in student_list:
            day_time_copy = copy.copy(day_time)
            day_time_copy.remove(agent.class_times[0][0])
            day_time_copy.remove(agent.class_times[1][0])
            class_times = random.sample(day_time_copy, k=2)
            day_time_copy.remove(class_times[0])
            day_time_copy.remove(class_times[1])
            class_num = 0

            while class_num < 2:
                class_time = class_times[class_num]
                other_majors = [0, 1, 2]
                major_index = random.randint(0, 2)
                other_majors.remove(major_index)

                if class_time[0] == "A":
                    day_index = 0
                else:  # if class_time[0] == "B"
                    day_index = 1
                time_index = class_time[1] // 2 - 1

                major_buildings = academic_buildings[major_index][day_index][
                    time_index]  # list of buildings at the corresponding [day, time]
                random.shuffle(major_buildings)

                while all(building.status == "Full" for building in major_buildings):
                    major_index = random.choice(other_majors)
                    major_buildings = academic_buildings[major_index][day_index][time_index]
                    other_majors.remove(major_index)

                for building in major_buildings:
                    if building.status == "Full":
                        continue
                    else:
                        classroom = building.assign_agent(agent)
                        agent.classes.append(classroom)
                        agent.class_times.append([class_time, major_index])
                        break

                class_num += 1


def add_class_to_schedule(agent_list):
    # after all agents have been assigned to classes, add the classes into their schedule attribute
    for agent in agent_list:
        # add assigned classes to agent's schedule attribute
        for classroom in agent.classes:
            i = agent.classes.index(classroom)
            class_timeslot = agent.class_times[i][0]  # [day, time] of i-th class
            class_day = class_timeslot[0]
            class_time = class_timeslot[1]
            agent.schedule[class_day][class_time] = classroom
            agent.schedule[class_day][class_time + 1] = classroom

            if agent.schedule[class_day][class_time - 1] != classroom:  # If previous agent's location is not the classroom that has just been assigned,
                all_transit_spaces[class_day][class_time].agents.append(agent)  # assign agent to transit space at corresponding [day, time]


# DINING HALL / GYM / LIBRARY ####################################################################################################################
def assign_dining_times(agent_list, dining_hall_space):
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
                    if len(available_times) != 0:
                        gym_hour = random.choice(available_times)
                        gym_spaces[count][gym_hour].assign_agent(agent)

                        if agent.schedule[day][gym_hour - 1] != "Gym":  # If previous agent's location is not Gym,
                            all_transit_spaces[day][gym_hour].agents.append(agent)  # assign agent to transit space at corresponding [day, time]


# Remaining slots for social spaces, library leaf, or dorm room
def assign_remaining_time(agent_list, library_spaces, social_spaces, stem_office_spaces, arts_office_spaces, humanities_office_spaces, off_campus_space):
    for agent in agent_list:
        if agent.type != "Faculty":
            for count, day in enumerate(SCHEDULE_DAYS):
                for hour in agent.get_available_hours(8, 22, day):
                    if day == 'W' and agent.type == "Off-campus Student":
                        off_campus_space[count][hour].assign_agent(agent)
                        continue

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
                            if agent.schedule[day][hour - 1] != "Dorm":  # If previous agent's location is not Dorm, assign agent to transit space at corresponding [day, time]
                                all_transit_spaces[day][hour].agents.append(agent)
                            if agent in doubles_students:
                                if agent.dorm_room in temp_doubles_dorm_times[count][hour]:
                                    doubles_dorm_times[count][hour].append(agent.dorm_room)
                                else:
                                    temp_doubles_dorm_times[count][hour].append(agent.dorm_room)
                        else:
                            off_campus_space[count][hour].assign_agent(agent)
                            if agent.schedule[day][hour - 1] != "Off-Campus Space":
                                all_transit_spaces[day][hour].agents.append(agent)

            if agent.type == "On-campus Student":
                for day in SCHEDULE_DAYS:
                    if agent.schedule[day][13] != "Dorm":
                        all_transit_spaces[day][14].agents.append(agent)
            else:  # if agent.type == "Off-campus Student"
                for day in SCHEDULE_WEEKDAYS:
                    if agent.schedule[day][9] != "Off-Campus Space":
                        all_transit_spaces[day][10].agents.append(agent)
        else:
            for count, day in enumerate(SCHEDULE_DAYS):
                for hour in agent.get_available_hours(8, 22, day):
                    if day == 'W':
                        off_campus_space[count][hour].assign_agent(agent)
                        continue

                    if hour == 0 or hour == 1 or 10 <= hour <= 14:  # hour >= 10 and hour <= 14:
                        off_campus_space[count][hour].assign_agent(agent)
                        if hour == 10:
                            if agent.schedule[day][9] != "Off-Campus Space":
                                all_transit_spaces[day][10].agents.append(agent)

                    else:  # Put into appropriate Division Office vertex
                        if agent.major == "STEM":
                            stem_office_spaces[count][hour].assign_agent(agent)
                        elif agent.major == "Arts":
                            arts_office_spaces[count][hour].assign_agent(agent)
                        else:  # Agent's major is Humanities
                            humanities_office_spaces[count][hour].assign_agent(agent)

                        if agent.schedule[day][hour - 1] != "Office":
                            all_transit_spaces[day][hour].agents.append(agent)