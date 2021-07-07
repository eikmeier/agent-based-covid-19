import random
import CovidAgents
from CovidAgents import initialize_leaves
from Schedule import create_spaces, assign_dorms, assign_faculty_classes, assign_student_classes, add_class_to_schedule, assign_dining_times, assign_gym, assign_remaining_time
from global_constants import DORM_BUILDINGS, ACADEMIC_BUILDINGS, CLASSROOMS
from spaces import Dorm, Academic

def initialize():
    # initialize agents - list of agents
    agent_list = CovidAgents.Agent().initialize()  # list of all agents

    faculty_list = []  # list of all faculty agents
    student_list = []  # list of all student agents
    on_campus_students = []  # list of students living on-campus and need to be assigned to a dorm room
    off_campus_students = []  # list of students living off-campus
    for agent in agent_list:
        if agent.type == "Faculty":
            faculty_list.append(agent)
        else:
            student_list.append(agent)
            if agent.type == "On-campus Student":
                on_campus_students.append(agent)
            else:
                off_campus_students.append(agent)

    random.shuffle(faculty_list)  # shuffle agents
    random.shuffle(student_list)
    random.shuffle(on_campus_students)
    random.shuffle(off_campus_students)

    # ------------------------------------------------------------------------------------------------------
    # create dorm buildings (25 small, 10 medium, 10 large)
    dorms = []
    for i in range(DORM_BUILDINGS.get("Small")):
        dorms.append(Dorm("Small"))
    for i in range(DORM_BUILDINGS.get("Medium")):
        dorms.append(Dorm("Medium"))
    for i in range(DORM_BUILDINGS.get("Large")):
        dorms.append(Dorm("Large"))


    # ------------------------------------------------------------------------------------------------------
    # create academic buildings (STEM, Humanities, Arts) for class times ([10AM, 12PM, 14PM, 16PM] - index [2, 4, 6, 8])
    # one list of all the classrooms at specific day(A or B) and time (2, 4, 6, 8)
    stem_buildings = [[[] for i in range(4)] for i in range(2)]  # STEM buildings: 2 small, 2 medium, 3 large
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
            else:
                major = "Arts"

            for j in range(ACADEMIC_BUILDINGS.get(major)[0]):
                building_list[i // 4][i % 4].append(Academic("Small", major, day_type, 2 + 2 * (i % 4)))
            for k in range(ACADEMIC_BUILDINGS.get(major)[1]):
                building_list[i // 4][i % 4].append(Academic("Medium", major, day_type, 2 + 2 * (i % 4)))
            for l in range(ACADEMIC_BUILDINGS.get(major)[2]):
                building_list[i // 4][i % 4].append(Academic("Large", major, day_type, 2 + 2 * (i % 4)))
    # ------------------------------------------------------------------------------------------------------
    # divide agents by major
    stem_faculty = []     # list of faculty by each major
    humanities_faculty = []
    arts_faculty = []
    faculty_by_major = [stem_faculty, humanities_faculty, arts_faculty]  # list of all faculty, but divided by major
    for agent in faculty_list:
        if agent.major == "STEM":
            stem_faculty.append(agent)
        elif agent.major == "Humanities":
            humanities_faculty.append(agent)
        else:  # if agent.major == "Arts"
            arts_faculty.append(agent)

    # list of students by each major
    stem_students = []
    humanities_students = []
    arts_students = []
    student_by_major = [stem_students, humanities_students, arts_students]  # list of all students, but divided by major
    for agent in student_list:
        if agent.major == "STEM":
            stem_students.append(agent)
        elif agent.major == "Humanities":
            humanities_students.append(agent)
        else:  # if agent.major == "Arts"
            arts_students.append(agent)
    # ----------------------------------------------------------------------------------------
    # list of [day, time] combinations for classes
    # Class assignment for each day & time
    day_range = ["A", "B"]  # days for classes
    time_range = [2, 4, 6, 8]  # index of time slots for classes
    day_time = []  # [day, time] combinations for classes
    for i in day_range:
        for j in time_range:
            day_time.append([i, j])
    # -------------------------------------------------------------------------------------------
    # SCHEDULING FUNCTIONS
    initialize_leaves(agent_list)

    assign_dorms(dorms, on_campus_students)
    """  # CODE TO CHECK IF DORM ASSIGNMENT WORKS
    # prints all the agents in each dorm
    for dorm in dorms:
        print(dorm.size + str(dorms.index(dorm) + 1))
        print("< SINGLES >")
        for single in dorm.singles:
            print(single.agent)
        print("\n")
        print("< DOUBLES >")
        for doubles in dorm.doubles:
            print(doubles.agents)
        print("---------------------------------------------------------------------------------------")
    """

    assign_faculty_classes(day_time, academic_buildings, faculty_by_major)
    """  # CODE TO CHECK IF FACULTY CLASS ASSIGNMENT IS DONE PROPERLY
    for faculty in faculty_list:
        if len(faculty.classes) != 2:
            print("not assigned two classes")
        elif faculty.class_times[0][0] == faculty.class_times[1][0]:
            print("time conflict")
        else:
            print(faculty.classes)

    for major in academic_buildings:  # check if all classrooms have a faculty(not always necessary in different cases, such as when there are either more faculty or classrooms)
        for day in major:
            for time in day:
                for building in time:
                    for classroom in building.classrooms:
                        print(classroom.faculty)
    """

    assign_student_classes(day_time, academic_buildings, student_by_major)
    add_class_to_schedule(agent_list)

    """
    #  CODE TO CHECK IF CLASS ASSIGNMENT IS DONE PROPERLY
    for agent in faculty_list:
        for classroom in agent.classes:
            index = agent.classes.index(classroom)
            if agent.class_times[index][0] != [classroom.space.day, classroom.space.time]:
                print("class does not correspond to class time")

        if not (len(agent.class_times) == 4 or len(agent.class_times) == 2):
            print("not assigned four classes")
        if len(agent.classes) != len(set(agent.classes)):
            print("time conflict")
        else:
            print(agent.major)
            print(agent.class_times)
            print(agent.classes)
            print(agent.schedule)
            print("---------------------------------")
    """


    dining_hall_space = create_spaces("DiningHall", 13)  # We have unused Dining Hall spaces (at time 16) because the hours are not consecutive
    assign_dining_times(agent_list, dining_hall_space)

    gym_spaces = create_spaces("Gym")
    assign_gym(agent_list, gym_spaces)

    library_spaces = create_spaces("Library")
    social_spaces = create_spaces("SocialSpace")
    stem_office_spaces = create_spaces("Office", 10, "STEM")
    arts_office_spaces = create_spaces("Office", 10, "Arts")
    humanities_office_spaces = create_spaces("Office", 10, "Humanities")
    off_campus_space = create_spaces("OffCampus")

    assign_remaining_time(agent_list, library_spaces, social_spaces, stem_office_spaces, arts_office_spaces, humanities_office_spaces, off_campus_space)


initialize()
