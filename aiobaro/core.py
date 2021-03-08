import functools
import json
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union
from uuid import UUID

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

from .models import (
    EventFormat,
    FilterT,
    HttpVerbs,
    MessageDirection,
    PushRuleKind,
    ResizingMethod,
    RoomPreset,
    RoomVisibility,
    UserKind,
)
from .tools import login_required, matrix_client


class BaseMatrixClient:
    def __init__(
        self,
        homeserver: str,
        access_token: str = None,
        version: str = "r0",
        client=matrix_client,
    ):
        self.version = version
        self.homeserver = homeserver
        self.access_token = access_token
        self.client = functools.partial(
            matrix_client,
            self.client_path,
            access_token=self.access_token,
        )

    @property
    def client_path(self):
        return f"{self.homeserver.strip('/')}/_matrix/client/{self.version}/"

    async def __call__(self, *args, **kwargs):
        return await self.client(*args, **kwargs)


class MatrixClient(BaseMatrixClient):
    async def login_info(self) -> httpx.Response:
        """Get the homeserver's supported login types

        * Matrix Spec
        5.5.1   GET /_matrix/client/r0/login
        Rate-limited:   Yes.
        Requires auth:  No.
        """
        return await self.client("GET", "login")

    async def login(
        self,
        user: str,
        password: str = None,
        device_name: Optional[str] = "",
        device_id: Optional[str] = "",
    ) -> httpx.Response:
        """Authenticate the user.
        Args:
            user (str): The fully qualified user ID or just local part of the
                user ID, to log in.
            password (str): The user's password.
            device_name (str): A display name to assign to a newly-created
                device. Ignored if device_id corresponds to a known device
            device_id (str): ID of the client device. If this does not
                correspond to a known client device, a new device will be
                created.

        * Matrix Spec
        5.5.2   POST /_matrix/client/r0/login
        Content-Type: application/json
        body = {
            "type": "m.login.password",
            "identifier": {
                "type": "m.id.user",
                "user": "cheeky_monkey"
            },
            "password": "ChangeMe",
            "device_id": "GHTYAJCE",
            "initial_device_display_name": "Jungle Phone"
        }
        Rate-limited:   Yes.
        Requires auth:  No.
        """
        data = {
            "type": "m.login.password",
            "identifier": {"type": "m.id.user", "user": user.lower()},
            "password": password,
            "device_id": device_id,
            "initial_device_display_name": device_name
            or f"{user.capitalize()}' device",
        }
        response = await self.client(
            "POST",
            "login",
            json=dict(filter(lambda x: x[1], data.items())),
        )
        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
        return response

    async def register(
        self,
        user: str,
        password: str = None,
        kind: UserKind = "user",
        device_name: Optional[str] = "",
        device_id: Optional[str] = "",
    ) -> httpx.Response:
        """Register a new user.
        Args:
            user (str): The fully qualified user ID or just local part of the
                user ID, to log in.
            password (str): The user's password.
            device_name (str): A display name to assign to a newly-created
                device. Ignored if device_id corresponds to a known device
            device_id (str): ID of the client device. If this does not
                correspond to a known client device, a new device will be
                created.

        * Matrix Spec
        5.6.1   POST /_matrix/client/r0/register
        Content-Type: application/json
        body = {
            "auth": {
                "type": "m.login.dummy"
            },
            "username": "cheeky_monkey",
            "password": "ChangeMe",
            "device_id": "GHTYAJCE",
            "initial_device_display_name": "Jungle Phone",
            "inhibit_login": false
        }
        Rate-limited:   Yes.
        Requires auth:  No.
        """
        data = {
            **dict(
                filter(
                    lambda x: x[1],
                    {
                        "username": user.lower(),
                        "password": password,
                        "device_id": device_id,
                        "initial_device_display_name": device_name
                        or f"{user.capitalize()}' device",
                    }.items(),
                )
            ),
            "auth": {"type": "m.login.dummy"},
            "inhibit_login": False,
        }
        response = await self.client(
            "POST", "register", params={"kind": kind}, json=data
        )
        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
        return response

    async def logout(self, all_devices: bool = True) -> httpx.Response:
        """Logout the session.
        Args:
            all_devices (bool): Logout all sessions from all devices if set to True.

        * Matrix Spec
        5.5.3   POST /_matrix/client/r0/logout
        5.5.4   POST /_matrix/client/r0/logout/all
        Content-Type: application/json
        body = {}
        """
        return await self.client(
            "POST",
            "logout/all" if all_devices else "logout",
            json={},
        )

    async def sync(
        self,
        since: Optional[str] = None,
        timeout: Optional[int] = None,
        data_filter: FilterT = None,
        full_state: Optional[bool] = None,
        set_presence: Optional[str] = None,
    ) -> httpx.Response:
        """Synchronise the client's state with the latest state on the server.
        Args:
            since (str): TA point in time to continue a sync from.
            timeout (int): The maximum time to wait, in milliseconds, before
                returning this request.
            filter (Union[None, str, Dict[Any, Any]):
                A filter ID or dict that should be used for this sync request.
            full_state (bool, optional): Controls whether to include the full
                state for all rooms the user is a member of. If this is set to
                true, then all state events will be returned, even if since is
                non-empty. The timeline will still be limited by the since
                parameter.
            set_presence (str, optinal): Controls whether the client is automatically
                marked as online by polling this API. If this parameter is omitted
                then the client is automatically marked as online when it uses this API.
                Otherwise if the parameter is set to "offline" then the client is not
                marked as being online when it uses this API. When set to "unavailable",
                the client is marked as being idle.
                One of: ["offline", "online", "unavailable"]

        * Matrix Spec
        9.4.1   GET /_matrix/client/r0/sync
        params = {
            "filter": "66696p746572",
            "since": "s72594_4483_1934",
            "full_state": "false",
            "set_presence": "offline",
            "timeout": "30000"
        }

        Rate-limited:   No.
        Requires auth:  Yes.
        """
        return await self.client(
            "sync",
            "GET",
            params=dict(
                filter(
                    lambda x: x[1],
                    {
                        "filter": json.dumps(
                            data_filter, separators=(",", ":")
                        )
                        if isinstance(data_filter, dict)
                        else data_filter,
                        "since": since,
                        "full_state": full_state,
                        "set_presence": set_presence,
                        "timeout": timeout,
                    }.items(),
                )
            ),
        )

    def room_send(
        self,
        room_id: str,
        event_type: str,
        body: Dict[Any, Any],
        tx_id: Union[str, UUID],
    ) -> httpx.Response:
        """Send a message event to a room.
        Args:
            room_id (str): The room id of the room where the event will be sent
                to.
            event_type (str): The type of the message that will be sent.
            body(Dict): The body of the event. The fields in this
                object will vary depending on the type of event.
            tx_id (str): The transaction ID for this event.

        * Matrix Spec
        9.6.2   PUT /_matrix/client/r0/rooms/{roomId}/send/{eventType}/{txnId}
        Content-Type: application/json
        body = {
            "msgtype": "m.text",
            "body": "hello"
        }

        Rate-limited:   No.
        Requires auth:  Yes.
        """
        return httpx.Response(status_code=200, json={})

    async def room_get_event(
        self, room_id: str, event_id: str
    ) -> httpx.Response:
        """Get a single event based on roomId/eventId.
        Args:
            room_id (str): The room id of the room where the event is in.
            event_id (str): The event id to get.

        * Matrix Spec

        """
        return httpx.Response(status_code=200, json={})

    async def room_put_state(
        self,
        room_id: str,
        event_type: str,
        body: Dict[Any, Any],
        state_key: str = "",
    ) -> httpx.Response:
        """Send a state event.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            room_id (str): The room id of the room where the event will be sent
                to.
            event_type (str): The type of the event that will be sent.
            body(Dict): The body of the event. The fields in this
                object will vary depending on the type of event.
            state_key: The key of the state to look up. Defaults to an empty
                string.

        * Matrix Spec
        9.6.1   PUT /_matrix/client/r0/rooms/{roomId}/state/{eventType}/{stateKey}
        Content-Type: application/json
        body = {
            "membership": "join",
            "avatar_url": "mxc://localhost/SEsfnsuifSDFSSEF",
            "displayname": "Alice Margatroid"
        }

        Rate-limited:   No.
        Requires auth:  Yes.
        """
        return httpx.Response(status_code=200, json={})

    async def room_get_state_event(
        self,
        room_id: str,
        event_event_type: str,
        state_key: str = "",
    ) -> httpx.Response:
        """Fetch a state event."""
        return httpx.Response(status_code=200, json={})

    async def room_get_state(self, room_id: str) -> httpx.Response:
        """Fetch the current state for a room."""
        return httpx.Response(status_code=200, json={})

    def room_redact(
        self,
        room_id: str,
        event_id: str,
        tx_id: Union[str, UUID],
        reason: Optional[str] = None,
    ) -> httpx.Response:
        """Strip information out of an event."""
        return httpx.Response(status_code=200, json={})

    async def room_kick(
        self, room_id: str, user_id: str, reason: Optional[str] = None
    ) -> httpx.Response:
        """Kick a user from a room, or withdraw their invitation."""
        return httpx.Response(status_code=200, json={})

    async def room_ban(
        self,
        room_id: str,
        user_id: str,
        reason: Optional[str] = None,
    ) -> httpx.Response:
        """Ban a user from a room."""
        return httpx.Response(status_code=200, json={})

    async def room_unban(
        self,
        room_id: str,
        user_id: str,
    ) -> httpx.Response:
        """Unban a user from a room."""
        return httpx.Response(status_code=200, json={})

    async def room_invite(self, room_id: str, user_id: str) -> httpx.Response:
        """Invite a user to a room."""
        return httpx.Response(status_code=200, json={})

    async def room_create(
        self,
        visibility: RoomVisibility = RoomVisibility.private,
        alias: Optional[str] = None,
        name: Optional[str] = None,
        topic: Optional[str] = None,
        room_version: Optional[str] = None,
        federate: bool = True,
        is_direct: bool = False,
        preset: Optional[RoomPreset] = None,
        invite: Sequence[str] = (),
        initial_state: Sequence[Dict[str, Any]] = (),
        power_level_override: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Create a new room."""
        return httpx.Response(status_code=200, json={})

    async def join(self, room_id: str) -> httpx.Response:
        """Join a room.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            room_id (str): The room identifier or alias to join.
        """
        return httpx.Response(status_code=200, json={})

    async def room_leave(self, room_id: str) -> httpx.Response:
        """Leave a room.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            room_id (str): The room id of the room that will be left.
        """
        return httpx.Response(status_code=200, json={})

    async def room_forget(self, room_id: str) -> httpx.Response:
        """Forget a room.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            room_id (str): The room id of the room that will be forgotten.
        """
        return httpx.Response(status_code=200, json={})

    async def room_messages(
        self,
        room_id: str,
        start: str,
        end: Optional[str] = None,
        direction: MessageDirection = MessageDirection.back,
        limit: int = 10,
        message_filter: Optional[Dict[Any, Any]] = None,
    ) -> httpx.Response:
        """Get room messages.
        Returns the HTTP method and HTTP path for the request.
        Args:
            access_token (str): The access token to be used with the request.
            room_id (str): room id of the room for which to download the
                messages
            start (str): The token to start returning events from.
            end (str): The token to stop returning events at.
            direction (MessageDirection): The direction to return events from.
            limit (int): The maximum number of events to return.
            message_filter (Optional[Dict[Any, Any]]):
                A filter dict that should be used for this room messages
                request.
        """
        return httpx.Response(status_code=200, json={})

    async def keys_upload(self, key_dict: Dict[str, Any]) -> httpx.Response:
        """Publish end-to-end encryption keys.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            key_dict (Dict): The dictionary containing device and one-time
                keys that will be published to the server.
        """
        return httpx.Response(status_code=200, json={})

    async def keys_query(
        self, user_set: Iterable[str], token: Optional[str] = None
    ) -> httpx.Response:
        """Query the current devices and identity keys for the given users.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            user_set (Set[str]): The users for which the keys should be
                downloaded.
            token (Optional[str]): If the client is fetching keys as a result
                of a device update received in a sync request, this should be
                the 'since' token of that sync request, or any later sync
                token.
        """
        return httpx.Response(status_code=200, json={})

    async def keys_claim(self, user_set: Dict[str, Iterable[str]]):
        """Claim one-time keys for use in Olm pre-key messages.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            user_set (Dict[str, List[str]]): The users and devices for which to
                claim one-time keys to be claimed. A map from user ID, to a
                list of device IDs.
        """
        return httpx.Response(status_code=200, json={})

    async def to_device(
        self,
        event_type: str,
        content: Dict[Any, Any],
        tx_id: Union[str, UUID],
    ) -> httpx.Response:
        """Send to-device events to a set of client devices.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            event_type (str): The type of the event which will be sent.
            content (Dict): The messages to send. A map from user ID, to a map
                from device ID to message body. The device ID may also be *,
                meaning all known devices for the user.
            tx_id (str): The transaction ID for this event.
        """
        return httpx.Response(status_code=200, json={})

    async def devices(self) -> httpx.Response:
        """Get the list of devices for the current user.
        Returns the HTTP method and HTTP path for the request.
        Args:
            access_token (str): The access token to be used with the request.
        """
        return httpx.Response(status_code=200, json={})

    async def update_device(
        self, device_id: str, content: Dict[str, str]
    ) -> httpx.Response:
        """Update the metadata of the given device.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            device_id (str): The device for which the metadata will be updated.
            content (Dict): A dictionary of metadata values that will be
                updated for the device.
        """
        return httpx.Response(status_code=200, json={})

    async def delete_devices(
        self,
        devices: List[str],
        auth_dict: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Delete a device.
        This API endpoint uses the User-Interactive Authentication API.
        This tells the server to delete the given devices and invalidate their
        associated access tokens.
        Should first be called with no additional authentication information.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            devices (List[str]): A list of devices which will be deleted.
            auth_dict (Dict): Additional authentication information for
                the user-interactive authentication API.
        """
        return httpx.Response(status_code=200, json={})

    async def joined_members(self, room_id: str) -> httpx.Response:
        """Get the list of joined members for a room.
        Returns the HTTP method and HTTP path for the request.
        Args:
            access_token (str): The access token to be used with the request.
            room_id (str): Room id of the room where the user is typing.
        """
        return httpx.Response(status_code=200, json={})

    async def joined_rooms(self) -> httpx.Response:
        """Get the list of joined rooms for the logged in account.
        Returns the HTTP method and HTTP path for the request.
        Args:
            access_token (str): The access token to be used with the request.
        """
        return httpx.Response(status_code=200, json={})

    async def room_resolve_alias(self, room_alias: str) -> httpx.Response:
        """Resolve a room alias to a room ID.
        Returns the HTTP method and HTTP path for the request.
        Args:
            room_alias (str): The alias to resolve
        """
        return httpx.Response(status_code=200, json={})

    async def room_typing(
        self,
        room_id: str,
        user_id: str,
        typing_state: bool = True,
        timeout: int = 30000,
    ) -> httpx.Response:
        """Send a typing notice to the server.
        This tells the server that the user is typing for the next N
        milliseconds or that the user has stopped typing.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            room_id (str): Room id of the room where the user is typing.
            user_id (str): The user who has started to type.
            typing_state (bool): A flag representing whether the user started
                or stopped typing
            timeout (int): For how long should the new typing notice be
                valid for in milliseconds.
        """
        return httpx.Response(status_code=200, json={})

    async def update_receipt_marker(
        self,
        room_id: str,
        event_id: str,
        receipt_type: str = "m.read",
    ) -> httpx.Response:
        """Update the marker of given `receipt_type` to specified `event_id`.
        Returns the HTTP method and HTTP path for the request.
        Args:
            access_token (str): The access token to be used with the request.
            room_id (str): Room id of the room where the marker should
                be updated
            event_id (str): The event ID the read marker should be located at
            receipt_type (str): The type of receipt to send. Currently, only
                `m.read` is supported by the Matrix specification.
        """
        return httpx.Response(status_code=200, json={})

    async def room_read_markers(
        self,
        room_id: str,
        fully_read_event: str,
        read_event: Optional[str] = None,
    ) -> httpx.Response:
        """Update fully read marker and optionally read marker for a room.
        This sets the position of the read marker for a given room,
        and optionally the read receipt's location.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            room_id (str): Room id of the room where the read
                markers should be updated
            fully_read_event (str): The event ID the read marker should be
                located at.
            read_event (Optional[str]): The event ID to set the read receipt
                location at.
        """
        return httpx.Response(status_code=200, json={})

    async def content_repository_config(self) -> httpx.Response:
        """Get the content repository configuration, such as upload limits.
        Returns the HTTP method and HTTP path for the request.
        Args:
            access_token (str): The access token to be used with the request.
        """
        return httpx.Response(status_code=200, json={})

    async def upload(
        self,
        filename: Optional[str] = None,
    ) -> httpx.Response:
        """Upload a file's content to the content repository.
        Returns the HTTP method, HTTP path and empty data for the request.
        The real data should be read from the file that should be uploaded.
        Note: This requests also requires the Content-Type http header to be
        set.
        Args:
            access_token (str): The access token to be used with the request.
            filename (str): The name of the file being uploaded
        """
        return httpx.Response(status_code=200, json={})

    async def download(
        self,
        server_name: str,
        media_id: str,
        filename: Optional[str] = None,
        allow_remote: bool = True,
    ) -> httpx.Response:
        """Get the content of a file from the content repository.
        Returns the HTTP method and HTTP path for the request.
        Args:
            server_name (str): The server name from the mxc:// URI.
            media_id (str): The media ID from the mxc:// URI.
            filename (str, optional): A filename to be returned in the response
                by the server. If None (default), the original name of the
                file will be returned instead, if there is one.
            allow_remote (bool): Indicates to the server that it should not
                attempt to fetch the media if it is deemed remote.
                This is to prevent routing loops where the server contacts
                itself.
        """
        return httpx.Response(status_code=200, json={})

    async def thumbnail(
        self,
        server_name: str,
        media_id: str,
        width: int,
        height: int,
        method: ResizingMethod = ResizingMethod.scale,
        allow_remote: bool = True,
    ) -> httpx.Response:
        """Get the thumbnail of a file from the content repository.
        Returns the HTTP method and HTTP path for the request.
        Note: The actual thumbnail may be larger than the size specified.
        Args:
            server_name (str): The server name from the mxc:// URI.
            media_id (str): The media ID from the mxc:// URI.
            width (int): The desired width of the thumbnail.
            height (int): The desired height of the thumbnail.
            method (ResizingMethod): The desired resizing method.
            allow_remote (bool): Indicates to the server that it should not
                attempt to fetch the media if it is deemed remote.
                This is to prevent routing loops where the server contacts
                itself.
        """
        return httpx.Response(status_code=200, json={})

    async def profile_get(self, user_id: str) -> httpx.Response:
        """Get the combined profile information for a user.
        Returns the HTTP method and HTTP path for the request.
        Args:
            user_id (str): User id to get the profile for.
            access_token (str): The access token to be used with the request. If
                                omitted, an unauthenticated request is perfomed.
        """
        return httpx.Response(status_code=200, json={})

    async def profile_get_displayname(self, user_id: str) -> httpx.Response:
        # type (str, str) -> Tuple[str, str]
        """Get display name.
        Returns the HTTP method and HTTP path for the request.
        Args:
            user_id (str): User id to get display name for.
            access_token (str): The access token to be used with the request. If
                                omitted, an unauthenticated request is perfomed.
        """
        return httpx.Response(status_code=200, json={})

    async def profile_set_displayname(
        self, user_id: str, display_name: str
    ) -> httpx.Response:
        """Set display name.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            user_id (str): User id to set display name for.
            display_name (str): Display name for user to set.
        """
        return httpx.Response(status_code=200, json={})

    async def profile_get_avatar(self, user_id: str) -> httpx.Response:
        """Get avatar URL.
        Returns the HTTP method and HTTP path for the request.
        Args:
            user_id (str): User id to get avatar for.
            access_token (str): The access token to be used with the request. If
                                omitted, an unauthenticated request is perfomed.
        """
        return httpx.Response(status_code=200, json={})

    async def profile_set_avatar(
        self, user_id: str, avatar_url: str
    ) -> httpx.Response:
        # type (str, str, str) -> Tuple[str, str, str]
        """Set avatar url.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            user_id (str): User id to set display name for.
            avatar_url (str): matrix content URI of the avatar to set.
        """
        return httpx.Response(status_code=200, json={})

    async def get_presence(self: str, user_id: str) -> httpx.Response:
        """Get the given user's presence state.
        Returns the HTTP method and HTTP path for the request.
        Args:
            access_token (str): The access token to be used with the request.
            user_id (str): User id whose presence state to get.
        """
        return httpx.Response(status_code=200, json={})

    async def set_presence(
        self, user_id: str, presence: str, status_msg: str = None
    ) -> httpx.Response:
        """This API sets the given user's presence state.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            user_id (str): User id whose presence state to get.
            presence (str): The new presence state.
            status_msg (str, optional): The status message to attach to this state.
        """
        return httpx.Response(status_code=200, json={})

    async def whoami(self) -> httpx.Response:
        """Get information about the owner of a given access token.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
        """
        return httpx.Response(status_code=200, json={})

    async def room_context(
        self, room_id: str, event_id: str, limit: Optional[str] = None
    ) -> httpx.Response:
        """Fetch a number of events that happened before and after an event.
        This allows clients to get the context surrounding an event.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            room_id (str): The room_id of the room that contains the event and
                its context.
            event_id (str): The event_id of the event that we wish to get the
                context for.
            limit(int, optional): The maximum number of events to request.
        """
        return httpx.Response(status_code=200, json={})

    async def upload_filter(
        self,
        user_id: str,
        event_fields: Optional[List[str]] = None,
        event_format: EventFormat = EventFormat.client,
        presence: Optional[Dict[str, Any]] = None,
        account_data: Optional[Dict[str, Any]] = None,
        room: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Upload a new filter definition to the homeserver.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            access_token (str): The access token to be used with the request.
            user_id (str):  ID of the user uploading the filter.
            event_fields (Optional[List[str]]): List of event fields to
                include. If this list is absent then all fields are included.
                The entries may include '.' characters to indicate sub-fields.
                A literal '.' character in a field name may be escaped
                using a '\'.
            event_format (EventFormat): The format to use for events.
            presence (Dict[str, Any]): The presence updates to include.
                The dict corresponds to the `EventFilter` type described
                in https://matrix.org/docs/spec/client_server/latest#id240
            account_data (Dict[str, Any]): The user account data that isn't
                associated with rooms to include.
                The dict corresponds to the `EventFilter` type described
                in https://matrix.org/docs/spec/client_server/latest#id240
            room (Dict[str, Any]): Filters to be applied to room data.
                The dict corresponds to the `RoomFilter` type described
                in https://matrix.org/docs/spec/client_server/latest#id240
        """
        return httpx.Response(status_code=200, json={})

    # async def set_pushrule(
    #     self,
    #     scope: str,
    #     kind: PushRuleKind,
    #     rule_id: str,
    #     before: Optional[str] = None,
    #     after: Optional[str] = None,
    #     actions: Sequence["PushAction"] = (),
    #     conditions: Optional[Sequence["PushCondition"]] = None,
    #     pattern: Optional[str] = None,
    # ) -> httpx.Response:
    #     """Create or modify an existing user-created push rule.
    #     Returns the HTTP method, HTTP path and data for the request.
    #     Args:
    #         access_token (str): The access token to be used with the request.
    #         scope (str): The scope of this rule, e.g. ``"global"``.
    #             Homeservers currently only process ``global`` rules for
    #             event matching, while ``device`` rules are a planned feature.
    #             It is up to clients to interpret any other scope name.
    #         kind (PushRuleKind): The kind of rule.
    #         rule_id (str): The identifier of the rule. Must be unique
    #             within its scope and kind.
    #             For rules of ``room`` kind, this is the room ID to match for.
    #             For rules of ``sender`` kind, this is the user ID to match.
    #         before (Optional[str]): Position this rule before the one matching
    #             the given rule ID.
    #             The rule ID cannot belong to a predefined server rule.
    #             ``before`` and ``after`` cannot be both specified.
    #         after (Optional[str]): Position this rule after the one matching
    #             the given rule ID.
    #             The rule ID cannot belong to a predefined server rule.
    #             ``before`` and ``after`` cannot be both specified.
    #         actions (Sequence[PushAction]): Actions to perform when the
    #             conditions for this rule are met. The given actions replace
    #             the existing ones.
    #         conditions (Sequence[PushCondition]): Event conditions that must
    #             hold true for the rule to apply to that event.
    #             A rule with no conditions always hold true.
    #             Only applicable to ``underride`` and ``override`` rules.
    #         pattern (Optional[str]): Glob-style pattern to match against
    #             for the event's content.
    #             Only applicable to ``content`` rules.
    #     """
    #     return httpx.Response(status_code=200, json={})

    # async def delete_pushrule(
    #     self,
    #     scope: str,
    #     kind: PushRuleKind,
    #     rule_id: str,
    # ) -> httpx.Response:
    #     """Delete an existing user-created push rule.
    #     Returns the HTTP method and HTTP path for the request.
    #     Args:
    #         access_token (str): The access token to be used with the request.
    #         scope (str): The scope of this rule, e.g. ``"global"``.
    #         kind (PushRuleKind): The kind of rule.
    #         rule_id (str): The identifier of the rule. Must be unique
    #             within its scope and kind.
    #     """
    #     return httpx.Response(status_code=200, json={})

    # async def enable_pushrule(
    #     self,
    #     scope: str,
    #     kind: PushRuleKind,
    #     rule_id: str,
    #     enable: bool,
    # ) -> httpx.Response:
    #     """Enable or disable an existing built-in or user-created push rule.
    #     Returns the HTTP method, HTTP path and data for the request.
    #     Args:
    #         access_token (str): The access token to be used with the request.
    #         scope (str): The scope of this rule, e.g. ``"global"``.
    #         kind (PushRuleKind): The kind of rule.
    #         rule_id (str): The identifier of the rule. Must be unique
    #             within its scope and kind.
    #         enable (bool): Whether to enable or disable the rule.
    #     """
    #     return httpx.Response(status_code=200, json={})

    # async def set_pushrule_actions(
    #     self,
    #     scope: str,
    #     kind: PushRuleKind,
    #     rule_id: str,
    #     actions: Sequence["PushAction"],
    # ) -> httpx.Response:
    #     """Set the actions for an existing built-in or user-created push rule.
    #     Unlike ``set_pushrule``, this method can edit built-in server rules.
    #     Returns the HTTP method, HTTP path and data for the request.
    #     Args:
    #         access_token (str): The access token to be used with the request.
    #         scope (str): The scope of this rule, e.g. ``"global"``.
    #         kind (PushRuleKind): The kind of rule.
    #         rule_id (str): The identifier of the rule. Must be unique
    #             within its scope and kind.
    #         actions (Sequence[PushAction]): Actions to perform when the
    #             conditions for this rule are met. The given actions replace
    #             the existing ones.
    #     """
    #     return httpx.Response(status_code=200, json={})
