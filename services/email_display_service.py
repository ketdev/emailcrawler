from .base_service import BaseService
from asyncio import Queue


class EmailDisplayService(BaseService):
    """
    Displays emails collected to the user
    """

    def __init__(self, task_counter, in_queue: Queue):
        super().__init__(task_counter, in_queue)

    async def handle(self, email):
        print(email)
        self.task_dec()  # finished with a task