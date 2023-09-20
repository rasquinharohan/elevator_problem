from scheduler import Scheduler
from elevator import Elevator
from passenger import Passenger
from enums import Status

from typing import List, Dict

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# def elevator_scheduler(passenger_entries: List[Passenger], scheduler: Scheduler):
#     run_timer = 0

#     while True:
#         scheduler.schedule_elevator()


class ElevatorSet:

    def __init__(self, no_of_elevators: int, no_of_floors: int, max_passengers_per_elevator: int, request_list: List[Dict]) -> None:
        self.scheduler = Scheduler(no_of_floors=no_of_floors)
        self.no_of_elevators = no_of_elevators
        self.max_elevator_passengers = max_passengers_per_elevator
        self.run_timer = 0
        self.total_floors = no_of_floors

        self.request_list = request_list
        self.request_element = 0

        self.__create_elevators()

    def __create_elevators(self) -> None:
        for i in range(self.no_of_elevators):
            self.scheduler.add_elevator(Elevator(name=str(i+1), total_floors=self.total_floors, status=Status.IDLE, no_of_persons=self.max_elevator_passengers))

    def get_next_scheduled_requests(self):
        i = self.request_element

        while i < len(self.request_list) and self.request_list[i]['time'] == self.run_timer:
            i += 1

        timer_request = [] if i == self.request_element else self.request_list[self.request_element: i]
        self.request_element = i
        return timer_request

    def schedule(self):
        while True:
            req_list = self.get_next_scheduled_requests()
            if req_list:
                self.scheduler.schedule_elevator([Passenger(req['id'], req['source'], req['dest'], self.run_timer) for req in req_list])

            self.scheduler.dispatch(self.run_timer)

            print('---------- TIMER: {0} ----------------'.format(self.run_timer))
            print(self.scheduler)
            print('--------------------------------------')
            self.run_timer += 1



if __name__ == '__main__':
    s = ElevatorSet(4, 100, 10, [dict(time=2, id='pass1', source=1, dest=51),
                                 dict(time=2, id='pass2', source=1, dest=37),
                                 dict(time=10, id='pass3', source=20, dest=1)])
    s.schedule()