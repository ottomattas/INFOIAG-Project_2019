import json
import os
import warnings
from itertools import combinations
from pprint import pprint
from random import sample, randint

import numpy as np
import pandas as pd
from owlready2 import *


from trust_system import AgentModel

warnings.filterwarnings("ignore")

ONTOLOGY_FILE = "./ultimate_ontology.owl"
DATA_FILE = "./student_data.json"

class Agent:

    def __init__(self, data, trust_models):
        self.ontology = get_ontology(ONTOLOGY_FILE)
        self.ontology.load()
        with self.ontology:
            sync_reasoner(infer_property_values=True)

        with open(data) as json_data:
            self.data = json.load(json_data)

        self.trust_models = trust_models
        self.student_obj = self.ontology.search(studentID=self.data["id"])[0]
        self.disliked_teachers_obj = [self.ontology.search(teacherID=teacher_id)[0]
                                      for teacher_id in self.data["preferences"]["dislikes"]
                                      ]
        self.liked_teachers_obj = [self.ontology.search(teacherID=teacher_id)[0]
                                   for teacher_id in self.data["preferences"]["likes"]
                                   ]
        self.friends_obj = self.student_obj.hasFriend

    @staticmethod
    def print_debug(*param):
        pprint(param)
        print("-" * 50)

    @staticmethod
    def extract_topics(course_list):
        return set([topic.name
                    for topic in list(itertools.chain.from_iterable([c.covers for c in course_list]))
                    ])

    @staticmethod
    def get_similar_courses_to(course, all_courses, no):
        similar_courses = []
        topics = course.covers
        for c in all_courses:
            if c == course:
                continue
            c_topic = c.covers
            similar = len(set(c_topic).intersection(set(topics)))
            dissimilar = len(set(c_topic).union(set(topics))) - similar
            similar_courses.append((c, similar / (similar + dissimilar)))

        similar_courses.sort(key=lambda t: t[1])

        return [c[0] for c in similar_courses[-no:]]

    @staticmethod
    def generate_combinations(courses):
        return list(combinations(courses, 2)) + list(combinations(courses, 3))

    @staticmethod
    def map_to_interval(importance):
        pref_weight = {
            "topics": 0,
            "skills": 0,
            "likes": 0,
            "dislikes": 0,
            "friends": 0,
        }
        split = 1 / (len(importance) - 1)
        pref_weight[importance[0]] = 1
        pref_weight[importance[-1]] = 0
        for idx, p in enumerate(importance[1:-1]):
            pref_weight[p] = 1 - (idx + 1) * split

        Agent.print_debug("Preferences Weight: ", pref_weight)
        return pref_weight

    @staticmethod
    def get_topics_scores(course, pref_topics):
        topics = course.covers
        topics = [t.name for t in topics]
        return len(set(topics).intersection(set(pref_topics))) / len(pref_topics)

    @staticmethod
    def get_skills_scores(course, pref_skills):
        research_met = course.uses
        skills = research_met[0].improves
        skills = [s.name for s in skills]
        return len(set(skills).intersection(set(pref_skills))) / len(pref_skills)

    def extract_courses_taken(self):
        taken_courses = self.student_obj.hasTaken
        return taken_courses

    def extract_possible_courses(self):
        can_take = self.student_obj.canTake
        return can_take

    def extract_basic_courses(self):
        basic_courses = self.ontology.BasicCourse
        return basic_courses

    def get_dislikes_scores(self, course, weight):
        for teacher in self.disliked_teachers_obj:
            if course.name in [c.name for c in teacher.teaches]:
                return -weight
        return weight

    def get_likes_scores(self, course, weight):
        for teacher in self.liked_teachers_obj:
            if course.name in [c.name for c in teacher.teaches]:
                return weight
        return -weight

    def get_friends_scores(self, course, weight):
        friends_courses = [friend.takes for friend in self.friends_obj]
        courses = [c.name for c in list(itertools.chain.from_iterable(friends_courses))]
        if course.name in courses:
            return weight
        return -weight

    def get_trust_scores(self, course):
        score = 0
        for model in self.trust_models:
            if course.name in self.trust_models[model]:
                score += self.trust_models[model][course.name]
        return score


    def calculate_score(self, package, pref_w):
        preferences = self.data["preferences"]
        score_per_course = []
        for c in package:
            course_scores = [pref_w["topics"] * self.get_topics_scores(c, preferences["topics"]),
                             pref_w["skills"] * self.get_skills_scores(c, preferences["skills"]),
                             self.get_dislikes_scores(c, pref_w["dislikes"]),
                             self.get_likes_scores(c, pref_w["likes"]),
                             self.get_friends_scores(c, pref_w["friends"]),
                             self.get_trust_scores(c)
                             ]

            score_per_course.append(sum(course_scores))

        return sum(score_per_course)

    def rank(self, packages):
        package_score_list = []
        importance_list = self.data["importance"]
        pref_weight = self.map_to_interval(importance_list)
        for p in packages:
            package_score_list.append((p, self.calculate_score(p, pref_weight) / len(p)))

        package_score_list.sort(key=lambda t: t[1])

        self.print_debug("Best packages: ", package_score_list[-5:])
        return package_score_list

    def similarity_rank(self, packages_and_rank_score):
        similar_score_list = []
        course_packages = [t[0] for t in packages_and_rank_score]
        taken_topics = self.extract_topics(self.extract_courses_taken())
        for idx, package in enumerate(packages_and_rank_score):
            pack_topics = self.extract_topics(course_packages[idx])
            similar_score_list.append(
                (course_packages[idx],
                 len(taken_topics.intersection(pack_topics)) / len(package[0]) + package[1]))

        similar_score_list.sort(key=lambda _t: _t[1])
        self.print_debug("Best after similarity ranking packages: ", similar_score_list[-5:])
        return similar_score_list

    def match_preferences(self):
        preferences = self.data["preferences"]
        period = preferences["period"]
        courses = self.get_courses_per_period()[period]
        self.print_debug("Courses from period [" + period + "]: ", courses)

        packages = self.generate_combinations(courses)
        self.print_debug("Generated Packages: ", packages, "Number: ", len(packages))
        ranked_packages = self.rank(packages)
        if ranked_packages[-1][1] == ranked_packages[-2][1]:
            similar_packages = self.similarity_rank(ranked_packages)
            return similar_packages[-1]

        return ranked_packages[-1]

    def get_courses_per_period(self):
        taken_course = self.extract_courses_taken()
        possible_course = self.extract_possible_courses()
        basic_course_without_preliminary = [c for c in self.extract_basic_courses().instances()
                                            if len(c.hasPreliminary) <= 0
                                            ]

        takeable = set(possible_course).union(set(basic_course_without_preliminary))
        final_takeable = takeable.difference(set(taken_course))

        course_per_periods = {"P1": [],
                              "P2": [],
                              "P3": [],
                              "P4": []
                              }

        for course in final_takeable:
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

    def get_all_courses(self):

        humanities_courses = list(self.ontology.HumanitiesCourse.instances())
        science_courses = list(self.ontology.ScienceCourse.instances())
        social_courses = list(self.ontology.SocialCourse.instances())

        return humanities_courses + science_courses + social_courses

    def check_hobbies(self):
        with self.ontology:
            hobby = self.data["preferences"]["hobby"]
            if hobby:
                self.student_obj.practices = [self.ontology.Hobby(hobby)]
                try:
                    sync_reasoner(infer_property_values=True)
                except OwlReadyInconsistentOntologyError:
                    self.print_debug("INCONSISTENCY: Student can't take course on same day as hobby.")


def course_planning(agent):
    courses_taken = agent.extract_courses_taken()
    all_courses = agent.get_all_courses()
    most_similar = agent.get_similar_courses_to(courses_taken[0], all_courses, 3)
    agent.print_debug("Taken Courses: ", courses_taken)
    agent.print_debug("Most similar courses to: [", courses_taken[0], "] are the following: ", most_similar)

    agent.check_hobbies()
    agent.match_preferences()

def generate_trust_models(courses, no_models, courses_per_model):
    for i in range(no_models):
        stud_courses = sample(courses, courses_per_model)
        courses_ratings = [[c.name, randint(0, 10)] for c in stud_courses]
        with open("agent_model{}".format(i), "w") as f:
            for thing in courses_ratings:
                f.write(str(thing)[1:-1] + "\n")

def main():
    models_list = []
    for i in range(6):
        models_list.append(AgentModel("agent_model{}".format(i)))

    a = AgentModel("agent_model0")
    a.trust(models_list)
    a.course_scores(models_list)

    onto_agent = Agent(DATA_FILE, a.trust_scores_dict)
    course_planning(onto_agent)
    # generate_trust_models(onto_agent.get_all_courses(), 6, 10)


if __name__ == "__main__":
    main()
