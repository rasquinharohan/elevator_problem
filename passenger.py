from enums import Direction

class Passenger:
    def __init__(self, id: str, start_floor: int, end_floor: int, start_time: int) -> None:
        self.id = id
        self.start_floor = start_floor
        self.end_floor = end_floor
        self.start_time = start_time
        self.pick_up_time = None
        self.end_time = None
        self.assigned_elevator = None
        self.is_trip_complete = False

    def __str__(self) -> str:
        return 'Passenger: {0}; Trip Completed: {1}; Elevator: {2}; Duration: {3} (Wait Time: {4})'.format(
            self.id, 'YES' if self.is_trip_complete else 'NO', self.assigned_elevator,
            self.total_time() if self.is_trip_complete else 'N/A',
            self.total_wait_time() if self.pick_up_time else 'N/A')

    def direction(self) -> Direction:
        return Direction.DOWN if self.end_floor < self.start_floor else Direction.UP

    def assign_elevator(self, elevator_id: str) -> None:
        self.assigned_elevator = elevator_id

    def set_end_time(self, end_time: int):
        self.end_time = end_time
        self.is_trip_complete = True

    def total_wait_time(self) -> int:
        return (self.pick_up_time - self.start_time) + 1

    def total_time(self) -> int:
        return (self.end_time - self.start_time) + 1

