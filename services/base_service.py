from asyncio import Queue, QueueEmpty
from common.item_counter import ItemCounter


class BaseService(object):
    """
    Base class for our services
    """
    HALT = None  # stopping indicator

    def __init__(self, item_counter: ItemCounter, in_queue: Queue):
        self._in_queue = in_queue
        self._item_counter = item_counter

    async def run(self):
        """
        Wait for items in input queue and calls handle method
        """
        while True:
            item = await self._in_queue.get()
            if item is BaseService.HALT:
                break
            await self.handle(item)

    async def stop(self):
        """
        Clears input queue and stops all execution after current item
        """
        try:
            while True:
                self._in_queue.get_nowait()
        except QueueEmpty:
            pass
        finally:
            await self._in_queue.put(BaseService.HALT)

    async def handle(self, item):
        """
        Should be implemented per service
        """
        raise NotImplementedError

    def task_inc(self):
        """
        Called by handler to indicate a new item has been added
        """
        self._item_counter.increment()

    def task_dec(self):
        """
        Called by handler to indicate an item has finished processing
        """
        self._item_counter.decrement()
