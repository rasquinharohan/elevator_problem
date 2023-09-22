from typing import List, Dict

from common.enums import Status, Direction
from src.elevator import Elevator
from src.passenger import Passenger


class ElevatorPassengerQueue:
    def __init__(self, elevator: Elevator) -> None:
        '''
        For each elevator we store information on the passengers that need to be picked up

        There are three states for the elevator dispatch queues.
        a) CURRENT -> passengers going in the same direction yet to be picked up with the floor yet to arrive
        b) NEXT -> passengers going in the opposite direction which are yet to be picked up
        c) FUTURE -> passengers going in the same direction yet to be picked up, but elevator has passed the floor
        '''
        self.dispatch_queue = dict(CURRENT=dict(), NEXT=dict(), FUTURE=dict())
        self.elevator = elevator

    def add_to_queue(self, passenger: Passenger):
        dispatch_queue_key = 'CURRENT'

        if passenger.direction() == self.elevator.passenger_direction:
            # passenger wants to move in the same direction as the elevators passengers
            if self.elevator.direction == self.elevator.passenger_direction:
                # elevator is already moving in the direction to pick/drop-off passengers
                if self.elevator.passenger_direction == Direction.UP:
                    dispatch_queue_key = 'CURRENT' if self.elevator.at_floor() <= passenger.start_floor else 'FUTURE'
                else:
                    dispatch_queue_key = 'CURRENT' if self.elevator.at_floor() >= passenger.start_floor else 'FUTURE'
            else:
                # elevator is moving, but yet to pick up passengers.
                # in this case we make sure we keep moving till we get to the highest/lowest pick-up spot
                dispatch_queue_key = 'CURRENT'
                self.elevator.update_pick_up_floor(passenger.start_floor, passenger.direction())

        else:
            dispatch_queue_key = 'NEXT'

        pick_up_floor_pass_list = self.dispatch_queue[dispatch_queue_key].get(passenger.start_floor, [])
        pick_up_floor_pass_list.append(passenger)
        self.dispatch_queue[dispatch_queue_key][passenger.start_floor] = pick_up_floor_pass_list

    def set_current_direction(self, direction: Direction):
        self.dispatch_queue['CURRENT'] = self.dispatch_queue['NEXT']
        self.dispatch_queue['NEXT'] = self.dispatch_queue['FUTURE']
        self.dispatch_queue['FUTURE'] = dict()
        self.current_direction = direction

    def get_passenger_queue(self) -> Dict[int, List[Passenger]]:
        return self.dispatch_queue['CURRENT']

    def serviced_current_passengers(self) -> bool:
        return len(self.dispatch_queue['CURRENT']) == 0

    def has_pending_passengers(self) -> bool:
        return not(len(self.dispatch_queue['NEXT']) == 0 and len(self.dispatch_queue['FUTURE']) == 0)

    def reset_passenger_queue(self):
        self.dispatch_queue = dict(CURRENT=dict(), NEXT=dict(), FUTURE=dict())
        self.current_direction = None

