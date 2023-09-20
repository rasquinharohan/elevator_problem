import sys
from collections import deque

from enums import Status, Direction
from passenger import Passenger
import logging

logger = logging.getLogger(__name__)

class Elevator:

    def __init__(self, name: str, status: Status = None, no_of_persons: int = 10) -> None:
        self.name = name
        self.status = status or Status.IDLE
        self.direction = None
        self.passenger_direction = None

        self.__pick_up_floor = None
        self.__destination_floor = None

        self.max_passengers = no_of_persons
        self.__passengers = dict()
        self.__passenger_count = 0
        self.__current_floor = 1

    def __str__(self) -> str:
        return 'Elevator ID: {0} Floor: {1}'.format(self.name, self.at_floor())

    def is_under_maintenance(self) -> bool:
        return self.status == Status.MAINTENANCE

    def is_idle(self) -> bool:
        return self.status == Status.IDLE

    def update_status(self, status: Status):
        self.status = status

    def is_at_max_capacity(self) -> bool:
        return self.__passenger_count == self.max_passengers

    def passenger_count(self) -> int:
        return self.__passenger_count

    def at_floor(self):
        return self.__current_floor

    def add_passenger(self, passenger: Passenger):
        if passenger.end_floor in self.__passengers:
            self.__passengers[passenger.end_floor].append(passenger)
        else:
            self.__passengers[passenger.end_floor] = [passenger]

        self.__passenger_count += 1

    def drop_passengers(self, time: int):
        if self.at_floor() in self.__passengers:
            passengers = self.__passengers.pop(self.at_floor())
            self.__passenger_count -= len(passengers)
            for passenger in passengers:
                passenger.set_end_time(time)
                logger.info('Dropped ==> {0} '.format(passenger))

    def update_destination(self, floor_no: int, direction: Direction):
        self.__destination_floor = floor_no
        self.direction = direction
        self.update_status(Status.IN_USE)

    def update_at_floor(self):
        if self.direction == Direction.UP:
            self.__current_floor += 1
        elif self.direction == Direction.DOWN:
            self.__current_floor -= 1

    def get_expected_trip_pickup(self, pick_up_floor: int, destination_floor: int, pick_up_direction: Direction) -> int:
        if self.is_at_max_capacity():
            return sys.maxsize


        if pick_up_direction == self.passenger_direction == self.direction:
            # calling request in the same direction as elevator and passenger direction
            # expected pick_up is in the same direction as the rest of passengers in elevator
            if pick_up_floor >= self.at_floor():
                # the floor is after the current floor the elevator is on. so the time to pick up is the difference
                return pick_up_floor - self.at_floor()
            else:
                # the floor is before the current floor.
                # so now the time to pick up is the total time to get to the destination and come back down to pick up floor
                return (self.__destination_floor - self.at_floor()) * 2  + (self.at_floor() - pick_up_floor)



        elif pick_up_direction == self.passenger_direction:
            # calling request in the direction of passenger_direction, but opposite of elevator direction
            pass




        elif self.is_idle():
            # if elevator is idle, the pick up time will the amount of time to get to the pick up floor
            return abs(self.at_floor() - pick_up_floor)

        else:
            # elevator is going in the opposite direction
            # pick up time, is the time time to get to the destination and come back to pick up floor
            return abs(self.__destination_floor - self.at_floor()) * 2  + abs(self.at_floor() - pick_up_floor)
