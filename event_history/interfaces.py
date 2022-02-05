"""Module for all interfaces for event_history package.

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
