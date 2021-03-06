from .base_service import BaseService
from common.website import Website
from multiprocessing import Queue
import logging
import re


class WebParserService(BaseService):
    """
    Look for hyperlinks and email addresses in a website content data
    """

    def __init__(self, item_counter, in_queue: Queue, email_queue: Queue, hyperlink_queue: Queue):
        super().__init__(item_counter, in_queue)
        self._email_queue = email_queue
        self._hyperlink_queue = hyperlink_queue
        self._link_re = re.compile(r'href=["\'](https?://.*?)["\']')
        self._email_re = re.compile(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]*[a-zA-Z0-9]+)')

    def handle(self, website):
        logging.info('Parsing start: %s', website.url)

        # Here we add new tasks per found item: hyperlink or email
        for link in self._link_re.findall(website.content):

            # calculate next iteration depth
            next_depth = website.depth - 1
            if next_depth == 0:  # reached depth limit
                continue
            elif next_depth < 0:  # no limit
                next_depth = -1

            # add a new task
            self.task_inc()
            logging.info('Found hyperlink: %s depth: %d', link, next_depth)
            self._hyperlink_queue.put(Website(link, next_depth, ''))

        for email in self._email_re.findall(website.content):
            # add a new task
            self.task_inc()
            self._email_queue.put(email.strip())

        logging.info('Parsing done: %s', website.url)

        # Our parsing task completed
        self.task_dec()
