import asyncio
import aiohttp
import requests
import re
import multiprocessing as mp
from queue import Empty

# Some type definitions used
URL = str
Queue = mp.Queue


def url_filter(timeout: int, in_queue: Queue, out_queue: Queue):
    """
    Filter out already processed items
    :param timeout: max time allowed to await new items before exiting
    :param in_queue: items to be filtered
    :param out_queue: new items
    """
    # internal state of seen hyperlinks
    seen_filter = set()
    # -------------
    try:
        while True:
            item = in_queue.get(timeout=timeout)
            print("<filter got: ", item, " >")

            # -------------
            if item not in seen_filter:
                print("<is new>")
                seen_filter.add(item)
                out_queue.put(item)
            else:
                print("<old!>")
            # -------------
    except Empty:
        print("<end url_filter>")


def network_reader(timeout: int, in_queue: Queue, out_queue: Queue):
    """
    Request website content
    :param timeout: max time allowed to await new items before exiting
    :param in_queue:
    :param out_queue:
    """
    try:
        while True:
            url = in_queue.get(timeout=timeout)
            print("<network_reader got: ", url, " >")

            # -------------
            # TODO: multi-thread IOs
            data = requests.get(url=url)
            out_queue.put((url, data))
            print("<data for: ", url, " >")
            # -------------
    except Empty:
        print("<end network_reader>")


def web_parser(timeout: int, in_queue: Queue, email_queue: Queue, hyperlink_queue: Queue):
    try:
        while True:
            (url, data) = in_queue.get(timeout=timeout)
            print("<web_parser got: ", url, " >")

            # -------------
            for link in re.findall('"(https?://.*?)"', data.text):
                print("<url: ", url, " link: ", link, " >")
                # hyperlink_queue.put(link)

            for email in re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", data.text):
                print("<email: ", email.strip())
                email_queue.put(email.strip())
            # -------------
    except Empty:
        print("<end web_parser>")


def email_display(timeout: int, in_queue: Queue):
    try:
        while True:
            email = in_queue.get(timeout=timeout)
            print("<email_display got: ", email, " >")

            # -------------
            print(email)
            # -------------

    except Empty:
        print("<end email_display>")


def main():
    # Timeout is the max time allowed for any service to await new messages before exiting
    timeout: int = 5  # seconds

    # Create communication queues
    hyperlink_queue = Queue()
    request_queue = Queue()
    parse_queue = Queue()
    email_queue = Queue()

    # Adds crawler seeds
    hyperlink_queue.put('http://localhost:3000')
    hyperlink_queue.put('https://www.michaelcho.me/article/primer-to-python-multiprocessing-multithreading-and-asyncio')

    # Create our service processes
    services = [
        # First we filter our URLs to not repeat already processed URLs
        mp.Process(target=url_filter, args=(timeout, hyperlink_queue, request_queue)),

        # New URLs are passed to the network IO service which returns the website data content
        mp.Process(target=network_reader, args=(timeout, request_queue, parse_queue)),

        # Then we find emails on the website content and extract new hyperlinks, repeating the loop
        mp.Process(target=web_parser, args=(timeout, parse_queue, email_queue, hyperlink_queue)),

        # And finally display the found emails to the user upon finding
        mp.Process(target=email_display, args=(timeout, email_queue)),
    ]

    # Startup our services and await completion
    [s.start() for s in services]
    [s.join() for s in services]


if __name__ == '__main__':
    main()
