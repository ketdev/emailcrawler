
Web Crawler for Email Address Extraction
       ~ Accenture Home Task ~
           - David Keter -

Written for Python 3.8

Dependencies:
------------
    pip install asyncio requests
    pip install pytest [for testing only]

To run:
------------
    python crawler.py [--depth X] URL [URLs...]
    Where URL are the initial crawler seeds to search

Notes:
------------
    The crawler avoids loops and will exit when there are no more links remaining,
    but can keep going for a long time, depending on the provided seeds.
    To limit the depth an optional argument 'depth' can be passed to the command line.
