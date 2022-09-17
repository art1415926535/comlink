from typing import Any

from comlink.queue import SqsQueue


async def test_sqs_queue_put_data(sqs_client: Any, sqs_queue_url: str) -> None:
    """Test that we can put data into the queue."""
    queue = SqsQueue(url=sqs_queue_url, client=sqs_client)

    response = await queue.put("test")

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


async def test_sqs_queue_take_data(
    sqs_client: Any, sqs_queue_url: str
) -> None:
    """Test that we can take data from the queue."""
    queue = SqsQueue(url=sqs_queue_url, client=sqs_client)
    await queue.put("test")

    messages = await queue.take(
        max_messages=1,
        visibility_timeout=1,
        wait_time_seconds=1,
    )

    assert messages[0]["Body"] == "test"


async def test_sqs_queue_remove_data(
    sqs_client: Any, sqs_queue_url: str
) -> None:
    """Test that we can remove data from the queue."""
    queue = SqsQueue(url=sqs_queue_url, client=sqs_client)
    await queue.put("test")
    messages = await queue.take(
        max_messages=1,
        visibility_timeout=1,
        wait_time_seconds=1,
    )

    response = await queue.remove(messages[0]["ReceiptHandle"])
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    messages = await queue.take(
        max_messages=1,
        visibility_timeout=1,
        wait_time_seconds=1,
    )
    assert not messages
