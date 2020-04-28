from services import FilterService
from asyncio import Queue
import pytest


@pytest.fixture
def service():
    yield FilterService(Queue(), Queue())


def test_pass_filter(event_loop, service):
    """
    Check new items aren't filtered out
    """
    service._in_queue.put_nowait('aaa')
    service._in_queue.put_nowait(FilterService.HALT)
    event_loop.run_until_complete(service.run())

    assert service._in_queue.qsize() == 0
    assert service._out_queue.qsize() == 1
    assert len(service._seen_filter) == 1


def test_block_filter(event_loop, service):
    """
    Check existing items are filtered out
    """
    service._seen_filter.add('aaa')

    service._in_queue.put_nowait('aaa')
    service._in_queue.put_nowait(FilterService.HALT)
    event_loop.run_until_complete(service.run())

    assert service._in_queue.qsize() == 0
    assert service._out_queue.qsize() == 0
    assert len(service._seen_filter) == 1


def test_unique(event_loop, service):
    """
    Check same item twice yields only one
    """
    service._in_queue.put_nowait('aaa')
    service._in_queue.put_nowait('bbb')
    service._in_queue.put_nowait('aaa')
    service._in_queue.put_nowait(FilterService.HALT)
    event_loop.run_until_complete(service.run())

    assert service._in_queue.qsize() == 0
    assert service._out_queue.qsize() == 2
    assert len(service._seen_filter) == 2
