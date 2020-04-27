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
        item = await in_queue.get()
        print("<url_filter got: ", item, " >")

        # -------------
        if item not in seen_filter:
            seen_filter.add(item)
            await out_queue.put(item)
        # -------------


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
            url = await in_queue.get()
            print("<network_reader got: ", url, " >")

            # -------------
            async def _handle_item(session, url, out_queue):
                try:
                    async with session.get(url) as resp:
                        data = await resp.text()
                        print("<data for: ", url, " >")
                        await out_queue.put((url, data))
                except aiohttp.client_exceptions.ClientError:
                    pass
                except UnicodeDecodeError:
                    pass

            # sending get request and saving the response as response object
            asyncio.ensure_future(_handle_item(session, url, out_queue))
            # -------------


async def web_parser(timeout: int, in_queue: Queue, email_queue: Queue, hyperlink_queue: Queue):
    while True:
        (url, data) = await in_queue.get()
        print("<web_parser got: ", url, " >")

        # -------------
        for link in re.findall('href="(https?://.*?)"', data):
            print("<url: ", url, " link: ", link, " >")
            await hyperlink_queue.put(link)

        for email in re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", data):
            print("<email: ", email.strip())
            await email_queue.put(email.strip())
        # -------------


async def email_display(timeout: int, in_queue: Queue):
    while True:
        email = await in_queue.get()
        print("<email_display got: ", email, " >")

        # -------------
        print(email)
        # -------------


async def main():
    # Timeout is the max time allowed for any service to await new messages before exiting
    timeout: int = 5  # seconds

    # Create communication queues
    hyperlink_queue = Queue()
    request_queue = Queue()
    parse_queue = Queue()
    email_queue = Queue()

    # Adds crawler seeds
    await hyperlink_queue.put(
        'https://www.michaelcho.me/article/primer-to-python-multiprocessing-multithreading-and-asyncio')
    await hyperlink_queue.put('http://localhost:3000')

    # Create our service processes
    services = [
        # First we filter our URLs to not repeat already processed URLs
        url_filter(timeout, hyperlink_queue, request_queue),

        # New URLs are passed to the network IO service which returns the website data content
        network_reader(timeout, request_queue, parse_queue),

        # Then we find emails on the website content and extract new hyperlinks, repeating the loop
        web_parser(timeout, parse_queue, email_queue, hyperlink_queue),

        # And finally display the found emails to the user upon finding
        email_display(timeout, email_queue)
    ]

    # Startup our services and await completion
    await asyncio.gather(*services)


if __name__ == '__main__':
    asyncio.run(main())
