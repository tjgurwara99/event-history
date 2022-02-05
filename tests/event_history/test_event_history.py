"""Module for testing the event history.

   Copyright 2022 Tajmeet Singh

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""
import dataclasses
import typing
from datetime import datetime

import pytest
from bson import ObjectId

from event_history import TransactionService


@dataclasses.dataclass
class Event:
    """Event dataclass."""

    event: str
    timestamp: datetime
    version: int = 0
    _id: ObjectId = None

    def to_dict(self):
        """Return dict representation of the event."""
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {
                key: value for key, value in x if value is not None
            },
        )


class FakeContextManager:
    """Fake context manager."""

    def __init__(
        self,
        fail_on_model_save=False,
        fail_on_model_update=False,
        fail_on_history_save=False,
    ):
        """Initialiser."""
        self.fail_on_model_save = fail_on_model_save
        self.fail_on_model_update = fail_on_model_update
        self.fail_on_history_save = fail_on_history_save
        self.committed = False
        self.rollbacked = False

    def __enter__(self):
        """Enter."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit."""
        if exc_type is not None:
            self.rollback(exc_val.args[0])
            return
        self.commit()

    def commit(self):
        """Commit."""
        self.committed = True

    def rollback(self, message=None):
        """Rollback."""
        self.rollbacked = True
        self.rollback_message = message


class EventService:
    """Event Service."""

    def __init__(self):
        """Initialiser."""
        self.events: typing.List[Event] = []

    def save(self, event_object: Event, session=None):
        """Save event object."""
        if session:
            if session.fail_on_model_save:
                raise Exception("Failed to save event object")
        self.events.append(event_object)

    def update(self, event_object: Event, session=None):
        """Update event object."""
        if session:
            if session.fail_on_model_update:
                raise Exception("Failed to update event object")
        for index, event in enumerate(self.events):
            if event.event == event_object.event:
                self.events[index] = event_object

    def get(self, event_name: str):
        """Get event object."""
        for event in self.events:
            if event.event == event_name:
                return event
        return None


class EventHistoryService:
    """Event History Service."""

    def __init__(self):
        """Initialiser."""
        self.events: typing.List[Event] = []

    def save(self, event_object: Event, session=None):
        """Save event history object."""
        if session:
            if session.fail_on_history_save:
                raise Exception("Failed to save event history object")
        for event in self.events:
            if (
                event.event == event_object.event
                and event.version == event_object.version
            ):
                raise Exception("Event already exists")
        self.events.append(event_object)


class TestTransactionService:
    """Tests for the Transaction Service."""

    def test_transaction_service_save(self):
        """Test transaction service success."""
        event_service = EventService()
        event_history_service = EventHistoryService()
        transaction_service = TransactionService(
            event_service=event_service,
            history_service=event_history_service,
        )
        event = Event(
            event="event_name",
            timestamp=datetime.now(),
        )
        with FakeContextManager() as session:
            event_object = dataclasses.replace(event)
            transaction_service.save(event_object, session=session)
            assert event_service.events == [event_object]
            assert event_history_service.events == [event_object]

        assert session.committed
        assert not session.rollbacked
        with pytest.raises(Exception):
            with FakeContextManager(fail_on_history_save=True) as session:
                event_object = dataclasses.replace(event)
                event_object.event = "event_name_2"
                transaction_service.save(event_object, session=session)
        assert session.rollbacked
        assert (
            session.rollback_message == "Failed to save event history object"
        )  # noqa: E501

        with pytest.raises(Exception):
            with FakeContextManager(fail_on_model_save=True) as session:
                event_object = dataclasses.replace(event)
                event_object.event = "new_event_name"
                transaction_service.save(event_object, session=session)
        assert session.rollbacked
        assert session.rollback_message == "Failed to save event object"

    def test_transaction_service_update(self):
        """Test transaction service success."""
        event_service = EventService()
        event_history_service = EventHistoryService()
        transaction_service = TransactionService(
            event_service=event_service,
            history_service=event_history_service,
        )
        event = Event(
            event="event_name",
            timestamp=datetime.now(),
        )
        with FakeContextManager() as session:
            event_object = dataclasses.replace(event)
            transaction_service.save(event_object, session=session)
            assert event_service.events[0].event == event_object.event
            assert event_service.events[0].version == event_object.version
            assert event_history_service.events[0].event == event_object.event
            assert event_history_service.events[0].version == event_object.version

        with FakeContextManager() as session:
            event_object = dataclasses.replace(event_service.get("event_name"))
            transaction_service.update(event_object, session=session)
            assert len(event_service.events) == 1
            assert event_service.events[0].event == event_object.event
            assert event_service.events[0].version == event_object.version
            assert len(event_history_service.events) == 2
            assert event_history_service.events[1].event == event_object.event

        assert session.committed
        assert not session.rollbacked
        with pytest.raises(Exception):
            with FakeContextManager(fail_on_history_save=True) as session:
                event_object = dataclasses.replace(event)
                event_object.event = "event_name_2"
                transaction_service.update(event_object, session=session)
        assert session.rollbacked
        assert session.rollback_message == "Failed to save event history object"

        with pytest.raises(Exception):
            with FakeContextManager(fail_on_model_update=True) as session:
                event_object = dataclasses.replace(event)
                event_object.event = "new_event_name"
                transaction_service.update(event_object, session=session)
        assert session.rollbacked
        assert session.rollback_message == "Failed to update event object"
