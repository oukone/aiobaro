import json
from enum import Enum, unique
from typing import Any, Dict, Union

import httpx
from httpx._models import (
    ByteStream,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
)

FilterT = Union[None, str, Dict[Any, Any]]


@unique
class HttpVerbs(str, Enum):
    put: str = "PUT"
    get: str = "GET"
    head: str = "HEAD"
    post: str = "POST"
    trace: str = "TRACE"
    patch: str = "PATCH"
    delete: str = "DELETE"
    connect: str = "CONNECT"
    options: str = "OPTIONS"


@unique
class UserKind(str, Enum):
    user: str = "user"
    guest: str = "guest"


@unique
class MessageDirection(Enum):
    """Enum representing the direction messages should be fetched from."""

    back: int = 0
    front: int = 1


@unique
class ResizingMethod(str, Enum):
    """Enum representing the desired resizing method for a thumbnail.
    "scale" maintains the original aspect ratio of the image,
    "crop" provides an image in the aspect ratio of the requested size.
    """

    scale: str = "scale"
    crop: str = "crop"


@unique
class RoomVisibility(str, Enum):
    """Enum representing the desired visibility when creating a room.
    "public" means the room will be shown in the server's room directory.
    "private" will hide the room from the server's room directory.
    """

    private: str = "private"
    public: str = "public"


@unique
class RoomPreset(str, Enum):
    """Enum representing the available rule presets when creating a room.
    "private_chat" makes the room invite-only and allows guests.
    "trusted_private_chat" is the same as above, but also gives all invitees
    the same power level as the room's creator.
    "public_chat" makes the room joinable by anyone without invitations, and
    forbid guests.
    """

    private_chat = "private_chat"
    trusted_private_chat = "trusted_private_chat"
    public_chat = "public_chat"


@unique
class EventFormat(str, Enum):
    """Available formats in which a filter can make the server return events.
    "client" will return the events in a format suitable for clients.
    "federation" will return the raw event as received over federation.
    """

    client = "client"
    federation = "federation"


@unique
class PushRuleKind(str, Enum):
    """Push rule kinds defined by the Matrix spec, ordered by priority."""

    override = "override"
    content = "content"
    room = "room"
    sender = "sender"
    underride = "underride"


@unique
class Presence(str, Enum):
    """Presence state for a user."""

    online = "online"
    offline = "offline"
    unavailable = "unavailable"


class MatrixResponse:
    def __init__(self, response: httpx.Response):
        self.response = response

    def __repr__(self):
        return self.response.__repr__()

    @property
    def ok(self):
        try:
            self.response.raise_for_status()
        except httpx.HTTPStatusError:
            return False
        return True

    @property
    def status_code(self):
        return self.response.status_code

    def json(self):
        return self.response.json()

    def as_json(self):
        return json.dumps(self.response.json(), indent=4)
