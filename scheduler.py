import sys
from collections import deque
from typing import List

from elevator import Elevator
from enums import Direction
from dispatcher import Dispatcher
from passenger import Passenger

import logging

logger = logging.getLogger(__name__)

class Scheduler:

    def __init__(self, no_of_floors: int) -> None:
        self.dispatcher = Dispatcher(no_of_floors)

    def __str__(self) -> str:
        return '\n'.join([str(elevator) for elevator in self.dispatcher.elevators])

    def add_elevator(self, e: Elevator) -> None:
        self.dispatcher.add_elevator(e)

    def __get_min_trip_elevator(self, start_floor: int, direction: Direction) -> Elevator:
        min_trip_time = sys.maxsize
        pick_up_elevator = None
        for elevator in self.dispatcher.elevators:
            t = elevator.get_expected_trip_pickup(start_floor, direction)
            if t < min_trip_time:
                # found a faster time, setting to that elevator
                pick_up_elevator = elevator
                min_trip_time = t
            elif t == min_trip_time and not elevator.is_idle():
                # in the case we have a moving elevator with the same trip time as as idle elevator, pick the moving one
                pick_up_elevator = elevator

        return pick_up_elevator

    def schedule_elevator(self, passengers: List[Passenger]):
        for passenger in passengers:
            e = self.__get_min_trip_elevator(passenger.start_floor, passenger.direction())
            self.dispatcher.add_passenger_to_elevator_queue(e, passenger)

    def dispatch(self, run_timer: int):
        self.dispatcher.dispatch(run_timer)