from global_constants import TOTAL_AGENTS
import random

# n = 10  # number of agents
# n = 2380, on-campus: 1500, off-campus: 500, faculty: 380
n = TOTAL_AGENTS


vaccine_percentage = 0.5
face_mask_comp = 0.5
screening_comp = 0.5
type_ratio = [500/2380, 380/2380]  # proportion of ["Off-campus Students", "Faculty"] - default value is "On-campus Student"
major_ratio = [0.25, 0.25]  # proportion of ["Humanities", "Arts"] - default value is "STEM"
initial_infection = 0.4  # proportion of students initially in the exposed state - should we make it number of students or a proportion?
social_ratio = 0.5  # proportion of students that are social


# ------------------------------------------------------------------------
class Agent:
    def initialize(self):
        # global agents
        agents = []
        for i in range(n):
            ag = Agent()
            ag.vaccinated = 0  # vaccination status (0 = not vaccinated, 1 = vaccinated)
            ag.face_mask = 0  # face_mask compliance
            ag.screening = 0  # screening test compliance
            ag.type = "On-campus Student"
            ag.major = "STEM"  # agent subtype/major (either STEM, Humanities, or Arts)
            ag.seir = "S"  # agent infection states (either "S", "E", "Ia", "Im", "Ie", "R")
            ag.classes = []  # list of subspaces/classrooms
            ag.class_times = []  # list of [[day, time], major_index]
            ag.social = "Not Social"  # default value
            ag.schedule = {"A": [None] * 15, "B": [None] * 15, "W": [None] * 15}  # time range is from 8 ~ 22, which is 15 blocks & class times are at index 2, 4, 6, 8

            agents.append(ag)

        # VACCINATION: randomly select and assign vaccination to certain proportion of agents
        select_vaccine = random.sample(agents, k=int(n * vaccine_percentage))
        for ag in select_vaccine:
            ag.vaccinated = 1

        # FACE MASK COMPLIANCE: randomly select and assign face mask compliance to certain proportion of agents
        select_face_mask = random.sample(agents, k=int(n * face_mask_comp))
        for ag in select_face_mask:
            ag.face_mask = 1

        #  SCREENING TEST COMPLIANCE: randomly select and assign screening test compliance to certain proportion of agents
        select_screening = random.sample(agents, k=int(n * screening_comp))
        for ag in select_screening:
            ag.screening = 1

        # TYPE (ON-CAMPUS/OFF-CAMPUS/FACULTY): randomly select and assign a certain proportion of agents as "Off-campus Student" and "Faculty"
        select_type = random.sample(agents, k=int(n * (type_ratio[0] + type_ratio[1])))
        i = 0
        while i < (len(select_type) * (type_ratio[0] / (type_ratio[0] + type_ratio[1]))):
            select_type[i].type = "Off-campus Student"
            i += 1
        while i < len(select_type):
            select_type[i].type = "Faculty"
            i += 1

        # MAJOR (STEM/HUMANITIES/ARTS): randomly select and assign a certain proportion of agents as "Humanities" and "Arts"
        faculty_list = []
        student_list = []
        for ag in agents:
            if ag.type == "Faculty":
                faculty_list.append(ag)
            else:  # if agent is a student
                student_list.append(ag)

        select_major_faculty = random.sample(faculty_list, k=int(len(faculty_list) * (major_ratio[0] + major_ratio[1])))
        select_major_student = random.sample(student_list, k=int(len(student_list) * (major_ratio[0] + major_ratio[1])))
        select_major = [select_major_faculty, select_major_student]

        for select in select_major:
            i = 0
            while i < (len(select) * (major_ratio[0] / (major_ratio[0] + major_ratio[1]))):
                select[i].major = "Humanities"
                i += 1
            while i < len(select):
                select[i].major = "Arts"
                i += 1

        # INITIAL INFECTION: randomly select and assign agents that are initially infected
        no_vaccine = []  # list of agents that haven't been vaccinated
        for ag in agents:
            if ag.vaccinated == 0:
                no_vaccine.append(ag)
        select_seir = random.sample(no_vaccine, k=int(
            n * initial_infection))  # randomly select initial number of agents (that haven't been vaccinated)
        for ag in select_seir:
            ag.seir = random.choice(["Ia", "Im", "Ie"])  # randomly assign one of the infected states to agents

        select_social = random.sample(agents, k=int(n * social_ratio))  # list of all social agents
        for ag in select_social:
            ag.social = "Social"

        # print all agents and their attributes
        # for ag in agents:
            # print([ag.vaccinated, ag.face_mask, ag.screening, ag.type, ag.major, ag.seir, ag.social, ag.schedule])
            # print([ag.type, ag.major])

        return agents

    def getMajorIndex(self):
        if self.major == "STEM":
            return 0
        elif self.major == "Humanities":
            return 1
        else:  # self.major == "Arts"
            return 2

    def __str__(self):
        return 'Agent:' + self.type + '/' + self.major + '/' + self.seir

    def __repr__(self):
        return 'Agent:' + self.type + '/' + self.major + '/' + self.seir


    def getAvailableHours(self, start_hour, end_hour, day):
        available_times = []
        for i in range(start_hour, end_hour + 1):
            if (self.schedule.get(day)[i-8]) == None:
                available_times.append(i-8)
        return available_times


    def __str__(self):
        return 'Agent:' + self.type + '/' + self.major + '/' + self.seir

    def __repr__(self):
        return 'Agent:' + self.type + '/' + self.major + '/' + self.seir