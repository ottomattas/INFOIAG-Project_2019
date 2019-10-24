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

# Observations:
#TODO: - Remove Bias (2 vs 3 course packages)
#TODO: - Scaling / Normalization
#TODO: - Score X - Similarity X- (?? what should we do in case of equality) ???? The INFO GAIN approach is biased back to the firrst question ???? NO
#TODO: - Performance measure: average score of random/total course over the average score of the filtered/best ones - How much better is our?
#TODO: - Equal imporance for preferences (same weight)
#TODO: - Learn new skills preference (only if we have time)
#TODO: - Translate from pythonic queries to Manchester queries

class Agent():

    def __init__(self, data, s_index):

        self.ontology   = get_ontology(ONTOLOGY_FILE)
        self.ontology.load()
        with self.ontology:
            sync_reasoner(infer_property_values=True)

        with open(data) as json_data:
            self.data   = json.load(json_data)

        self.student_obj            = self.ontology.search(studentID=self.data["id"])[0]
        self.disliked_teachers_obj  = [self.ontology.search(teacherID=teacher_id)[0]
                                        for teacher_id in self.data["preferences"]["dislikes"]
                                        ]
        self.liked_teachers_obj     = [self.ontology.search(teacherID=teacher_id)[0]
                                        for teacher_id in self.data["preferences"]["likes"]
                                        ]
        self.friends_obj            = self.student_obj.hasFriend


    @staticmethod
    def print_debug(*param):
        print(param)
        print("-" * 50)

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
            "likes": 0,
            "dislikes": 0,
            "friends": 0,
        }
        split = 1 / (len(importance) - 1)
        pref_weight[importance[0]] = 2
        pref_weight[importance[-1]] = 1
        for idx, p in enumerate(importance[1:-1]):
            pref_weight[p] = 2 - (idx + 1) * split

        Agent.print_debug("Preferences Weight: ", pref_weight)
        return pref_weight

    # checked
    def get_topics_scores(self, course, pref_topics):
        topics = course.covers
        topics = [t.name for t in topics]
        return len(set(topics).intersection(set(pref_topics)))

    # checked
    def get_skills_scores(self, course, pref_skills):
        research_met = course.uses
        skills = research_met[0].improves
        skills = [s.name for s in skills]
        return len(set(skills).intersection(set(pref_skills)))

    def get_dislikes_scores(self, course, pref_dislike, weight):
        for teacher in self.disliked_teachers_obj:
            if course.name in [c.name for c in teacher.teaches]:
                # why did we do this shit here?
                return -weight
        return 1

    def get_likes_scores(self, course, pref_likes, weight):
        for teacher in self.liked_teachers_obj:
            if course.name in [c.name for c in teacher.teaches]:
                return weight
        return 1

    def get_friends_scores(self, course, pref_friends, weight):
        friends_courses = [friend.takes for friend in self.friends_obj]
        courses = [c.name for c in list(itertools.chain.from_iterable(friends_courses))]
        if course.name in courses:
            return weight
        return 1

    def calculate_score(self, packege, pref_w):
        preferences = self.data["preferences"]
        score_per_course = []
        for c in packege:
            course_scores = []
            course_scores.append(pref_w["topics"] * self.get_topics_scores(c, preferences["topics"]))
            course_scores.append(pref_w["skills"] * self.get_skills_scores(c, preferences["skills"]))
            course_scores.append(self.get_dislikes_scores(c, preferences["dislikes"], pref_w["dislikes"]))
            course_scores.append(self.get_likes_scores(c, preferences["likes"], pref_w["likes"]))
            course_scores.append(self.get_friends_scores(c, preferences["friends"], pref_w["friends"]))



            score_per_course.append(sum(course_scores))

        return sum(score_per_course)

    def rank(self, packages):
        package_score_list = []
        importance_list = self.data["importance"]
        pref_weight = self.map_to_interval(importance_list)
        for p in packages:
            package_score_list.append((p, self.calculate_score(p, pref_weight) / len(p)))

        package_score_list.sort(key = lambda t: t[1])

        Agent.print_debug("Best packeges: ", package_score_list[-5:])
        return package_score_list

    def extract_topics(self, course_list):
        return set([topic.name
                    for topic in list(itertools.chain.from_iterable([c.covers for c in course_list]))
                    ])

    def similar_rank(self, taken, packages):
        similar_score_list = []
        course_packages = [t[0] for t in packages]
        taken_topics = self.extract_topics(taken)
        for idx, package in enumerate(packages):
            pack_topics = self.extract_topics(course_packages[idx])
            similar_score_list.append((course_packages[idx], len(taken_topics.intersection(pack_topics)) / len(package[0]) + package[1]))

        similar_score_list.sort(key = lambda t: t[1])
        return similar_score_list


    def match_preferences(self):

        preferences = self.data["preferences"]
        importance_list = self.data["importance"]
        period = preferences["period"]
        courses = self.get_courses_per_period()[period]
        Agent.print_debug("Courses from period [" + period + "]: ", courses)

        packages = self.generate_combinations(courses)
        Agent.print_debug("Generated Packages: ", packages, "Number: ", len(packages))
        ranked_packages = self.rank(packages)
        # if the best packages have the same score
        if ranked_packages[-1][1] == ranked_packages[-2][1]:
            similar_packages = self.similar_rank(self.extract_courses_taken(), ranked_packages)


        return ranked_packages[-1]

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

    def check_hobbies(self):
        with self.ontology:
            hobby = self.data["preferences"]["hobby"]
            if hobby:
                self.student_obj.practices = [self.ontology.Hobby(hobby)]
                try:
                    sync_reasoner(infer_property_values=True)
                except OwlReadyInconsistentOntologyError:
                    print("Inconsistent")


def course_planning(agent):

    coursesTaken        = agent.extract_courses_taken()
    all_courses         = agent.get_all_courses()
    most_similar        = agent.get_similar_courses_to(coursesTaken[0], all_courses, 3)
    Agent.print_debug("Taken Courses: ", coursesTaken)
    Agent.print_debug("Most similar courses to: [", coursesTaken[0], "] are the following: ", most_similar)

    agent.check_hobbies()
    agent.match_preferences()



def main():

    onto_agent = Agent(DATA_FILE, 0)
    course_planning(onto_agent)


if __name__ == "__main__":
    main()
