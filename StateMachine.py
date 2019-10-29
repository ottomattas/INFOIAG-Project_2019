import json

from Student import Student
from onto_agent import Agent
from trust_system import AgentModel
from owlready2 import *
from quickstart import *

class StateMachine(object):
    __shared_state = {}

    def __init__(self):
        self.previousState = self.currentState = self.nextState = None
        self.agent = self.student = None
        self.checked = False
        self.__dict__ = self.__shared_state

    def run(self):
        models_list = []
        for i in range(6):
            models_list.append(AgentModel("./models/agent_model{}".format(i)))
        a = AgentModel("./models/agent_model0")
        a.trust(models_list)
        a.generate_course_scores(models_list)

        with open("./data/student_data_final.json") as json_data:
            data = json.load(json_data)

        for idx in range(len(data) - 1):
            self.student = Student(idx)
            self.currentState = StartState()
            self.agent = Agent(a.trust_scores_dict, self.student.data)
            self.update(self.agent, self.student)
            break #for testing calendar!

    def update(self, agent, student):
        while self.currentState:
            self.currentState.update(agent, student)
            if self.nextState:
                self.previousState = self.currentState
                self.currentState = self.nextState
                self.nextState = None

class IdleState(StateMachine):
    def update(self, agent, student):
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        if agent.pref_weight is None:
            self.nextState = AskStrictFilters()
            return

        if type(self.previousState) == CheckResult:
            print("\nIf you give me more preferences I can do better! Yes or no?")
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
            print("\nWould you like take this course plan! Yes or no?")
            if student.confirm():
                hobby = student.get_hobby()
                """Checking consistancy of ontology w\ respect to chosen course plan and hobby"""
                if agent.check_hobbies(hobby, package):
                    #if ontology is good, add new courses to calendar!
                    print("Adding courses to calendar...")
                    calendar = GCalendar()
                    for course in package[0]:
                        for weekday in course.isTaughtOnWeekday:
                            calendar.insert_event(course.name, weekday.name)
                    print("Done\n")
                    self.nextState = EndState()
                    return
                else:
                    print("\nPlease, choose another course plan!")
                    continue    
    
        print("\nThere are no packages left. Do you want to search again! Yes or Not?")
        if student.confirm():
            self.nextState = StartState()
        else:
            self.nextState = EndState()    

class CheckResult(StateMachine):
    def update(self, agent, student):
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        agent.print_debug("Best packages: ", agent.ranked_packages[-5:])
        try:
            if agent.ranked_packages[-1][1] == agent.ranked_packages[-2][1]:
                agent.print_debug(
                    "WARNING:\nThere is a tie, system will narrow down by matching \n"
                    "similarity with previously taken courses.")
                similar_packages = agent.similarity_rank()
                agent.print_debug(similar_packages[-1])
        except IndexError:
            agent.print_debug(
                "WARNING:\nLooks like there is only one combination possible:\n", agent.ranked_packages[-1])

        self.nextState = IdleState()

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


class AskStrictFilters(StateMachine):
    def update(self, agent, student):
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        ranked_pref = student.get_ranked_preferences()
        print("\nAsking to rank the preferences list: {}".format(ranked_pref))
        agent.set_preference_rank(ranked_pref)
        hobby = student.get_hobby()
        print("\nApplying filter on hobby: {}".format(hobby))
        agent.check_hobbies(hobby)
        period = student.get_period()
        print("\nApplying filter on period: {}\n".format(period))
        agent.check_period(period)

        self.nextState = IdleState()


class EndState(StateMachine):
    def update(self, agent, student):
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        print("\nExiting.\n")
        self.currentState = None


class StartState(StateMachine):
    def update(self, agent, student):
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        print("Greetings, I am your agent I will suggest you some courses based on your preferences.\n")
        self.nextState = IdleState()
