import json
import os
import warnings

import pandas as pd
from owlready2 import *

warnings.filterwarnings("ignore")

ONTOLOGY_FILE = "./ultimate_ontology.owl"
DATA_FILE = "./student_data.json"


class Agent():

    def __init__(self, ontology, data, s_index):
        self.ontology = ontology

        with open(data) as json_data:
            self.student_data = json.load(json_data)

        self.student_obj = self.ontology.search(studentID=self.student_data[s_index]["id"])[0]

    def extract_courses_taken(self):
        taken_courses = self.student_obj.hasTaken
        return taken_courses

    def extract_possible_courses(self):
        can_take = self.student_obj.canTake
        return can_take

    def extract_basic_courses(self):
        basic_courses = self.ontology.BasicCourse
        return basic_courses

    def preliminary_courses(self, courses_has_taken):
        pass

    def make_rankings(self):
        pass

    def apply_filter(self):
        pass

    def build_combinations(self):
        taken_course = self.extract_courses_taken()
        possible_course = self.extract_possible_courses()
        basic_course = self.extract_basic_courses().instances()

        comb = [c for c in possible_course if c not in taken_course]



        print(comb)

    def check_consistency(self):
        pass


def main():
    # path to the wine ontology
    onto = get_ontology(ONTOLOGY_FILE)
    onto.load()

    with onto:
        sync_reasoner(infer_property_values=True)

        new_agent = Agent(onto, DATA_FILE, 0)

        new_agent.build_combinations()


if __name__ == "__main__":
    main()
