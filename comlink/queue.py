from typing import Any, Protocol


class Queue(Protocol):
    async def put(self, data: Any, **kwargs) -> Any:
        ...

    async def take(self, **kwargs) -> Any:
        ...

    async def remove(self, **kwargs) -> Any:
        ...


class SqsQueue(Queue):
    def __init__(self, url: str, client: Any):
        self.url = url
        self.client = client

    async def put(self, data: str, **kwargs) -> Any:
        """Put data into the queue."""
        return await self.client.send_message(
            QueueUrl=self.url, MessageBody=data, **kwargs
        )

    async def take(
        self,
        /,
        max_messages: int,
        visibility_timeout: int,
        wait_time_seconds: int,
        **kwargs: Any,
    ) -> list[Any]:
        """Take SQS message from the queue."""
        messages = await self.client.receive_message(
            QueueUrl=self.url,
            MaxNumberOfMessages=max_messages,
            VisibilityTimeout=visibility_timeout,
            WaitTimeSeconds=wait_time_seconds,
            **kwargs,
        )
        return messages.get("Messages", [])

    async def remove(self, /, receipt_handle: str, **kwargs) -> Any:
        """Remove SQS message from the queue by receipt handle."""
        return await self.client.delete_message(
            QueueUrl=self.url,
            ReceiptHandle=receipt_handle,
            **kwargs,
        )
