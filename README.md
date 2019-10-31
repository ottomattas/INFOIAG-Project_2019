Student Course Recommendation Agent
===================================

### Group 7

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To install the required packages listed in requirements.txt file, run the following command:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ pip install -r requirements.txt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To start the program change directory to the project root folder and run:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ python3 main.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### main.py

This file contains only main() function where creates and
runs *"StateMachine"* class which we use for handling agents (state transition
function) and students behaviour.

### StateMachine.py

**StateMachine.py**

This file contains an implementation of *"StateMachine"* class and its child
classes.

**StateMachine** class contains the main initialisation function, run and update
functions. In the initialisation function, we define only object variables.

At **update()** function contains state transition function.

**IdleState** class is inherited from the main *StateMachine* class which
contains implementation of state change situations and forwards agent to one of
the next states: - AskStrictFilters - AskPreferenceState - PresentFinalResult

**PresentFinalResult** class is inherited from the main *StateMachine* class and
contains the implementation of presenting final course packages one by one. If
the user accepts one of these, the program ends. If the agent is out of
suggestions, the system asks the user to change preferences.

**CheckResult** class is inherited from the main *StateMachine* class and
contains the function of presenting intermediate results and displays the best
5-course packages. If the rank of packages equal system warns the user about
this situation and builds similarity rank in advance.

**AskPreferenceState** class is inherited from the main *StateMachine* class and
contains the function of user-agent interaction. And retrieving user
preferences. If agent out of preferences it goes directly
to *PresentFinalResult* state, otherwise to *CheckResult* state.

**AskStrictFilters** class is inherited from the main *StateMachine* class and
contains a function which applying hard filters (period and hobbies).

**EndState** class is inherited from the main *StateMachine* class and contains
a function which gets course packages from random and hard filter only agents
and makes a comparison with our agent by accuracy.

![](media/ad5a24e12b07faf421e3603e5bc7793d.jpg)
