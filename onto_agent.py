import json
import os
import pandas as pd
import numpy as np
from owlready2 import *
from pprint import pprint
import warnings
from itertools import combinations

warnings.filterwarnings("ignore")

ONTOLOGY_FILE   = "./ultimate_ontology.owl"
DATA_FILE       = "./student_data.json"
COURSE_THRESHOLD = 5

class agent():

    def __init__(self, ontology, data, s_index):
        self.ontology   = ontology

        with open(data) as json_data:
            self.data = json.load(json_data)

        self.student_obj = self.ontology.search(studentID=self.data["id"])[0]

    def extract_courses_taken(self):
        taken_courses = self.student_obj.hasTaken
        return taken_courses

    def extract_possible_courses(self):
        can_take = self.student_obj.canTake
        return can_take

    def extract_basic_courses(self):
        basic_courses = self.ontology.BasicCourse
        return basic_courses

    # checked
    def get_similar_courses_to(self, course, all_courses, no):

        similar_courses = []
        topics = course.covers
        for c in all_courses:
            if c == course:
                continue
            c_topic = c.covers
            similar = len(set(c_topic).intersection(set(topics)))
            desimilar = len(set(c_topic).union(set(topics))) - similar
            similar_courses.append((c, similar/(similar + desimilar)))

        similar_courses.sort(key=lambda t: t[1])

        return [c[0] for c in similar_courses[-no:]]

    # checked
    def generate_combinations(self, courses):
        return list(combinations(courses, 2)) + list(combinations(courses, 3))

    def map_to_interval(self, importance):
        pref_weight = {
            "topics": 0,
            "skills": 0,
            "techears_id": 0,
            "friends": 0,
            "hobbies": 0,
        }
        split = 1 / (len(importance) - 1)
        pref_weight[importance[0]] = 2
        pref_weight[importance[-1]] = 1
        for idx, p in enumerate(importance[1:-1]):
            pref_weight[p] = 2 - (idx + 1) * split

        print("Preferences Weight: ")
        pprint(pref_weight)
        return pref_weight


    def get_topics_scores(self, course, topics):
        pass

    def calculate_score(self, packege, pref_w):
        preferences = self.data["preferences"]
        score_per_course = []
        for c in packege:
            course_scores = []
            course_scores.append(self.get_topics_scores(c, preferences["topics"]))
            # do the same for each preference (ex skills etc)
            score_per_course.append(sum(course_scores))



        return sum(score_per_course)

    def rank(self, packages):
        package_score_dict = {}
        importance_list = self.data["importance"]
        pref_weight = self.map_to_interval(importance_list)
        for p in packages:
            package_score_dict[tuple(p)] = self.calculate_score(p, pref_weight)
        return package_score_dict

    def match_preferences(self):

        preferences = self.data["preferences"]
        importance_list = self.data["importance"]
        period = preferences["period"]
        courses = self.get_courses_per_period()[period]
        if len(courses) <= COURSE_THRESHOLD:
            packages = self.generate_combinations(courses)
            print("Generated Packages: ", packages)
            ranked_packages = self.rank(packages)


        print("Courses from period [" + period + "]: ", courses)


    # checked
    def get_courses_per_period(self):
        taken_course = self.extract_courses_taken()
        possible_course = self.extract_possible_courses()
        basic_course_without_preliminary = [c for c in self.extract_basic_courses().instances()
                                            if len(c.hasPreliminary) <= 0
                                            ]

        takeble = set(possible_course).union(set(basic_course_without_preliminary))
        final_takeble = takeble.difference(set(taken_course))

        course_per_periods = {"P1": [],
                              "P2": [],
                              "P3": [],
                              "P4": []
                              }

        for course in final_takeble:
            period = str(course.isTaughtOnPeriod[0]).split(".")[1]
            if period == "P1":
                course_per_periods["P1"].append(course)
            elif period == "P2":
                course_per_periods["P2"].append(course)
            elif period == "P3":
                course_per_periods["P3"].append(course)
            elif period == "P4":
                course_per_periods["P4"].append(course)

        return course_per_periods

    # checked
    def get_all_courses(self):

        HumanitiesCourses    = list(self.ontology.HumanitiesCourse.instances())
        ScienceCourses       = list(self.ontology.ScienceCourse.instances())
        SocialCourses        = list(self.ontology.SocialCourse.instances())

        return HumanitiesCourses + ScienceCourses + SocialCourses

    def check_consistency(self):
        pass


def course_planning(agent):

    coursesTaken        = agent.extract_courses_taken()
    all_courses         = agent.get_all_courses()
    most_similar        = agent.get_similar_courses_to(coursesTaken[0], all_courses, 3)
    print("Taken Courses: ", coursesTaken)
    print("Most similar courses to: [", coursesTaken[0], "] are the following: ", most_similar)

    agent.match_preferences()



def main():

    # ONTOLOGY_FILE - path to the ontology
    onto = get_ontology(ONTOLOGY_FILE)
    onto.load()

    with onto:
        sync_reasoner(infer_property_values=True)

        onto_agent = agent(onto, DATA_FILE, 0)
        course_planning(onto_agent)


if __name__ == "__main__":
    main()
