import asyncio
import os
import signal

from comlink import signal_event


async def test_signal_event():
    """Tests that the signal event is set when a signal is received."""
    event = signal_event(signals={signal.SIGUSR1: "SIGUSR1"})
    assert event.is_set() is False

    # Send a signal to the process
    os.kill(os.getpid(), signal.SIGUSR1)
    await asyncio.wait_for(event.wait(), timeout=1)

    assert event.is_set()
