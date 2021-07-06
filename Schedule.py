import random
import copy
import CovidAgents
from spaces import Dorm, Academic, DiningHall, Gym, Library, SocialSpace, OffCampus, Office
from global_constants import DORM_BUILDINGS, ACADEMIC_BUILDINGS, PROBABILITY_G, PROBABILITY_S, PROBABILITY_L, \
    SCHEDULE_DAYS, SCHEDULE_WEEKDAYS

def create_spaces(space, num_hours = 15, division = None):
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

def assign_meal(agent, day, start_hour, end_hour, dhArr):
    day_index = 0
    if day == 'B':
        day_index = 1
    elif day == 'W':
        day_index = 2
    possibleMealHours = agent.get_available_hours(start_hour, end_hour, day)
    if possibleMealHours:
        mealHour = random.choice(possibleMealHours)
        dhArr[day_index][mealHour].assignAgent(agent)

# initialize agents - list of agents
agent_list = CovidAgents.Agent().initialize()  # list of all agents

faculty_list = [agent for agent in agent_list if agent.type == "Faculty"]  # list of all faculty agents
on_campus_students = [agent for agent in agent_list if agent.type == "On-campus Student"]  # list of students living on-campus and need to be assigned to a dorm room
off_campus_students = [agent for agent in agent_list if agent.type == "Off-campus Student"]  # list of students living off-campus
student_list = on_campus_students + off_campus_students  # list of all student agents

# Shuffle agents
random.shuffle(faculty_list) 
random.shuffle(on_campus_students)
random.shuffle(off_campus_students)
random.shuffle(student_list)

# DORM ASSIGNMENT ------------------------------------------------------------------------------------------------------------------------------------
# create dorm buildings (25 small, 10 medium, 10 large)
dorms = []
for i in range(DORM_BUILDINGS.get("Small")):
    dorms.append(Dorm("Small"))
for i in range(DORM_BUILDINGS.get("Medium")):
    dorms.append(Dorm("Medium"))
for i in range(DORM_BUILDINGS.get("Large")):
    dorms.append(Dorm("Large"))

# list of available dorms that are not fully occupied
available_dorms = copy.copy(dorms)

doubles_students = []
temp_doubles_dorm_times = [[[] for j in range(15)] for i in range(3)]
doubles_dorm_times = [[[] for j in range(15)] for i in range(3)]

# randomly assigns agents(on-campus students) to dorms
for agent in on_campus_students:
    if len(dorms) == 0:  # if there are no available dorms (all dorms are full)
        print("All dorms are fully occupied")
    else:
        agent.dorm_building = random.choice(available_dorms)
        agent.dorm_room = agent.dorm_building.assignAgent(agent)
        if agent.dorm_room in agent.dorm_building.doubles:
            doubles_students.append(agent)
        if agent.dorm_building.status == "Full":
            available_dorms.remove(agent.dorm_building)

# CLASS ASSIGNMENT ------------------------------------------------------------------------------------------------------------------------------------
# create academic buildings (STEM, Humanities, Arts) for class times ([10AM, 12PM, 14PM, 16PM] - index [2, 4, 6, 8])
# one list of all the classrooms at specific day(A or B) and time (2, 4, 6, 8)
stem_buildings = [[[] for i in range(4)] for i in range(2)] # STEM buildings: 2 small, 2 medium, 3 large
humanities_buildings = [[[] for i in range(4)] for i in range(2)]  # Humanities buildings: 1 small, 2 medium, 1 large
arts_buildings = [[[] for i in range(4)] for i in range(2)]  # Arts buildings: 2 small, 1 medium, 1 large
academic_buildings = [stem_buildings, humanities_buildings, arts_buildings]

# create all buildings at all day and times -> First list is split up by Day A and then Day B. Then list is split up by times (10, 12, 14, 16). Then,
 # finally, each entry at a specific day and time contains all academic buildings.

