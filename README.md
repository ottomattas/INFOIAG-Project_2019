# Student Course Recommendation Agent
### Group 7
Firstly, needs to install all dependences which contains in __requirements.txt__ file. You can easy do that with comand in terminal: 
```sh
$ pip install -r requirements.txt
```

To start the program you need to go to path which contains "main.py" file and run it in terminal
```sh
$ python3 main.py
```
 

### main.py
This file contains only main() function where creates and runs *"StateMachine"* class which we use for handling agents (state transition function) and students behaviour. 

### StateMachine.py
This file contains implementation of *"StateMachine"* class and his inherits.

__*StateMachine*__ class contains main initialisation function, run and update functions. 
In initialisation function we define only object varaibles. 

At __*run()*__ function 

At __*update()*__ function contains state transition function.

__*IdleState*__ class is inherit of main *StateMachine* class which contains implementation of state change situations and forwards agent to one of the next states:
    - AskStrictFilters
    - AskPreferenceState
    - PresentFinalResult

__*PresentFinalResult*__ class is inherit of main *StateMachine* class and contains implimentation of presenting final course packages one by one. If user accepts one of them interaction ends. If agent out of suggestions, system ask user to change preferences.

This text you see here is *actually* written in Markdown! To get a feel for Markdown's syntax, type some text into the left window and watch the results in the right.

__*CheckResult*__ class is inherit of main *StateMachine* class and contains function of presenting intermediate results and displays best 5 course packages. If rank of packages equal system warns user about this situation and builds similarity rank in advance.

__*AskPreferenceState*__ class is inherit of main *StateMachine* class and contains function of user-agent interaction. And retrieving user preferences. If agent out of preferences it goes directly to *PresentFinalResult* state, otherwise to *CheckResult* state.

__*AskStrictFilters*__ class is inherit of main *StateMachine* class and contains function which applying hard filters (period and hobbies). 

__*EndState*__ class is inherit of main *StateMachine* class and contains function which gets course packeges from random and hard filter only agents and make a comparison with our agent by accuracy.
