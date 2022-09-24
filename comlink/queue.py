from typing import Any, Callable, Generic, TypeVar


Message = TypeVar("Message")


class SqsQueue(Generic[Message]):
    def __init__(
        self,
        url: str,
        client: Any,
        serializer: Callable[[Message], str] | None = None,
        deserializer: Callable[[str], Message] | None = None,
    ):
        self.url = url
        self.client = client
        self.serializer = serializer
        self.deserializer = deserializer

    async def put(self, data: Message, **kwargs) -> Any:
        """Put data into the queue."""
        if self.serializer is not None:
            data = self.serializer(data)

        return await self.client.send_message(
            QueueUrl=self.url, MessageBody=data, **kwargs
        )

    async def take(
        self,
        max_messages: int,
        visibility_timeout: int,
        wait_time_seconds: int,
        **kwargs: Any,
    ) -> list[Message]:
        """Take SQS message from the queue."""
        messages_response = await self.client.receive_message(
            QueueUrl=self.url,
            MaxNumberOfMessages=max_messages,
            VisibilityTimeout=visibility_timeout,
            WaitTimeSeconds=wait_time_seconds,
            **kwargs,
        )
        messages = messages_response.get("Messages", [])

        if self.deserializer is not None:
            for message in messages:
                message["Body"] = self.deserializer(message["Body"])

        return messages

    async def remove(self, receipt_handle: str, **kwargs) -> Any:
        """Remove SQS message from the queue by receipt handle."""
        return await self.client.delete_message(
            QueueUrl=self.url,
            ReceiptHandle=receipt_handle,
            **kwargs,
        )
