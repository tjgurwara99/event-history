"""Module for event related services."""

import subprocess
import dataclasses
from datetime import datetime
import pymongo
from bson import ObjectId
from event_history import TransactionService
import time


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


CON_STR = "mongodb://mongo1:30001,mongo2:30002,mongo3:30003/?replicaSet=my-replica-set"  # noqa: E501


class EventService:
    """Event Service."""

    def __init__(self, client):
        """Initialiser."""
        self.client = client
        self.db = self.client.test_database
        self.collection = self.db.test_collection
        self.collection.create_index(
            [
                ("event", 1),
            ],
            unique=True,
        )

    def save(self, event_object: Event, session=None):
        """Save event object."""
        self.collection.insert_one(
            event_object.to_dict(),
            session=session,
        )

    def update(self, event_object: Event, session=None):
        """Update event object."""
        self.collection.update_one(
            {
                "_id": event_object._id,
            },
            {
                "$set": event_object.to_dict(),
            },
            session=session,
        )

    def get(self, event_name: str):
        """Get event object."""
        return self.collection.find_one(
            {
                "event": event_name,
            },
        )


class EventHistoryService:
    """Event History Service."""

    def __init__(self, client):
        """Initialiser."""
        self.client = client
        self.db = self.client.test_database
        self.collection = self.db.test_history_collection
        self.collection.create_index(
            [
                ("event", 1),
                ("version", 1),
            ],
            unique=True,
        )

    def save(self, event_object: Event, session=None):
        """Save event history object."""
        event_dict = event_object.to_dict()
        event_dict.pop("_id", None)
        self.collection.insert_one(
            event_dict,
            session=session,
        )


if __name__ == "__main__":

    subprocess.run(
        "docker-compose up -d",
        shell=True,
    )
    time.sleep(30)

    client = pymongo.MongoClient(CON_STR)
    event_service = EventService(client)
    event_history_service = EventHistoryService(client)
    transaction_service = TransactionService(
        event_service,
        event_history_service,
    )

    event = Event(
        event="test_event",
        timestamp=datetime.now(),
    )

    with client.start_session() as session:
        transaction_service.save(
            event_object=event,
            session=session,
        )

    returned_event = event_service.get(event.event)

    assert returned_event["version"] == 1
    assert returned_event["event"] == event.event

    with client.start_session() as session:
        transaction_service.update(
            event_object=Event(**returned_event),
            session=session,
        )

    returned_event = event_service.get(event.event)

    assert returned_event["version"] == 2
    assert returned_event["event"] == event.event

    # at this point check the mongo shell to see the two different histories
    # for the event and also check that the latest record on the event.
    breakpoint()

    event_service.collection.delete_many({"event": event.event})
    event_history_service.collection.delete_many({"event": event.event})
