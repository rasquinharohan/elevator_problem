# elevator_problem

Setup:
- At start-up, each elevator is initialized (using elevator class) with some basic attributes like the below:
    - Provide number of elevators, number of floors and max passengers per elevator.
    - Provide list of requests.


Assumptions:
- Person enters elevator bay, provides destination floor.
- Elevators are scheduled as follows:
    - When a request comes in, the nearest elevator moving in that direction is selected. 
    - If all elevators are idle, request is picked by the first elevator, the direction of the elevator is set to the direction where the passenger call happens.
    - If all elevators are moving in the opposite direction, the elevator with the least travel time is selected.
    - Elevator continues to move in that direction till its, a) idle b) reached the top floor or bottom floor
 

The scheduling methodology went through multiple iterations. In the end the above method was chosen as:
1. this prevents starving requests
2. simplest form of scheduling algorithm
The issue with this scheduling method is that it causes longer wait times as the elevators need to keep moving in up and down
