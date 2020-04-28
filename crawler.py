import argparse
import logging
import time
from multiprocessing import Queue, Process
from services import FilterService, NetworkReaderService, WebParserService, EmailDisplayService
from common.item_counter import ItemCounter
from common.website import Website

# Set logging level
logging.basicConfig(level=logging.INFO)


def crawler(seeds, depth):
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

    # Count active items, before stopping services
    ic = ItemCounter(len(seeds))  # starting number of items

    # Create our service tasks
    services = [
        # First we filter our URLs to not repeat already processed URLs
        FilterService(ic, hyperlink_queue, request_queue),

        # New URLs are passed to the network IO service which returns the website data content
        NetworkReaderService(ic, request_queue, parse_queue),
        NetworkReaderService(ic, request_queue, parse_queue),
        NetworkReaderService(ic, request_queue, parse_queue),
        NetworkReaderService(ic, request_queue, parse_queue),

        # Then we find emails on the website content and extract new hyperlinks, repeating the loop
        WebParserService(ic, parse_queue, email_queue, hyperlink_queue),
        WebParserService(ic, parse_queue, email_queue, hyperlink_queue),

        # Also filter output emails to remove duplicates
        FilterService(ic, email_queue, display_queue),

        # And finally display the found emails to the user upon finding
        EmailDisplayService(ic, display_queue),
    ]

    # Startup our services
    processes = [Process(target=s.run) for s in services]
    [p.start() for p in processes]

    # Wait for completion
    while not ic.all_done():
        time.sleep(1)
    logging.info('All tasks completed')

    # Close all services
    [s.stop() for s in services]
    [p.join() for p in processes]
    logging.info('All services stopped')

    end = time.time()
    logging.info('Total time: %s', end - start)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web crawler')
    parser.add_argument('--depth', metavar='Depth', type=int, nargs='?', help='Max crawler depth', default=-1)
    parser.add_argument('url', metavar='URL', type=str, nargs='+', help='Crawler seed URLs')
    args = parser.parse_args()

    # Run the crawler with initial seeds
    crawler(args.url, args.depth)
