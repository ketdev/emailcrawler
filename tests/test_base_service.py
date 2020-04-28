from services.base_service import BaseService
from asyncio import Queue
import asyncio
import pytest


@pytest.fixture
def service():
    yield BaseService(Queue())


def test_stop(event_loop, service):
    """
    Check sending a stop (None) doesn't hang
    """
    event_loop.run_until_complete(service.stop())
    wait = asyncio.wait([service.run(), ], timeout=2)
    done, pending = event_loop.run_until_complete(wait)
    assert len(done) == 1
    assert len(pending) == 0
    assert service._in_queue.qsize() == 0


def test_queue_loop(event_loop, service):
    """
    Check we reach timeout
    """
    wait = asyncio.wait([service.run(), ], timeout=2)
    done, pending = event_loop.run_until_complete(wait)
    assert len(done) == 0
    assert len(pending) == 1
    event_loop.run_until_complete(service.stop())
    assert service._in_queue.qsize() == 0


def test_call_handle(event_loop, service):
    """
    Check we called unimplemented handle
    """
    event_loop.run_until_complete(service._in_queue.put('test'))
    with pytest.raises(NotImplementedError):
        event_loop.run_until_complete(service.run())
    assert service._in_queue.qsize() == 0


def test_clear_stop(event_loop, service):
    """
    Check sending a stop clears all other items first
    """
    event_loop.run_until_complete(service._in_queue.put('test'))
    event_loop.run_until_complete(service.stop())
    wait = asyncio.wait([service.run(), ], timeout=2)
    done, pending = event_loop.run_until_complete(wait)
    assert len(done) == 1
    assert len(pending) == 0
    assert service._in_queue.qsize() == 0
