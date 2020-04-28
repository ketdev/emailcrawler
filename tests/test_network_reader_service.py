from services import NetworkReaderService
from asyncio import Queue, wait
import pytest


@pytest.fixture
def service():
    yield NetworkReaderService(Queue(), Queue())


def test_bad_url(event_loop, service):
    """
    Check url errors are ignored
    """
    service._in_queue.put_nowait('bad')
    service._in_queue.put_nowait(NetworkReaderService.HALT)
    event_loop.run_until_complete(service.run())

    assert service._in_queue.qsize() == 0
    assert service._out_queue.qsize() == 0


def test_valid_url(event_loop, service):
    """
    Check url errors are ignored
    """
    service._in_queue.put_nowait('https://www.google.com/')

    # give it some time to get page
    task = service.run()
    event_loop.run_until_complete(wait([task, ], timeout=2))
    event_loop.run_until_complete(service.stop())

    assert service._in_queue.qsize() == 0
    assert service._out_queue.qsize() == 1
