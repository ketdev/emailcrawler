
Web Crawler for Email Address Extraction
       ~ Accenture Home Task ~
           - David Keter -

Written for Python 3.8
Dependencies:
    pip install asyncio aiohttp
    pip install pytest [for testing only]

To run:
    python crawler.py URL [URLs...]
    Where URL are the initial crawler seeds to search

The crawler avoids loops and will exit when there are no more links remaining,
but can keep going for a long time, depending on the provided seeds.
