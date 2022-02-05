"""Module for generating event history service.

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
from datetime import datetime

from event_history.interfaces import IEventHistoryService, IEventService


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
