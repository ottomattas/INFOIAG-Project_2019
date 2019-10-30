from StateMachine import StateMachine
from quickstart import GCalendar


if __name__ == "__main__":
    state_machine = StateMachine()
    state_machine.run()
    state_machine.df.to_csv("results.csv", sep=',')
