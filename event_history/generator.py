"""Module for generating event history service."""
from datetime import datetime

from event_history.interfaces import (
    IEventHistoryService,
    IEventService,
)


class TransactionService:
    def __init__(
        self,
        event_service: IEventService,
        history_service: IEventHistoryService,
    ):
        """Initialiser."""
        self.event_service = event_service
        self.history_service = history_service

    def save(self, event_object, session=None):
        """Save event history object."""
        event_object.version = 1  # first version of the event
        event_object.timestamp = datetime.now()
        self.history_service.save(event_object, session=session)
        self.event_service.save(event_object, session=session)

    def update(self, event_object, session=None):
        """Update event history object."""
        event_object.version += 1
        event_object.timestamp = datetime.now()
        self.history_service.save(event_object, session=session)
        self.event_service.update(event_object, session=session)
