import asyncio
import aiohttp
import re

# Some type definitions used
URL = str
Queue = asyncio.Queue


class IService(object):
    async def run(self):
        pass


class Filter(IService):
    def __init__(self, timeout: int, hyperlink_queue: Queue, request_queue: Queue):
        self._timeout: int = timeout
        self._hyperlink_queue: Queue = hyperlink_queue
        self._request_queue: Queue = request_queue
        # internal state of seen hyperlinks
        self._seen_filter = set()

    async def run(self):
        pass


async def url_filter(timeout: int, in_queue: Queue, out_queue: Queue):
    """
    Filter out already processed items
    :param timeout: max time allowed to await new items before exiting
    :param in_queue: items to be filtered
    :param out_queue: new items
    """
    # internal state of seen hyperlinks
    seen_filter = set()
    # -------------

    while True:
        # Break loop if empty for timeout
        if in_queue.qsize() == 0:
            await asyncio.sleep(timeout)
            if in_queue.qsize() == 0:
                break

        item = await in_queue.get()
        print("<filter got: ", item, " >")

        # -------------
        if item not in seen_filter:
            print("<is new>")
            seen_filter.add(item)
            await out_queue.put(item)
        else:
            print("<old!>")
        # -------------

    print("<end url_filter>")


async def network_reader(timeout: int, in_queue: Queue, out_queue: Queue):
    """
    Request website content
    :param timeout: max time allowed to await new items before exiting
    :param in_queue:
    :param out_queue:
    """
    # internal state of request futures pending
    async with aiohttp.ClientSession() as session:

        while True:
            # Break loop if empty for timeout
            if in_queue.qsize() == 0:
                await asyncio.sleep(timeout)
                if in_queue.qsize() == 0:
                    break

            url = await in_queue.get()
            print("<network_reader got: ", url, " >")

            # -------------
            async def _handle_item(session, url, out_queue):
                async with session.get(url) as resp:
                    data = await resp.text()
                    print("<data for: ", url, " >")
                    await out_queue.put((url, data))
                pass

            # sending get request and saving the response as response object
            asyncio.ensure_future(_handle_item(session, url, out_queue))
            # -------------

        print("<end network_reader>")


async def web_parser(timeout: int, in_queue: Queue, email_queue: Queue, hyperlink_queue: Queue):
    while True:
        # Break loop if empty for timeout
        if in_queue.qsize() == 0:
            await asyncio.sleep(timeout)
            if in_queue.qsize() == 0:
                break

        (url, data) = await in_queue.get()
        print("<web_parser got: ", url, " >")

        # -------------
        for link in re.findall('"(https?://.*?)"', data):
            print("<url: ", url, " link: ", link, " >")
            # await hyperlink_queue.put(link)
        # -------------

    print("<end web_parser>")


class NetworkReader(IService):
    def __init__(self, timeout: int, request_queue: Queue, parse_queue: Queue):
        self._timeout: int = timeout
        self._request_queue: Queue = request_queue
        self._parse_queue: Queue = parse_queue

    def _handle(self, url):
        print("NetworkReader got: ", url)


class WebParser(IService):
    def __init__(self, timeout: int, parse_queue: Queue, email_queue: Queue, hyperlink_queue: Queue):
        self._timeout: int = timeout
        self._parse_queue: Queue = parse_queue
        self._email_queue: Queue = email_queue
        self._hyperlink_queue: Queue = hyperlink_queue

    def _handle(self, url):
        print("WebParser got: ", url)


class Display(IService):
    def __init__(self, timeout: int, email_queue: Queue):
        self._timeout: int = timeout
        self._email_queue: Queue = email_queue

    def _handle(self, url):
        print("Display got: ", url)


async def main():
    # Timeout is the max time allowed for any service to await new messages before exiting
    timeout: int = 5  # seconds

    # Create communication queues
    hyperlink_queue = Queue()
    request_queue = Queue()
    parse_queue = Queue()
    email_queue = Queue()

    # Adds crawler seeds
    await hyperlink_queue.put('http://localhost:3000')
    await hyperlink_queue.put(
        'https://www.michaelcho.me/article/primer-to-python-multiprocessing-multithreading-and-asyncio')

    # Create our service processes
    services = [
        # First we filter our URLs to not repeat already processed URLs
        url_filter(timeout, hyperlink_queue, request_queue),

        # New URLs are passed to the network IO service which returns the website data content
        network_reader(timeout, request_queue, parse_queue),

        # Then we find emails on the website content and extract new hyperlinks, repeating the loop
        web_parser(timeout, parse_queue, email_queue, hyperlink_queue),

        # And finally display the found emails to the user upon finding
        # Display(timeout, email_queue)
    ]

    # Startup our services and await completion
    await asyncio.gather(*services)


if __name__ == '__main__':
    asyncio.run(main())
