from enums import Status, Direction
from passenger import Passenger

import logging
logger = logging.getLogger(__name__)

class Elevator:

    def __init__(self, name: str, total_floors: int, status: Status = None, no_of_persons: int = 10) -> None:
        self.name = name
        self.status = status or Status.IDLE
        self.total_number_of_floors = total_floors

        self.direction = None
        self.passenger_direction = None

        self.__pick_up_floor = 1

        self.max_passengers = no_of_persons
        self.__passengers = dict()
        self.__passenger_count = 0
        self.__current_floor = 1

    def __str__(self) -> str:
        return 'Elevator ID: {0} Floor: {1} Passengers: {2} Status: {3}'.format(self.name, self.at_floor(), self.__passenger_count, self.status.name) + \
                '\t\t[Direction: {0}, Passenger Direction: {1}]'.format(self.direction, self.passenger_direction)

    def is_under_maintenance(self) -> bool:
        return self.status == Status.MAINTENANCE

    def is_idle(self) -> bool:
        return self.status == Status.IDLE

    def update_status(self, status: Status):
        self.status = status

    def is_at_max_capacity(self) -> bool:
        return self.__passenger_count == self.max_passengers

    def __is_at_pick_up_floor(self) -> bool:
        return self.at_floor() == self.__pick_up_floor

    def is_moving_in_pass_direction(self) -> bool:
        if self.__is_at_pick_up_floor() and self.direction != self.passenger_direction:
            # in the event the elevator is moving in the direction of the pick-up,
            # change it's direction to move in the direction of the passenger
            self.direction = self.passenger_direction

        return self.direction == self.passenger_direction

    def passenger_count(self) -> int:
        return self.__passenger_count

    def at_floor(self):
        return self.__current_floor

    def add_passenger(self, passenger: Passenger, pick_up_time: int):
        passenger.pick_up_time = pick_up_time
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
                logger.debug('Dropped ==> {0} '.format(passenger))

    def update_pick_up_floor(self, floor_no: int, direction: Direction):

        if direction == Direction.UP:
            self.__pick_up_floor = min(self.__pick_up_floor, floor_no)

        elif direction == Direction.DOWN:
            self.__pick_up_floor = max(self.__pick_up_floor, floor_no)

    def update_elevator_direction(self, floor_no: int, direction: Direction):
        '''
        when updating elevator direction, check to see which floor we need to move to,
        and set the elevator to that direction.

        floor_no: the floor to which we need to move to.
        direction: passenger direction
        '''
        if direction == None or floor_no == self.at_floor():
            self.direction = direction
        elif floor_no < self.at_floor():
            self.direction = Direction.DOWN
        else:
            self.direction = Direction.UP

    def update_passenger_direction(self, direction: Direction):
        self.passenger_direction = direction

    def update_at_floor(self):
        if self.direction == Direction.UP:
            self.__current_floor += 1
        elif self.direction == Direction.DOWN:
            self.__current_floor -= 1

