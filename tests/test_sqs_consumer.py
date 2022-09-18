import asyncio

from comlink.consumer import SqsConsumer
from comlink.queue import SqsQueue
from tests import helpers


async def test_sqs_consumer_without_messages(sqs_queue: SqsQueue):
    """Test that the consumer works when there are no messages."""
    stop_event = asyncio.Event()
    handler = helpers.Handler(stop_event)

    consumer = SqsConsumer(queue=sqs_queue, handler=handler, batch_size=1)
    consumer_task = await consumer.start(stop_event=stop_event)
    await helpers.wait_first_else_cancel(stop_event.wait(), timeout=1)

    stop_event.set()
    await consumer_task
    assert not handler.received_messages


async def test_sqs_consumer_with_messages(sqs_queue: SqsQueue):
    """Test that the consumer yields messages when there are some."""
    stop_event = asyncio.Event()
    handler = helpers.Handler(stop_event)
    await sqs_queue.put("test")

    consumer = SqsConsumer(queue=sqs_queue, handler=handler, batch_size=1)
    consumer_task = await consumer.start(stop_event=stop_event)
    await helpers.wait_first_else_cancel(stop_event.wait(), timeout=1)

    stop_event.set()
    await consumer_task
    assert handler.received_messages
    assert handler.received_messages[0] == "test"


async def test_sqs_async_handler(sqs_queue: SqsQueue):
    """Test that the consumer works with async handlers."""
    stop_event = asyncio.Event()
    handler = helpers.AsyncHandler(stop_event)
    await sqs_queue.put("test")

    consumer = SqsConsumer(queue=sqs_queue, handler=handler, batch_size=1)
    consumer_task = await consumer.start(stop_event=stop_event)
    await helpers.wait_first_else_cancel(stop_event.wait(), timeout=1)

    stop_event.set()
    await consumer_task
    assert handler.received_messages
    assert handler.received_messages[0] == "test"


async def test_sqs_consumer_remove_handled_message(sqs_queue: SqsQueue):
    """Test that the consumer removes correctly processed messages."""
    stop_event = asyncio.Event()
    handler = helpers.Handler(stop_event)
    await sqs_queue.put("test")

    consumer = SqsConsumer(queue=sqs_queue, handler=handler, batch_size=1)
    consumer_task = await consumer.start(stop_event=stop_event)
    await helpers.wait_first_else_cancel(stop_event.wait(), timeout=1)
    stop_event.set()
    await consumer_task

    messages = await sqs_queue.take(
        max_messages=1, visibility_timeout=0, wait_time_seconds=0
    )
    assert not messages, "we shouldn't have any messages left in the queue"


async def test_sqs_consumer_left_not_handled_messages(sqs_queue: SqsQueue):
    """Test that the consumer keeps messages that are not processed."""
    stop_event = asyncio.Event()
    handler = helpers.BrokenHandler(stop_event)

    await sqs_queue.put("test")
    consumer = SqsConsumer(
        queue=sqs_queue, handler=handler, batch_size=1, visibility_timeout=1
    )
    consumer_task = await consumer.start(stop_event=stop_event)
    await helpers.wait_first_else_cancel(stop_event.wait(), timeout=1)
    stop_event.set()
    await consumer_task

    messages = await sqs_queue.take(
        max_messages=1, visibility_timeout=1, wait_time_seconds=2
    )
    assert messages, "we should have a message left in the queue"
