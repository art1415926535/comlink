import asyncio
import logging
from asyncio import Task
from typing import Any, Callable, Coroutine, Generic, TypeVar

from .queue import SqsQueue


log = logging.getLogger(__name__)


MessageType = TypeVar("MessageType")


class SqsConsumer(Generic[MessageType]):
    def __init__(
        self,
        queue: SqsQueue,
        handler: Callable,
        parser: Callable[[str], MessageType] | None = None,
        batch_size: int = 1,
        visibility_timeout: int = 120,
        wait_time_seconds: int = 20,
    ):
        """
        SQS message consumer.

        Args:
            queue: SQS queue object.
            handler: Message handler function (sync/async).
            batch_size: Number of messages to receive in one request from sqs.
            visibility_timeout: The duration (in seconds) that the received messages are hidden from subsequent.
            wait_time_seconds: Wait time for long polling.
        """
        self.queue = queue
        self.handler = handler
        self.parser = parser

        self.batch_size = batch_size
        self.visibility_timeout = visibility_timeout
        self.wait_time_seconds = wait_time_seconds

        self._handle: Callable[
            [str | MessageType], Coroutine
        ] = self._get_handler_func()

    def _get_handler_func(self) -> Callable[[Any], Coroutine]:
        real_handler = self.handler
        if hasattr(real_handler, "__call__"):
            real_handler = real_handler.__call__

        if asyncio.iscoroutinefunction(real_handler):
            return self._handle_async

        return self._handle_sync

    async def start(self, stop_event: asyncio.Event) -> Task:
        task = asyncio.create_task(self._handler_loop(stop_event))
        log.debug("Handler loop task created")

        task.add_done_callback(
            lambda x: log.debug("Message handler task done")
        )

        return task

    async def _handler_loop(self, stop_event: asyncio.Event) -> None:
        log.debug("Handler loop task started")

        while not stop_event.is_set():
            log.debug("Start message handler iteration")
            await self._handle_messages(stop_event)

    async def _handle_messages(self, stop_event: asyncio.Event) -> None:
        get_messages_task = asyncio.create_task(
            self.queue.take(
                max_messages=self.batch_size,
                visibility_timeout=self.visibility_timeout,
                wait_time_seconds=self.wait_time_seconds,
            )
        )

        stop_task = asyncio.create_task(stop_event.wait())
        tasks: list[asyncio.Task] = [get_messages_task, stop_task]
        done, _ = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_COMPLETED
        )

        if stop_task in done:
            log.debug("Stopping message handler")
            get_messages_task.cancel()
            return

        if get_messages_task in done:
            stop_task.cancel()
            messages = get_messages_task.result()
            log.debug("Received messages", extra={"count": len(messages)})

            for message in messages:
                if stop_event.is_set():
                    break

                try:
                    data = message["Body"]
                    if self.parser is not None:
                        data = self.parser(data)
                    await self._handle(data)
                except Exception as e:
                    log.exception("Message handler error", exc_info=e)
                    continue

                await self.queue.remove(message["ReceiptHandle"])

    async def _handle_async(self, message: str | MessageType) -> None:
        await self.handler(message)

    async def _handle_sync(self, message: str | MessageType) -> None:
        await asyncio.to_thread(self.handler, message)
