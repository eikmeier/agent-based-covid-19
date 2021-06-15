# from global_constants import TOTAL_AGENTS
import random

n = 10  # n = 2380 # number of agents
# agent_attributes = []
vaccine_percentage = [50, 50]
face_mask_comp = [50, 50]
screening_comp = [50, 50]
student_faculty_ratio = [1500/2380, 500/2380, 380/2380]
# ---------------------------------------------------------------------
vaccine_percentage2 = 0.5
face_mask_comp2 = 0.5
screening_comp2 = 0.5
student_faculty_ratio2 = [1500 / 2380, 500 / 2380, 380 / 2380]
# ------------------------------------------------------------------------

class agent:

    def initialize(self):
        # global agents
        agents = []
        for i in range(n):

            ag = agent()
            ag.vaccinated = random.choices([0, 1], weights=vaccine_percentage)[0]  # vaccination status (0 = not vaccinated, 1 = vaccinated)
            ag.face_mask = random.choices([0, 1], weights=face_mask_comp)[0]  # face_mask compliance
            ag.screening = random.choices([0, 1], weights=screening_comp)[0] # screening test compliance
            ag.type = random.choices(["On-campus Student", "Off-campus Student", "Faculty"], weights=student_faculty_ratio)[0]  # agent type - "Student" or "Faculty"
            ag.subtype = random.choice(["STEM", "Humanities", "Arts"])  # agent subtype - should this be random? or are we also going to assign a specific percentage for this?
            ag.seir = random.choice(["S", "E", "Ia", "Im", "Ie", "R"])  # agent (infection) states - maybe this shouldn't be random..?
            ag.social = random.choice([0, 0.25, 0.75])  # reduction in socializing - not sure if I should make this {0, 1}
            agents.append(ag)

            print([ag.vaccinated, ag.face_mask, ag.screening, ag.type, ag.subtype, ag.seir, ag.social])


    def initialize2(self):
        # global agents
        agents = []
        for i in range(n):
            ag = agent()
            ag.vaccinated = 0  # vaccination status (0 = not vaccinated, 1 = vaccinated)
            ag.face_mask = 0  # face_mask compliance
            ag.screening = 0  # screening test compliance
            ag.type = random.choices(["On-campus Student", "Off-campus Student", "Faculty"], weights=student_faculty_ratio)[0]  # agent type - "Student" or "Faculty"
            ag.subtype = random.choice(["STEM", "Humanities", "Arts"])  # agent subtype - should this be random? or are we also going to assign a specific percentage for this?
            ag.seir = random.choice(["S", "E", "Ia", "Im", "Ie", "R"])  # agent (infection) states - maybe this shouldn't be random..?
            ag.social = random.choice([0, 0.25, 0.75])  # reduction in socializing - not sure if I should make this {0, 1}
            agents.append(ag)
            # print([ag.vaccinated, ag.face_mask, ag.screening, ag.type, ag.subtype, ag.seir, ag.social])

        select_vaccine = random.choices(agents, k=int(n * vaccine_percentage2))
        for ag in select_vaccine:
            ag.vaccinated = 1
            # print([ag.vaccinated, ag.face_mask, ag.screening, ag.type, ag.subtype, ag.seir, ag.social])


        select_face_mask = random.choices(agents, k=int(n * face_mask_comp2))
        for ag in select_face_mask:
            ag.face_mask = 1

        select_screening = random.choices(agents, k=int(n * screening_comp2))
        for ag in select_screening:
            ag.screening = 1

        print("-----------------------------------------------------------------------------")
        for ag in agents:
            print([ag.vaccinated, ag.face_mask, ag.screening, ag.type, ag.subtype, ag.seir, ag.social])




    # def infect(self):











