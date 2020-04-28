from services import EmailDisplayService
from asyncio import Queue
import pytest


@pytest.fixture
def service():
    yield EmailDisplayService(Queue())


def test_print(capsys, event_loop, service):
    """
    Check print sanity
    """
    service._in_queue.put_nowait('ping')
    service._in_queue.put_nowait(EmailDisplayService.HALT)
    event_loop.run_until_complete(service.run())

    assert service._in_queue.qsize() == 0
    captured = capsys.readouterr()
    assert captured.out == "ping\n"
