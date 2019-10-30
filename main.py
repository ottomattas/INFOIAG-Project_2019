from StateMachine import StateMachine
from quickstart import GCalendar


if __name__ == "__main__":
    state_machine = StateMachine()
    state_machine.run()
    print(state_machine.performance)
    # calendar = GCalendar()
    # calendar.insert_event(("IntelligentAgents", "Monday"))
