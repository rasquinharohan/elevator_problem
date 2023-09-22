import sys
from typing import List

from src.elevator import Elevator
from common.enums import Direction
from src.dispatcher import Dispatcher
from src.passenger import Passenger

import logging

logger = logging.getLogger(__name__)

class Scheduler:

    def __init__(self, dispatcher: Dispatcher) -> None:
        self.dispatcher = dispatcher

    def __str__(self) -> str:
        return '\n'.join([str(elevator) for elevator in self.dispatcher.elevators])

    def __get_elevator_pick_up_time(self, elevator: Elevator, pick_up_floor: int, pick_up_direction: Direction):
        # function to get how much time it will for the elevator to pick up the passenger.

        if elevator.is_idle():
            # in this case, elevator has to move to pick up floor
            return abs(pick_up_floor - elevator.at_floor())

        elif pick_up_direction == Direction.UP:
            if elevator.passenger_direction == pick_up_direction:
                if pick_up_floor >= elevator.at_floor():
                    # in-same direction and passenger at floor along the way
                    return pick_up_floor - elevator.at_floor()
                else:
                    # in this case, elevator goes to the last floor, heads back down to 1st floor
                    # and then goes up to pick-up floor
                    return (elevator.total_number_of_floors - elevator.at_floor()) + elevator.total_number_of_floors + pick_up_floor

            else:
                # in this case, elevators passengers are going down, so the total time is
                # time to get to 1st floor and then to pick-up floor
                return abs(1 - elevator.at_floor()) + pick_up_floor

        elif pick_up_direction == Direction.DOWN:
            if elevator.passenger_direction == pick_up_direction and elevator.direction != pick_up_direction:
                # elevator is moving UP to get to first pick-up spot.
                if pick_up_floor >= elevator.at_floor():
                    # in this case the pick-up-floor would be beyond the elevators current floor
                    # so the time taken with be the difference between the at floor and pick-up floor
                    return abs(pick_up_floor - elevator.at_floor())
                else:
                    # in this case the pick-up floor is below the current floor,
                    # so here we need to assume the worst case of the elevator having to go to the
                    # last floor to pick up a passenger and then head down
                    return abs(elevator.total_number_of_floors - elevator.at_floor()) + (elevator.total_number_of_floors - pick_up_floor)

            elif elevator.passenger_direction == pick_up_direction:
                if pick_up_floor <= elevator.at_floor():
                    # in-same direction and passenger at floor along the way
                    return abs(pick_up_floor - elevator.at_floor())

                else:
                    # in-same direction, but passenger at floor above. so the total time is,
                    # time to get to the bottom, time to get all the way to the top and then time to get to pick-up floor
                    return abs(1 - elevator.at_floor()) + elevator.total_number_of_floors + \
                                                        (elevator.total_number_of_floors - pick_up_floor)

            else:
                # in this case, elevators passengers are going up, while current passenger is going down, so the total time is
                # time to get to last floor and then to pick-up floor
                return (elevator.total_number_of_floors - elevator.at_floor()) + (elevator.total_number_of_floors - pick_up_floor)


    def __get_min_trip_elevator(self, start_floor: int, direction: Direction) -> Elevator:
        min_trip_time = sys.maxsize
        pick_up_elevator = None
        for elevator in self.dispatcher.elevators:
            t = self.__get_elevator_pick_up_time(elevator=elevator, pick_up_floor=start_floor, pick_up_direction=direction)
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
