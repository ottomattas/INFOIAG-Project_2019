import json

from onto_agent import Agent
from trust_system import AgentModel


class StateMachine(object):
    __shared_state = {}

    def __init__(self):
        self.previousState = self.currentState = self.nextState = None
        self.fuck = 10
        self.agent = None
        self.checked = False
        self.__dict__ = self.__shared_state

    def run(self):
        models_list = []
        for i in range(6):
            models_list.append(AgentModel("./models/agent_model{}".format(i)))
        a = AgentModel("./models/agent_model0")
        a.trust(models_list)
        a.generate_course_scores(models_list)

        with open("./data/student_data.json") as json_data:
            data = json.load(json_data)

        for idx in range(len(data) - 1):
            self.currentState = StartState()
            self.agent = Agent(idx, a.trust_scores_dict)
            self.update(self.agent)

    def update(self, agent):
        while self.currentState:
            self.currentState.update(agent)
            if self.nextState:
                self.previousState = self.currentState
                self.currentState = self.nextState
                self.nextState = None


class IdleState(StateMachine):
    def update(self, agent):
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        print("Basing courses on: ", agent.student.given_preferences)
        # if self.previousState == ApplyHardFilter():
        #     self.checked = True
        # if not self.checked:
        #     self.nextState = ApplyHardFilter()
        #     return
        agent.match_preferences()
        self.nextState = AskPreferenceState()


class AskPreferenceState(StateMachine):
    def update(self, agent):
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        next_pref = agent.student.get_next_preference()
        if next_pref is None:
            self.nextState = EndState()
            return
        self.nextState = IdleState()


class ApplyHardFilter(StateMachine):
    def update(self, agent):
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        print("Applying filter on hobby: {}".format(agent.student.get_hobby()))
        agent.check_hobbies()
        self.nextState = IdleState()


class EndState(StateMachine):
    def update(self, agent):
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        self.currentState = None


class StartState(StateMachine):
    def update(self, agent):
        print("-" * 25, "Current state: ", str(self.currentState).split(".")[1].split()[0], "-" * 25)
        print("Greetings, I am your agent I will suggest you some courses based on your preferences.\n")
        self.nextState = IdleState()
