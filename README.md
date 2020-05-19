
# Web Crawler for Email Address Extraction
Written for Python 3.8

Dependencies:
------------
    pip install asyncio requests
    pip install pytest [for testing only]

To run:
------------
    python crawler.py [--depth X] URL [URLs...]
        Where URL are the initial crawler seeds to search
        Depth is an optional limit to the number of hyperlinks followed

Notes:
------------
    The crawler avoids loops and will exit when there are no more links remaining,
    but can keep going for a long time, depending on the provided seeds, or infinite depth.
