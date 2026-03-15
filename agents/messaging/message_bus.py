"""Message bus placeholder for Issue #8."""

from typing import Optional


class MessageBus:
    """Simple shell to be expanded with publish/subscribe logic in Issue #8."""

    def __init__(self) -> None:
        self.ready = True


_message_bus: Optional[MessageBus] = None


def get_message_bus() -> MessageBus:
    """Return a singleton message bus shell."""
    global _message_bus
    if _message_bus is None:
        _message_bus = MessageBus()
    return _message_bus
