import logging
from .base_service import BaseService
from multiprocessing import Queue
import requests


class NetworkReaderService(BaseService):
    """
    Request website content
    """

    def __init__(self, item_counter, in_queue: Queue, out_queue: Queue):
        super().__init__(item_counter, in_queue)
        self._out_queue = out_queue

    def handle(self, website):
        logging.info('GET request: %s', website.url)
        website.content = requests.get(url=website.url).text
        self._out_queue.put(website)
