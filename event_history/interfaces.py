"""Module for all interfaces for event_history package."""

import typing


class IEventHistoryService(typing.Protocol):
    """Event History service interface that is expected by this library."""

    def save(self, event_object, session=None) -> None:
        """Save event history object."""


class IEventService(typing.Protocol):
    """Event service interface that is expected by this library."""

    def save(self, event_object, session=None) -> None:
        """Save event object."""

    def update(self, event_object, session=None) -> None:
        """Update event object."""
