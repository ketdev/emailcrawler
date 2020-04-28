from .base_service import BaseService
from multiprocessing import Queue


class EmailDisplayService(BaseService):
    """
    Displays emails collected to the user
    """

    def __init__(self, item_counter, in_queue: Queue):
        super().__init__(item_counter, in_queue)

    def handle(self, email):
        print(email)
        self.task_dec()  # finished with a task
