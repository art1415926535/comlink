import asyncio

from aiobotocore.session import get_session

from comlink import SqsConsumer, SqsQueue, signal_event


async def example(sqs_client, queue_url):
    sqs_queue = SqsQueue(url=queue_url, client=sqs_client)
    stop_event = signal_event()

    consumer = SqsConsumer(queue=sqs_queue, handler=print)
    consumer_task = await consumer.start(stop_event=stop_event)

    await consumer_task


async def main():
    async with get_session().create_client(
        "sqs",
        region_name="us-east-1",
        endpoint_url="http://localhost:4566",
        aws_secret_access_key="test",
        aws_access_key_id="test",
    ) as sqs_client:
        queue_info = await sqs_client.create_queue(
            QueueName="graceful-shutdown-example"
        )

        await example(sqs_client, queue_info["QueueUrl"])


if __name__ == "__main__":
    asyncio.run(main())
