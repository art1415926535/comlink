import asyncio
from asyncio import Task
from typing import Any, Coroutine


async def wait_first_else_cancel(
    *aws: Coroutine | Task, timeout: float = 1
) -> None:
    """Wait for the first task to finish, else cancel the others."""
    tasks = []
    for a in aws:
        if isinstance(a, asyncio.Task):
            tasks.append(a)
        elif asyncio.iscoroutine(a):
            tasks.append(asyncio.create_task(a))
        else:
            raise TypeError("Expected coroutine or task")

    _, pending = await asyncio.wait(
        tasks, return_when=asyncio.FIRST_COMPLETED, timeout=timeout
    )

    for task in pending:
        if not task.done():
            task.cancel()

    for task in tasks:
        try:
            await task
        except asyncio.CancelledError:
            pass


class Handler:
    def __init__(self, handled: asyncio.Event | None) -> None:
        self.handled = handled
        self.received_messages = []

    def __call__(self, msg: Any) -> None:
        self.received_messages.append(msg)
        if self.handled is not None:
            self.handled.set()


class BrokenHandler(Handler):
    def __call__(self, msg: Any) -> None:
        self.received_messages.append(msg)
        if self.handled is not None:
            self.handled.set()

        raise Exception("Broken handler")
