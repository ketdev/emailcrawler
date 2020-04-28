import logging
from .base_service import BaseService
from asyncio import Queue


class FilterService(BaseService):
    """
    Filter out already processed items
    """

    def __init__(self, task_counter, in_queue: Queue, out_queue: Queue):
        super().__init__(task_counter, in_queue)
        self._out_queue = out_queue
        self._seen_filter = set()  # internal state of seen item set

    async def handle(self, item):
        if item not in self._seen_filter:
            logging.info('New item: %s', item)
            self._seen_filter.add(item)
            await self._out_queue.put(item)
