import json
import os
import pandas as pd
from owlready2 import *
import warnings

warnings.filterwarnings("ignore")
print("\033c")

ONTOLOGY_FILE   = "./model.owl"
DATA_FILE       = "./student_data.json"


class agent():

    def __init__(self, ontology, data):
        self.ontology   = ontology   
        
        with open(data) as json_data:
            self.student_data = json.load(json_data)

    def extract_courses_taken(self):

        student = self.ontology.Person.Student.id(self.data.id)
        print(student)

    def preliminary_courses(self, courses_has_taken):
        pass
    def make_rankings(self):
        pass
    def apply_filter(self):
        pass
    def built_combinations(self, possible_courses):
        pass
    def check_consistency(self):
        pass

def main():

    # path to the wine ontology
    onto = get_ontology(ONTOLOGY_FILE)
    onto.load()

    with onto:
        sync_reasoner(infer_property_values=True)

        new_agent = agent(onto, DATA_FILE)
        new_agent.extract_courses_taken()


if __name__ == "__main__":
    main()