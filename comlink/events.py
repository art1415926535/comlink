import asyncio
import logging
import signal


log = logging.getLogger(__name__)

default_signals: dict[int, str] = {
    signal.SIGINT: "SIGINT",
    signal.SIGTERM: "SIGTERM",
}


def _event_handler(
    event: asyncio.Event, signal_name: str, log_level: int
) -> None:
    """Set an event when a signal is received."""
    event.set()
    log.log(log_level, "Received signal", extra={"signal": signal_name})


def signal_event(
    signals: dict[int, str] | None = None,
    log_level: int = logging.WARNING,
    loop: asyncio.AbstractEventLoop | None = None,
) -> asyncio.Event:
    """Create an event that is set when a signal is received."""
    _signals = signals or default_signals
    _loop = loop or asyncio.get_running_loop()

    event = asyncio.Event()
    for sig in _signals:
        _loop.add_signal_handler(
            sig, lambda: _event_handler(event, _signals[sig], log_level)
        )

    return event
