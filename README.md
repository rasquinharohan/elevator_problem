# elevator_problem

Setup:
In main.py, provide details like number of elevators, no of floors, max passengers per elevator and a list of requests.

Assumptions:
- Person enters elevator bay, provides destination floor.
- Elevators are scheduled as follows:
    - When a request comes in, the nearest elevator moving in that direction is selected. 
    - If all elevators are idle, request is picked by the first elevator, the direction of the elevator is set to the direction where the passenger call happens.
    - If all elevators are moving in the opposite direction, the elevator with the least travel time is selected.
    - Elevator continues to move in that direction till its, a) idle b) reached the top floor or bottom floor
 

The scheduling methodology went through multiple iterations. In the end the above method was chosen as it causes minimum to no starvation, however we are going to add more wait-times for passengers as the elevators need to finish moving in one direction and then reset to move in opposite direction.