class Dispatcher:
    def __init__(self, no_of_floors: int) -> None:
        self.no_of_floors = no_of_floors
        self.elevators = list()
        self.elevator_passenger_queue = dict() # for each elevator, store a queue of passengers for every floor

    def add_elevator(self, elevator: Elevator) -> None:
        self.elevators.append(elevator)
        self.elevator_passenger_queue[elevator.name] = ElevatorPassengerQueue(elevator=elevator)

    def are_all_elevators_idle(self):
        for elevator in self.elevators:
            if not elevator.status == Status.IDLE:
                return False

        return True

    def add_passenger_to_elevator_queue(self, elevator: Elevator, passenger: Passenger):
        passenger.assign_elevator(elevator.name)
        if elevator.is_idle():
            elevator.update_pick_up_floor(passenger.start_floor, passenger.direction())
            elevator.update_elevator_direction(passenger.start_floor, passenger.direction())
            elevator.update_passenger_direction(passenger.direction())
            self.elevator_passenger_queue[elevator.name].set_current_direction(passenger.direction())
            elevator.update_status(Status.IN_USE)

        self.elevator_passenger_queue[elevator.name].add_to_queue(passenger=passenger)

    def update_elevator_status(self, elevator: Elevator):
        ele_pass_q_obj = self.elevator_passenger_queue[elevator.name]
        if elevator.passenger_count() == 0 and ele_pass_q_obj.serviced_current_passengers():
            # indicates elevator has picked up and dropped all passengers in this direction

            # switch to NEXT queue.
            # if requests are present in the next queue, then change the direction of the elevator to go and pick them up
            # if elevator was going UP, we now want to go DOWN and pick up the first available passenger (or passengers at the next highest floor)
            # if elevator was going DOWN, we now want to go UP and pick up the first available passenger (or passengers at the next highest floor)
            ele_pass_q_obj.set_current_direction(Direction.DOWN if elevator.direction == Direction.UP else Direction.UP)
            if not ele_pass_q_obj.serviced_current_passengers():
                if elevator.direction == Direction.UP:
                    elevator.update_elevator_direction(elevator.at_floor(), Direction.DOWN)
                    elevator.update_passenger_direction(Direction.DOWN)
                    elevator.update_pick_up_floor(max(ele_pass_q_obj.get_passenger_queue().keys()), Direction.DOWN)
                else:
                    elevator.update_elevator_direction(elevator.at_floor(), Direction.UP)
                    elevator.update_passenger_direction(Direction.UP)
                    elevator.update_pick_up_floor(min(ele_pass_q_obj.get_passenger_queue().keys()), Direction.UP)

                return

            # ONLY IF NO REQUESTS IN NEXT QUEUE, we switch to future queue.
            # if elevator was going UP, we now want to the elevator to go DOWN and pick up the passenger at the lowest floor and then move UP
            # if elevator was going DOWN, we now want to the elevator to go UP and pick up the passenger at the highest floor and then move DOWN
            ele_pass_q_obj.set_current_direction(elevator.direction)
            if not ele_pass_q_obj.serviced_current_passengers():
                if elevator.direction == Direction.UP:
                    elevator.update_elevator_direction(elevator.at_floor(), Direction.DOWN)
                    elevator.update_passenger_direction(Direction.UP)
                    elevator.update_pick_up_floor(min(ele_pass_q_obj.get_passenger_queue().keys()), Direction.UP)
                else:
                    elevator.update_elevator_direction(elevator.at_floor(), Direction.UP)
                    elevator.update_passenger_direction(Direction.DOWN)
                    elevator.update_pick_up_floor(max(ele_pass_q_obj.get_passenger_queue().keys()), Direction.DOWN)

                return

            # elevator has completed all requests and can be set to IDLE
            elevator.update_status(Status.IDLE)
            elevator.update_elevator_direction(elevator.at_floor(), None)
            elevator.update_passenger_direction(None)
            ele_pass_q_obj.reset_passenger_queue()


    def move_elevators(self):
        for elevator in self.elevators:
            if not elevator.is_idle():
                elevator.update_at_floor()

    def dispatch(self, run_timer: int, scheduler):
        for elevator in self.elevators:
            if not elevator.is_idle():
                elevator.drop_passengers(run_timer)

                elevator_pass_q = self.elevator_passenger_queue[elevator.name].get_passenger_queue()

                if elevator_pass_q:
                    # passengers still left to be serviced
                    if elevator.is_moving_in_pass_direction() and elevator_pass_q.get(elevator.at_floor(), None):
                        passenger_q = elevator_pass_q.pop(elevator.at_floor())
                        for passenger in passenger_q:
                            if elevator.is_at_max_capacity():
                                # elevator arrived to pick-up passenger but was full.
                                # so we need to re-schedule the passenger
                                scheduler.schedule_elevator([passenger])
                            else:
                                elevator.add_passenger(passenger, run_timer)

                self.update_elevator_status(elevator=elevator)




