import numpy as np
from itertools import combinations, chain
from pprint import pprint
from random import randint, shuffle

from owlready2 import *

warnings.filterwarnings("ignore")


class Agent:

    def __init__(self, trust_models, data):
        self.ontology = get_ontology("./ontology.owl")
        self.ontology.load()
        with self.ontology:
            sync_reasoner(infer_property_values=True)

        self.counter            = 0
        self.preferences        = data["preferences"]
        self.ranked_packages    = self.packages = None
        self.pref_weight        = None
        self.trust_models       = trust_models
        self.student_obj        = self.ontology.search(studentID=data["id"])[0]
        self.friends_obj        = self.student_obj.hasFriend

        if data["preferences"]["dislikes"]:
            self.disliked_teachers_obj = self.ontology.search(teacherID=data["preferences"]["dislikes"])[0]

        if data["preferences"]["likes"]:
            self.liked_teachers_obj = self.ontology.search(teacherID=data["preferences"]["likes"])[0]

    @staticmethod
    def print_debug(*param):
        pprint(param)
        print("-" * 50)

    # performance metric
    def dummy_choice_after_hard_filters(self):
        idx = randint(0, len(self.packages))
        return self.packages[idx]

    def dummy_dummy_choice(self):
        # 2 course package
        all_courses = self.get_all_courses()
        shuffle(all_courses)
        if randint(0, 1) == 0:
            return all_courses[0:2]
        return all_courses[0:3]

    @staticmethod
    def prepare_data(preference_dict):
        pref_tuple_list = []
        for p in preference_dict:
            if not preference_dict[p]:
                continue
            if type(preference_dict[p]) == type(list()):
                pref_tuple_list += [(p, elem) for elem in preference_dict[p]]
            pref_tuple_list.append((p, preference_dict[p]))
        return pref_tuple_list

    def apply_pref(self, pref_type, pref_value, package):
        self.counter += 1
        met_prefs = 0

        if pref_type == "period":
            if (all([True if c.isTaughtOnPeriod[0].name == pref_value else False for c in package])):
                return 1
            return 0

        if pref_type == "hobby":
            if (all([True if pref_value not in [w.name for w in c.isTaughtOnWeekday] else False for c in package])):
                return 1
            return 0

        if pref_type == "weekdays":
            if (any([True if pref_value in [w.name for w in c.isTaughtOnWeekday] else False for c in package])):
                return 1
            return 0

        if pref_type == "nweekdays":
            if (any([True if pref_value in [w.name for w in c.isTaughtOnWeekday] else False for c in package])):
                return 0
            return 1

        if pref_type == "topics":
            package_topics = [c.covers for c in package]
            pack_topics = [t.name for t in list(np.concatenate(package_topics))]
            if pref_value in pack_topics:
                return 1
            return 0

        if pref_type == "ntopics":
            package_ntopics = [c.covers for c in package]
            pack_ntopics = [t.name for t in list(np.concatenate(package_ntopics))]
            if pref_value in pack_ntopics:
                return 0
            return 1

        if pref_type == "skills":
            package_skills = [c.uses[0].improves for c in package]
            pack_skills = [s.name for s in list(np.concatenate(package_skills))]
            if pref_value in pack_skills:
                return 1
            return 0

        if pref_type == "likes":
            teacher_courses = [c.name for c in self.liked_teachers_obj.teaches]
            if (any([c for c in package if c in teacher_courses])):
                return 1
            return 0

        if pref_type == "dislikes":
            teacher_courses = [c.name for c in self.disliked_teachers_obj.teaches]
            if (any([c for c in package if c in teacher_courses])):
                 return 0
            return 1

        if pref_type == "friends":
            friends_courses = [c.name
                              for s in self.friends_obj
                              for c in s.takes
                              ]
            if pref_value in friends_courses:
                return 1
            return 0

    def check_unitary_prefs(self, package):
        self.counter = 0
        pref_list = Agent.prepare_data(self.preferences)
        met_prefs = [0]
        for tuple in pref_list:
            met_prefs.append(self.apply_pref(tuple[0], tuple[1], package))
        return sum(met_prefs) / self.counter

    def compact_prefs(self, package):
        pass

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
            r_meth = 0
            if c == course:
                continue
            if c.uses[0].name == course.uses[0].name:
                r_meth = 1 / (len(topics) + 1)
            c_topic = c.covers
            similar = len(set(c_topic).intersection(set(topics)))
            dissimilar = len(set(c_topic).union(set(topics))) - similar
            similar_courses.append((c, similar / (similar + dissimilar + 1) + r_meth))

        similar_courses.sort(key=lambda t: t[1])

        return [c[0] for c in similar_courses[-no:]]

    @staticmethod
    def generate_combinations(courses):
        print(len(list(combinations(courses, 2)) + list(combinations(courses, 3))))
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
        return pref_weight

    @staticmethod
    def get_topics_scores(course, pref_topics):
        topics = course.covers
        topics = [t.name for t in topics]
        return len(set(topics).intersection(set(pref_topics))) / len(pref_topics)

    @staticmethod
    def get_unwanted_topic_scores(course, unwanted_topics):
        topics = course.covers
        topics = [t.name for t in topics]
        return -len(set(topics).intersection(set(unwanted_topics))) / len(unwanted_topics)

    @staticmethod
    def get_weekdays_score(course, weekdays):
        course_weekdays = course.isTaughtOnWeekday
        course_weekdays = [w.name for w in course_weekdays]
        return len(set(weekdays).intersection(set(course_weekdays)))

    @staticmethod
    def get_unwanted_weekdays_score(course, weekdays):
        course_weekdays = course.isTaughtOnWeekday
        course_weekdays = [w.name for w in course_weekdays]
        return -len(set(weekdays).intersection(set(course_weekdays)))

    @staticmethod
    def get_skills_scores(course, pref_skills):
        research_met = course.uses
        skills = research_met[0].improves
        # skills = course.enhances
        skills = [s.name for s in skills]
        return len(set(skills).intersection(set(pref_skills))) / len(pref_skills)

    def extract_courses_taken(self):
        taken_courses = self.student_obj.hasTaken
        return taken_courses

    def extract_possible_courses(self):
        can_take = self.student_obj.unlockedCourse
        return can_take

    def extract_basic_courses(self):
        basic_courses = set(self.ontology.Course.instances()).difference(set(self.ontology.AdvancedCourse.instances()))
        return basic_courses

    def get_dislikes_scores(self, course, weight):
        if course.name in [c.name for c in self.disliked_teachers_obj.teaches]:
            return -weight
        return weight

    def get_likes_scores(self, course, weight):
        if course.name in [c.name for c in self.liked_teachers_obj.teaches]:
            return weight
        return -weight

    def get_friends_scores(self, course, weight):
        friends_courses = [friend.takes for friend in self.friends_obj]
        courses = [c.name for c in list(chain.from_iterable(friends_courses))]
        if course.name in courses:
            return weight
        return -weight

    def get_trust_scores(self, course):
        score = 0
        no = 0
        for model in self.trust_models:
            if course.name in self.trust_models[model]:
                no += 1
                score += self.trust_models[model][course.name]
        return 0 if no == 0 else score / no

    def calculate_score(self, package, given_preferences):
        preferences = dict(given_preferences)
        score_per_course = []
        for c in package:
            course_scores = []
            if "topics" in preferences: course_scores.append(
                self.pref_weight["topics"] * self.get_topics_scores(c, preferences["topics"]))
            if "ntopics" in preferences: course_scores.append(
                self.pref_weight["ntopics"] * self.get_unwanted_topic_scores(c, preferences["ntopics"]))
            if "skills" in preferences: course_scores.append(
                self.pref_weight["skills"] * self.get_skills_scores(c, preferences["skills"]))
            if "dislikes" in preferences: course_scores.append(
                self.get_dislikes_scores(c, self.pref_weight["dislikes"]))
            if "likes" in preferences: course_scores.append(
                self.get_likes_scores(c, self.pref_weight["likes"]))
            if "friends" in preferences: course_scores.append(
                self.get_friends_scores(c, self.pref_weight["friends"]))
            if "weekdays" in preferences: course_scores.append(
                self.pref_weight["weekdays"] * self.get_weekdays_score(c, preferences["weekdays"]))
            if "nweekdays" in preferences: course_scores.append(
                self.pref_weight["nweekdays"] * self.get_unwanted_weekdays_score(c, preferences["nweekdays"]))
            course_scores.append(self.get_trust_scores(c))
            score_per_course.append(sum(course_scores))

        return sum(score_per_course)

    def set_preference_rank(self, ranked_preferences):
        self.pref_weight = self.map_to_interval(ranked_preferences)
        self.print_debug("Preferences Weight: ", self.pref_weight)

    def rank(self, given_preferences):
        package_score_list = []
        for p in self.packages:
            package_score_list.append((p, self.calculate_score(p, given_preferences) / len(p)))
        package_score_list.sort(key=lambda t: t[1])
        self.ranked_packages = package_score_list

    def similarity_rank(self):
        similar_score_list = []
        course_packages = [t[0] for t in self.ranked_packages]
        taken_topics = self.extract_topics(self.extract_courses_taken())
        for idx, package in enumerate(self.ranked_packages):
            pack_topics = self.extract_topics(course_packages[idx])
            similar_score_list.append(
                (course_packages[idx],
                 len(taken_topics.intersection(pack_topics)) / len(package[0]) + package[1]))
        similar_score_list.sort(key=lambda _t: _t[1])
        self.print_debug("Best after similarity ranking packages: ", similar_score_list[-5:])
        return similar_score_list

    def check_period(self, period):
        courses = self.get_courses_per_period()[period]
        self.packages = self.generate_combinations(courses)

    def get_courses_per_period(self):
        taken_course = self.extract_courses_taken()
        possible_course = self.extract_possible_courses()
        basic_course_without_preliminary = [c for c in self.extract_basic_courses()
                                            if not c.hasPreliminary]

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

    def check_hobbies(self, hobby, package=False):
        consist = True
        with self.ontology:
            if package:
                self.student_obj.takes = [course for course in package[0]]
            if hobby:
                self.student_obj.practices = [self.ontology.Hobby(hobby)]
                try:
                    print("\nChecking consistancy of ontology...")
                    sync_reasoner(infer_property_values=True)
                    consist = True
                except OwlReadyInconsistentOntologyError:
                    self.print_debug("INCONSISTENCY: Student can't take course on same day as hobby.")
                    consist = False
        return consist