for i in range(8):
    for index, building_list in enumerate(academic_buildings):
        if i // 4 == 0:
            day_type = 'A'
        else:
            day_type = 'B'

        if index == 0:
            major = "STEM"
        elif index == 1:
            major = "Humanities"
        else: # index == 2
            major = "Arts"

        for j in range(ACADEMIC_BUILDINGS.get(major)[0]):
            building_list[i // 4][i % 4].append(Academic("Small", day_type, 2 + 2 * (i % 4)))
        for k in range(ACADEMIC_BUILDINGS.get(major)[1]):
            building_list[i // 4][i % 4].append(Academic("Medium", day_type, 2 + 2 * (i % 4)))
        for l in range(ACADEMIC_BUILDINGS.get(major)[2]):
            building_list[i // 4][i % 4].append(Academic("Large", day_type, 2 + 2 * (i % 4)))

# Class assignment for each day & time
time_range = [2, 4, 6, 8]  # index of time slots for classes
day_time = [[day, time] for day in SCHEDULE_WEEKDAYS for time in time_range] # [day, time] combinations for classes

# list of faculty by major
stem_faculty = [faculty for faculty in faculty_list if faculty.subtype == "STEM"]
humanities_faculty = [faculty for faculty in faculty_list if faculty.subtype == "Humanities"]
arts_faculty = [faculty for faculty in faculty_list if faculty.subtype == "Arts"]
faculty_by_major = [stem_faculty, humanities_faculty, arts_faculty]
remaining_buildings = []

for major in academic_buildings:
    major_index = academic_buildings.index(major)
    major_faculty = faculty_by_major[major_index]

    for day in major:
        for time in day:
            for building in time:
                class_num = len(building.classrooms)  # number of classrooms in building
                select_faculty = []
                zero_class_faculty = [faculty for faculty in major_faculty if faculty.num_of_classes == 0]
                one_class_faculty = [faculty for faculty in major_faculty if faculty.num_of_classes == 1]
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
                    building.assignAgent(faculty)  # assign agent to a classroom
                    if faculty.num_of_classes == 2:  # if agent is already assigned to 2 classes, remove them from list
                        major_faculty.remove(faculty)

                if len(select_faculty) < class_num:  # after assigning all selected faculty, if building is not full (with faculty) and has remaining classrooms that need faculty assigned
                    remaining_buildings.append(building)

remaining_faculty = [faculty for major in faculty_by_major for faculty in major]

for faculty in copy.copy(remaining_faculty):
    for building in copy.copy(remaining_buildings):
        if faculty.schedule.get(building.day)[building.time] == None:
            classroom = building.assignAgent(faculty)  # assign agent to a classroom
            if classroom == None:
                remaining_buildings.remove(building)
            else:
                remaining_faculty.remove(faculty)
                break # No need to go through the other buildings for this faculty since they have been successfully assigned


# First randomly assign an agent's 2 major classes
for agent in student_list:
    agent.class_times = random.sample(day_time, k=4)
    major_index = agent.get_major_index()

    while agent.num_of_classes < 2:  # select two classes within agent's major
        class_time = agent.class_times[agent.num_of_classes]

        # We want to get a building from this major, at the time and day we have been given, and then assign an agent to that space.
        day = 0
        if class_time[0] == 'B':
            day = 1
        
        major_spaces = academic_buildings[major_index][day][int((class_time[1] - 2) / 2)]
        for space in copy.copy(major_spaces):
            classroom = space.assignAgent(agent)
            if classroom != None:
                break

# Next, randomly assign 2 non-major classes
for agent in student_list:
    while agent.num_of_classes < 4:  # select two classes regardless of agent's major
        class_time = agent.class_times[agent.num_of_classes]
        # We want to get a building from this major, at the time and day we have been given, and then assign an agent to that space.
        day = 0 # Day is by default 'A'
        if class_time[0] == 'B':
            day = 1
        other_spaces = academic_buildings[random.randint(0, 2)][day][int((class_time[1] - 2) / 2)]
        for space in other_spaces:
            classroom = space.assignAgent(agent)
            if classroom is not None:
                break

diningHallSpaces = create_spaces("DiningHall", 13) # We have unused Dining Hall spaces (at time 16) because the hours are not consecutive
    
for agent in agent_list: # Assign dining hall times to all agents
    if agent.type == "Off-campus Student":
        for day in SCHEDULE_WEEKDAYS:
            assign_meal(agent, day, 12, 15, diningHallSpaces)
    elif agent.type == "Faculty":
        for day in SCHEDULE_WEEKDAYS:
            assign_meal(agent, day, 11, 13, diningHallSpaces)     
    else:
        for day in SCHEDULE_DAYS:
            assign_meal(agent, day, 8, 11, diningHallSpaces)
            assign_meal(agent, day, 12, 15, diningHallSpaces)
            assign_meal(agent, day, 17, 20, diningHallSpaces)

gymSpaces = create_spaces("Gym")

# Try to assign Gym slots
for agent in agent_list:
    if agent.type != "Faculty":
        for count, day in enumerate(SCHEDULE_DAYS):
            if day == 'W' and agent.type == "Off-campus Student":
                break
            rand_prob = random.random()
            if rand_prob < PROBABILITY_G:
                available_times = agent.get_available_hours(8, 22, day)
                gymHour = random.choice(available_times)
                gymSpaces[count][gymHour].assignAgent(agent)

librarySpaces = create_spaces("Library")
socialSpaces = create_spaces("SocialSpace")
stem_office_spaces = create_spaces("Office", 10, "STEM") 
arts_office_spaces = create_spaces("Office", 10, "Arts")
humanities_office_spaces = create_spaces("Office", 10, "Humanities")
offCampusSpace = create_spaces("OffCampus")
        
# Remaining slots for social spaces, library leaf, or dorm room
for agent in agent_list:
    if agent.type != "Faculty":
        for count, day in enumerate(SCHEDULE_DAYS):
            for hour in agent.get_available_hours(8, 22, day):
                if day == 'W' and agent.type == "Off-campus Student":
                    offCampusSpace[count][hour].assignAgent(agent)
                    continue
                rand_number = random.random()
                if rand_number < PROBABILITY_S: # Assign social space
                    socialSpaces[count][hour].assignAgent(agent)
                elif rand_number < PROBABILITY_S + PROBABILITY_L: # Assign library space
                    librarySpaces[count][hour].assignAgent(agent)
                else: # Assign dorm room if on-campus, otherwise assign off-campus
                    if agent.type == "On-campus Student":
                        agent.schedule.get(day)[hour] = "Dorm"
                        if agent in doubles_students:
                            if agent.dorm_room in temp_doubles_dorm_times[count][hour]:
                                doubles_dorm_times[count][hour].append(agent.dorm_room)
                            else:
                                temp_doubles_dorm_times[count][hour].append(agent.dorm_room)
                    else:
                        offCampusSpace[count][hour].assignAgent(agent)
    else:
        for count, day in enumerate(SCHEDULE_DAYS):
            for hour in agent.get_available_hours(8, 22, day):
                if day == 'W':
                    offCampusSpace[count][hour].assignAgent(agent)
                    continue
                if hour == 0 or hour == 1 or hour >= 10 and hour <= 14:
                    offCampusSpace[count][hour].assignAgent(agent)
                else: # Put into appropriate Division Office vertex
                    if agent.subtype == "STEM":
                        stem_office_spaces[count][hour].assignAgent(agent)
                    elif agent.subtype == "Arts":
                        arts_office_spaces[count][hour].assignAgent(agent)
                    else: # Agent's major is Humanities
                        humanities_office_spaces[count][hour].assignAgent(agent)

