"""
base_module.py — Abstract base class every analysis module must implement.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from event_record import EventRecord


class BaseModule(ABC):
    """
    Interface for a processing module.

    Lifecycle
    ---------
    1. Framework calls ``begin()`` once before the event loop.
    2. Framework calls ``process(record)`` for every event.
    3. Framework calls ``end()`` once after the event loop.

    Modules should write their output into ``record.extras[self.name]``.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique string identifier — also used as the key in record.extras."""

    def begin(self) -> None:
        """Called once before the first event. Override for setup."""

    @abstractmethod
    def process(self, record: EventRecord) -> None:
        """
        Process one event and append results to record.extras[self.name].
        Must not raise; catch internal errors and store them if needed.
        """

    def end(self) -> None:
        """Called once after the last event. Override for teardown / summaries."""
