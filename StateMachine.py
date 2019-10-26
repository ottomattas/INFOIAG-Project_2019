class StateMachine(object):
    __shared_state = {}

    def __init__(self):
        self.previousState = self.currentState = self.nextState = None

        self.food_types = self.areas = self.price_ranges = None
        self.__dict__ = self.__shared_state

    def run(self):
        self.currentState = StartState()
        self.update()

    def update(self):
        while self.currentState:
            self.currentState.update()
            if self.nextState:
                self.previousState = self.currentState
                self.currentState = self.nextState
                self.nextState = None


class IdleState(StateMachine):
    def update(self):
        pass


class AskPreferenceState(StateMachine):
    def update(self):
        pass


class FilterCourses(StateMachine):
    def update(self):
        pass


class EndState(StateMachine):
    def update(self):
        self.currentState = None


class StartState(StateMachine):
    def update(self):
        self.nextState = IdleState()
