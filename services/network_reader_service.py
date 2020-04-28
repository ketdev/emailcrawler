import logging
from .base_service import BaseService
from asyncio import Queue, ensure_future
import requests


class NetworkReaderService(BaseService):
    """
    Request website content
    """

    def __init__(self, item_counter, in_queue: Queue, out_queue: Queue):
        super().__init__(item_counter, in_queue)
        self._out_queue = out_queue

    async def handle(self, website):
        task = ensure_future(self._get_request(website))

    async def _get_request(self, website):
        logging.info('GET request: %s', website.url)
        website.content = requests.get(url=website.url).text
        await self._out_queue.put(website)
