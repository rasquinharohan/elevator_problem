from collections import deque

from elevator import Elevator
from enums import Status
from passenger import Passenger
from typing import List

class Dispatcher:
    def __init__(self, no_of_floors: int) -> None:
        self.no_of_floors = int
        self.elevators = list()
        self.elevator_info = dict() # for each elevator, store a queue of passengers for every floor

    def add_elevator(self, elevator: Elevator) -> None:
        self.elevators.append(elevator)
        self.elevator_info[elevator.name] = dict(same=dict(), opposite=dict())

    def add_passenger_to_elevator_queue(self, elevator: Elevator, passenger: Passenger):
        passenger.assign_elevator(elevator.name)
        if elevator.is_idle():
            elevator.update_destination(passenger.end_floor, passenger.direction())

        passenger_q = self.elevator_info[elevator.name].get(passenger.start_floor, deque([]))
        passenger_q.append(passenger)
        self.elevator_info[elevator.name][passenger.start_floor] = passenger_q

    def dispatch(self, run_timer: int):
        for elevator in self.elevators:
            if not elevator.is_idle():
                elevator.update_at_floor()

                if elevator.at_floor() in self.elevator_info[elevator.name]:
                    passenger_q = self.elevator_info[elevator.name].pop(elevator.at_floor())
                    while passenger_q:
                        elevator.add_passenger(passenger_q.pop())

                elevator.drop_passengers(run_timer)
                if elevator.passenger_count() == 0 and len(self.elevator_info[elevator.name].keys()) == 0:
                    elevator.update_status(Status.IDLE)
