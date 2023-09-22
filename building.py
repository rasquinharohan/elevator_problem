from src.scheduler import Scheduler
from src.elevator import Elevator
from src.passenger import Passenger
from src.dispatcher import Dispatcher
from common.enums import Status

import datetime
import pandas as pd
from typing import List, Dict

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Building:

    def __init__(self, no_of_elevators: int, no_of_floors: int, max_passengers_per_elevator: int, request_list: List[Dict]) -> None:
        self.dispatcher = Dispatcher(no_of_floors=no_of_floors)
        self.scheduler = Scheduler(dispatcher=self.dispatcher)

        self.no_of_elevators = no_of_elevators
        self.max_elevator_passengers = max_passengers_per_elevator
        self.run_timer = 0
        self.total_floors = no_of_floors

        self.request_list = request_list
        self.request_element = 0

        self.passengers = []

        self.elevator_states = pd.DataFrame()
        self.__create_elevators()

    def __create_elevators(self) -> None:
        for i in range(self.no_of_elevators):
            self.dispatcher.add_elevator(Elevator(name=str(i+1), total_floors=self.total_floors, status=Status.IDLE, no_of_persons=self.max_elevator_passengers))

        self.elevator_states = self.elevator_states.reindex(columns=['RunTimer'] + ['Elevator {}'.format(i+1) for i in range(self.no_of_elevators)])

    def get_next_scheduled_requests(self):
        i = self.request_element

        while i < len(self.request_list) and self.request_list[i]['time'] == self.run_timer:
            i += 1

        timer_request = [] if i == self.request_element else self.request_list[self.request_element: i]
        self.request_element = i
        return timer_request

    def are_all_requests_completed(self):
        return self.request_element >= len(self.request_list)

    def record_elevator_state(self):
        state = dict(RunTimer=self.run_timer)
        for elevator in self.dispatcher.elevators:
            state['Elevator {}'.format(elevator.name)] = elevator.at_floor()
        self.elevator_states = self.elevator_states.append(state, ignore_index = True)

    def print_passenger_stats(self):
        passenger_state = pd.DataFrame(dict(
            Name=pd.Series(dtype='str'),
            StartTime=pd.Series(dtype='int'),
            PickUpTime=pd.Series(dtype='int'),
            EndTime=pd.Series(dtype='int'),
            WaitTime=pd.Series(dtype='int'),
            TotalTime=pd.Series(dtype='int'),
            TripCompleted=pd.Series(dtype='bool')))

        passenger_data_rows = []
        for passenger in self.passengers:
            passenger_data_rows.append(dict(
                Name=passenger.id, StartTime=passenger.start_time, PickUpTime=passenger.pick_up_time,
                EndTime=passenger.end_time, WaitTime=passenger.total_wait_time(), TotalTime=passenger.total_wait_time(),
                TripCompleted=passenger.is_trip_complete
            ))

        passenger_state = passenger_state.append(passenger_data_rows, ignore_index=True)

        logger.debug('--------------- PASSENGER STATS: MIN ---------------')
        logger.debug(passenger_state[['PickUpTime', 'WaitTime', 'TotalTime']].min())
        logger.debug('--------------- PASSENGER STATS: MAX ---------------')
        logger.debug(passenger_state[['PickUpTime', 'WaitTime', 'TotalTime']].max())
        logger.debug('--------------- PASSENGER STATS: MEAN --------------')
        logger.debug(passenger_state[['PickUpTime', 'WaitTime', 'TotalTime']].mean())
        passenger_state.to_csv('./outputs/passenger_states_{}.csv'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')), index=False)

    def write_stats(self):
        self.elevator_states.to_csv('./outputs/elevator_states_{}.csv'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')), index=False)

    def schedule(self):
        while True:
            self.dispatcher.move_elevators()

            req_list = self.get_next_scheduled_requests()
            if req_list:
                passengers = [Passenger(req['id'], req['source'], req['dest'], self.run_timer) for req in req_list]
                self.passengers.extend(passengers)
                self.scheduler.schedule_elevator(passengers)

            self.dispatcher.dispatch(run_timer=self.run_timer)

            logger.debug('---------- TIMER: {0} ----------------'.format(self.run_timer))
            logger.debug(self.scheduler)
            self.record_elevator_state()
            logger.debug('--------------------------------------')
            self.run_timer += 1

            if self.dispatcher.are_all_elevators_idle() and self.are_all_requests_completed():
                self.print_passenger_stats()
                self.write_stats()
                return