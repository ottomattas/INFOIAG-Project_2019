import json
from random import shuffle, randint, seed


class Student:
    def __init__(self, json_idx):
        with open("./data/student_data.json") as json_data:
            self.data = json.load(json_data)[json_idx]
        self.ranked_preferences = self.data["importance"]
        shuffle(self.ranked_preferences)
        self.given_preferences = []
        self.preferences = self.data["preferences"]
        self.prf_idx = 2
        seed()

    def get_next_preference(self):
        if self.prf_idx < len(self.preferences):
            next_pref = list(self.preferences.items())[self.prf_idx]
            print("\nStudent gives new preference: {}\n".format(next_pref[0]))
            self.given_preferences.append(next_pref)
            self.prf_idx += 1
            return next_pref
        return None

    @staticmethod
    def confirm():
        if randint(0, 10) > 0:
            print("\nShow me more!\n")
            return True
        print("\nNo, bye!\n")
        return False

    def get_ranked_preferences(self):
        return self.ranked_preferences

    def get_hobby(self):
        return self.data["preferences"]["hobby"]

    def get_period(self):
        return self.data["preferences"]["period"]
