import argparse
import asyncio
import logging
from asyncio import Queue
from services import FilterService, NetworkReaderService, WebParserService, EmailDisplayService
from common.task_counter import TaskCounter
from common.website import Website
import time

# Set logging level
logging.basicConfig(level=logging.INFO)


async def crawler(seeds, depth):
    logging.info('Starting crawler with depth: %s with seeds: %s', depth, seeds)
    start = time.time()

    # Create communication queues between services
    hyperlink_queue = Queue()
    request_queue = Queue()
    parse_queue = Queue()
    email_queue = Queue()
    display_queue = Queue()

    # Adds crawler seeds
    [hyperlink_queue.put_nowait(Website(s, depth, '')) for s in seeds]

    # Count active tasks, before stopping services
    tc = TaskCounter(len(seeds))  # starting number of tasks

    # Create our service tasks
    services = [
        # First we filter our URLs to not repeat already processed URLs
        FilterService(tc, hyperlink_queue, request_queue),

        # New URLs are passed to the network IO service which returns the website data content
        NetworkReaderService(tc, request_queue, parse_queue),

        # Then we find emails on the website content and extract new hyperlinks, repeating the loop
        WebParserService(tc, parse_queue, email_queue, hyperlink_queue),

        # Also filter output emails to remove duplicates
        FilterService(tc, email_queue, display_queue),

        # And finally display the found emails to the user upon finding
        EmailDisplayService(tc, display_queue),
    ]

    # Startup our services
    [asyncio.ensure_future(s.run()) for s in services]

    # Wait for completion
    while not tc.all_done():
        await asyncio.sleep(1)
    logging.info('All tasks completed')

    # Close all services
    [await s.stop() for s in services]
    logging.info('All services stopped')

    end = time.time()
    logging.info('Total time: %s', end-start)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web crawler')
    parser.add_argument('--depth', metavar='Depth', type=int, nargs='?', help='Max crawler depth', default=-1)
    parser.add_argument('url', metavar='URL', type=str, nargs='+', help='Crawler seed URLs')
    args = parser.parse_args()

    # Run the crawler with initial seeds
    asyncio.run(crawler(args.url, args.depth))
