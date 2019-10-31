import numpy as np

from statistics import mean
from pprint import pprint

class AgentModel:
    def __init__(self, file):
        self.id = int(file[-1])
        self.trust_dict = None
        self.trust_scores_dict = None
        with open(file, "r") as f:
            content = f.readlines()
            self.course_ratings = {}
            for line in content:
                split = line.split(",")
                self.course_ratings[split[0][1:-1]] = int(split[1])

    def get_course_ratings(self):
        return self.course_ratings

    def print_(self):
        print(self.course_ratings)

    def trust(self, agents_models):
        del agents_models[self.id]
        print(agents_models)

        trust_dict = {}
        for model in agents_models:
            model_ratings = model.get_course_ratings()
            common = list(set(self.course_ratings).intersection(set(model_ratings)))
            scale = len(common) / len(model_ratings)

            if not common:
                trust_dict[model.id] = 0
                continue
            diff_list = [abs(self.course_ratings[c] - model_ratings[c]) for c in common]
            trust_dict[model.id] = (10 - mean(diff_list)) * 0.1 * scale
        self.trust_dict = trust_dict

    @staticmethod
    def score(x):
        
        if x > 5:
            return (x - 5) / 5
        if x < 5:
            return -(5 - x) / 5
        return 0


    @staticmethod
    def sigmoid_score_discount(x):
        return (11 / (1 + np.e ** (-x / 2))) - 5.5

    @staticmethod
    def score_discount(x):
        
        mx = (10 * 11 / 2) / 10
        if x > 10:
            return mx
        n = 10 - x
        return mx - ((n * (n + 1) / 2) / 10)

    def generate_course_scores(self, agents_models):

        if not self.trust_dict:
            return

        trust_scores_dict = {}
        for model in agents_models:
            model_ratings = model.get_course_ratings()
            for course in model_ratings:
                model_ratings[course] = AgentModel.score(model_ratings[course]) * self.trust_dict[
                    model.id] * AgentModel.sigmoid_score_discount(len(self.trust_dict))
            trust_scores_dict[model.id] = model_ratings

        self.trust_scores_dict = trust_scores_dict
