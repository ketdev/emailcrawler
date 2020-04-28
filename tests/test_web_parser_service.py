from services import WebParserService
from asyncio import Queue
import pytest


@pytest.fixture
def service():
    yield WebParserService(Queue(), Queue(), Queue())


def test_hyperlink(event_loop, service):
    """
    Check it identifies hyperlinks
    """
    service._in_queue.put_nowait("JUNK")
    service._in_queue.put_nowait("JUNK href='https://test' JUNK")
    service._in_queue.put_nowait("JUNK href=JUNK JUNK")
    service._in_queue.put_nowait(WebParserService.HALT)
    event_loop.run_until_complete(service.run())

    assert service._in_queue.qsize() == 0
    assert service._email_queue.qsize() == 0
    assert service._hyperlink_queue.qsize() == 1
    assert service._hyperlink_queue.get_nowait() == 'https://test'


def test_email(event_loop, service):
    """
    Check it identifies hyperlinks
    """
    service._in_queue.put_nowait("JUNK")
    service._in_queue.put_nowait("JUNK py@te.st.com.. JUNK")
    service._in_queue.put_nowait("JUNK JUNK")
    service._in_queue.put_nowait(WebParserService.HALT)
    event_loop.run_until_complete(service.run())

    assert service._in_queue.qsize() == 0
    assert service._email_queue.qsize() == 1
    assert service._hyperlink_queue.qsize() == 0
    assert service._email_queue.get_nowait() == 'py@te.st.com'


def test_multiple(event_loop, service):
    """
    Check it identifies hyperlinks
    """
    service._in_queue.put_nowait("JUNK")
    service._in_queue.put_nowait("JUNK py@te.st.com2 JUNK")
    service._in_queue.put_nowait("JUNK href='https://test1' JUNK")
    service._in_queue.put_nowait("JUNK href=JUNK JUNK")
    service._in_queue.put_nowait("JUNK py@te.st.com1 JUNK")
    service._in_queue.put_nowait("JUNK href='https://test2' JUNK")
    service._in_queue.put_nowait(WebParserService.HALT)
    event_loop.run_until_complete(service.run())

    assert service._in_queue.qsize() == 0
    assert service._email_queue.qsize() == 2
    assert service._hyperlink_queue.qsize() == 2
    assert service._hyperlink_queue.get_nowait() == 'https://test1'
    assert service._hyperlink_queue.get_nowait() == 'https://test2'
    assert service._email_queue.get_nowait() == 'py@te.st.com2'
    assert service._email_queue.get_nowait() == 'py@te.st.com1'
