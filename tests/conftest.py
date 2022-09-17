import logging
import uuid
from typing import Any, AsyncGenerator

import pytest
from aiobotocore.session import get_session

from comlink.queue import SqsQueue


logging.basicConfig(level=logging.DEBUG)
logging.getLogger("botocore").setLevel(logging.WARNING)

log = logging.getLogger(__name__)


@pytest.fixture
async def sqs_client() -> AsyncGenerator[Any, None]:
    """Create a SQS client."""
    session = get_session()

    async with session.create_client(
        "sqs",
        region_name="us-east-1",
        endpoint_url="http://localhost:4566",
        aws_secret_access_key="test",
        aws_access_key_id="test",
    ) as sqs:
        yield sqs


@pytest.fixture
async def sqs_queue_url(
    sqs_client: Any, request: pytest.FixtureRequest
) -> AsyncGenerator[str, None]:
    """Create a SQS queue and return its URL."""
    test_name = request.node.name
    queue_name = f"{test_name}-{uuid.uuid4()}"
    await sqs_client.create_queue(QueueName=queue_name)
    log.info("Created queue", extra={"queue_name": queue_name})

    queue_info = await sqs_client.get_queue_url(QueueName=queue_name)
    queue_url = queue_info["QueueUrl"]

    yield queue_url

    await sqs_client.delete_queue(QueueUrl=queue_url)
    log.info("Deleted queue", extra={"queue_name": queue_name})


@pytest.fixture
async def sqs_queue(
    sqs_queue_url: str, sqs_client: Any
) -> AsyncGenerator[SqsQueue, None]:
    """Create a SQS queueL."""
    yield SqsQueue(url=sqs_queue_url, client=sqs_client)
