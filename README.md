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

The different classes can be described as follows:
1. Elevator:
   A class that defines the elevator characteristics. It gives information as follows:
   - is the elevator idle
   - which direction the elevator is going
   - which direction are the passengers going
   - what is the current count of passengers
   - adds or drop a passenger to/from the elevator
2. Passenger:
   A class that defines the passenger characteristics. It gives information as follows:
   - when passenger was made the request
   - when passenger was picked up
   - when passenger completed the trip
   - total time spent waiting + travelling in the elevator
   - total time waiting for the elevator
3. Scheduler:
   This class is responsible for chosing an elevator for a passenger.
   The scheduler decides this by looking for the next best elevator that would provide the shortest wait time.
4. Dispatcher:
   This class is responsible for doing the work i.e.:
   - move the elevator in the direction
   - adds passenger to the queue corresponding to the elevator
   - update the status of the elevator i.e. if the elevator has completed all requests set it to idle
   - at every floor, check if there needs to passengers that have to be dropped and picked up by each elevator
6. Building:
   This class in the starting point for all requests.
