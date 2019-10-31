import json
import pandas as pd

from Student import Student
from onto_agent import Agent
from trust_system import AgentModel
from owlready2 import *
from quickstart import *

class StateMachine(object):
    __shared_state = {}

    def __init__(self):

        self.rank_package = self.hard_filter_package = self.random_package = None
        self.previousState = self.currentState = self.nextState = None
        self.agent = self.student = None
        
        self.checked        = False
        self.performance    = None
        self.df             = None

        self.__dict__ = self.__shared_state


    def run(self):

        models_list = []
        for i in range(6):
            models_list.append(AgentModel("./models/agent_model{}".format(i)))
        
        agent = AgentModel("./models/agent_model0")
        agent.trust(models_list)
        agent.generate_course_scores(models_list)
        self.df = pd.DataFrame(columns=["random_package", "hard_filter_package", "ranked_package", "random_scores", "hard_filter_scores", "ranked_scores"])
        
        #Loading students data
        with open("./data/student_data_final.json") as json_data:
            data = json.load(json_data)
        
        for idx in range(len(data)):
            self.student        = Student(data[idx])
            self.currentState   = StartState()
            self.agent          = Agent(agent.trust_scores_dict, data[idx])
            
            self.update(self.agent, self.student)

    #State transition function
    def update(self, agent, student):
        
        while self.currentState:
            self.currentState.update(agent, student)

            if self.nextState:
                self.previousState  = self.currentState
                self.currentState   = self.nextState
                self.nextState      = None

class IdleState(StateMachine):

    def update(self, agent, student):
        
        #Before preferences weights evaluation - do hard filtering 
        if agent.pref_weight is None:
            self.nextState = AskStrictFilters()
            return

        #After agent checked results, asking user give more preferences, otherwise present final result
        if type(self.previousState) == CheckResult:
            print("\nAGENT: If you give me more preferences I can do better! Yes or no?")
            if student.confirm():
                self.nextState = AskPreferenceState()
            else:
                self.nextState = PresentFinalResult()
            return

        self.nextState = AskPreferenceState()

class PresentFinalResult(StateMachine):

    def update(self, agent, student):
        
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        
        agent.ranked_packages.reverse()
        for package in agent.ranked_packages:
            agent.print_debug("Best package: ", package)
            print("\nAGENT: Would you like take this course plan! Yes or no?")
            
            if student.confirm():
                print("Adding courses to calendar...")
                calendar = GCalendar()
                for course in package[0]:
                   for weekday in course.isTaughtOnWeekday:
                        calendar.insert_event(course.name, weekday.name)
                print("Done\n")

                self.rank_package   = package[0]
                self.nextState      = EndState()
                #End of interaction
                return

        print("\nAGENT: There are no packages left. Do you want to search again! Yes or Not?")
        if student.confirm():
            self.nextState = StartState()
        else:
            self.nextState = EndState(None)

class CheckResult(StateMachine):

    def update(self, agent, student):
        
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        
        #Show to user best 5 packages
        agent.print_debug("Best packages: ", agent.ranked_packages[-5:])
        try:
            if agent.ranked_packages[-1][1] == agent.ranked_packages[-2][1]:
                agent.print_debug(
                    "AGENT: There is a tie, system will narrow down by matching"
                    "similarity with previously taken courses.")
                similar_packages = agent.similarity_rank()
                agent.ranked_packages = similar_packages
        except IndexError:
            agent.print_debug(
                "AGENT: Looks like there is only one combination possible: ", agent.ranked_packages[-1])

        self.nextState = IdleState()

#Extracting preferences function
class AskPreferenceState(StateMachine):

    def update(self, agent, student):
        
        next_pref = student.get_next_preference()
        if next_pref is None:
            print("End of possible preferences.")
            self.nextState = PresentFinalResult()
            return

        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        
        curr_prefs = student.given_preferences
        print("Basing courses on: {} \n ".format(curr_prefs))
        agent.rank(curr_prefs)
        
        self.nextState = CheckResult()

#Hard filtering function
class AskStrictFilters(StateMachine):

    def update(self, agent, student):
        
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        
        ranked_pref = student.get_ranked_preferences()
        
        print("\nAsking to rank the preferences list: {}".format(ranked_pref))
        agent.set_preference_rank(ranked_pref)
        period = student.get_period()
        
        print("\nApplying filter on period: {}\n".format(period))
        agent.check_period(period)
        hobby = student.get_hobby()
        
        print("\nApplying filter on hobby: {}".format(hobby))
        agent.check_hobbies(hobby)
        
        self.nextState = IdleState()

#Final state
class EndState(StateMachine):

    def update(self, agent, student):
        
        #Information for user
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        print("\nExiting.\n")
        
        self.hard_filter_package    = agent.hard_filters_only()
        self.random_package         = agent.random_choice()
        #Set different variance of package choice
        random_pref      = agent.check_unitary_prefs(self.random_package)
        hard_filter_perf = agent.check_unitary_prefs(self.hard_filter_package)
        rank_pref        = agent.check_unitary_prefs(self.rank_package)

        #Evaluating performance
        self.performance = (random_pref, hard_filter_perf, rank_pref)
        print("-" * 25, "Packages: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        print("Random package: ", tuple(self.random_package))
        print("Hard filter only package: ", self.hard_filter_package)
        print("Ranked package: ", self.rank_package)
        
        print("-" * 25, "Performance score: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        print("Random score", random_pref)
        print("Hard filter score", hard_filter_perf)
        print("Ranked score", rank_pref)
        print("\n")
        
        #Saving statistics
        self.df = self.df.append({"random_package": tuple(self.random_package), "hard_filter_package":  self.hard_filter_package, "ranked_package": self.rank_package,
                         "random_scores": self.performance[0], "hard_filter_scores": self.performance[1], "ranked_scores": self.performance[2]}, ignore_index=True)

        self.currentState = None
 
class StartState(StateMachine):

    def update(self, agent, student):
        
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        print("Agent: Greetings, I am your agent I will suggest you some courses based on your preferences.\n")
        
        self.nextState = IdleState()
