import asyncio
import datetime

from aiobotocore.session import get_session

from comlink import SqsConsumer, SqsQueue


async def example(sqs_client, queue_url):
    # Create a queue object
    sqs_queue = SqsQueue(url=queue_url, client=sqs_client)

    # Event for stopping the consumer
    stop_event = asyncio.Event()
    # Create a consumer with a handler that just prints the message
    consumer = SqsConsumer(queue=sqs_queue, handler=print)
    # Start the consumer
    consumer_task = await consumer.start(stop_event=stop_event)

    # Send a message to the queue
    await sqs_queue.put(f"{datetime.datetime.now()} Hello, world!")
    # Wait for 1 second for the message to be processed
    await asyncio.sleep(1)

    # Stop the consumer
    stop_event.set()
    # Wait for the consumer to stop
    await consumer_task


async def main():
    async with get_session().create_client(
        "sqs",
        region_name="us-east-1",
        endpoint_url="http://localhost:4566",
        aws_secret_access_key="test",
        aws_access_key_id="test",
    ) as sqs_client:
        queue_info = await sqs_client.create_queue(QueueName="basic-example")

        await example(sqs_client, queue_info["QueueUrl"])


if __name__ == "__main__":
    asyncio.run(main())
