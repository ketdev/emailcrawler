import logging
from .base_service import BaseService
from asyncio import Queue, ensure_future
from aiohttp import ClientSession, ClientError


class NetworkReaderService(BaseService):
    """
    Request website content
    """

    def __init__(self, task_counter, in_queue: Queue, out_queue: Queue):
        super().__init__(task_counter, in_queue)
        self._out_queue = out_queue

    async def handle(self, website):
        # create a new task for the network operation to keep running code
        ensure_future(self._get_request(website))

    async def _get_request(self, website):
        try:
            async with ClientSession() as session:
                async with session.get(website.url) as resp:
                    logging.info('GET request: %s', website.url)
                    website.content = await resp.text()
                    await self._out_queue.put(website)
        except ClientError:
            pass
        except UnicodeDecodeError:
            pass
        except OSError:
            pass
