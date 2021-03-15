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
    MatrixResponse,
    MessageDirection,
    Presence,
    PushRuleKind,
    ResizingMethod,
    RoomPreset,
    RoomVisibility,
    UserKind,
)
from .tools import auth_required, jsonable_encoder


class BaseMatrixClient:
    def __init__(
        self, homeserver: str, access_token: str = None, version: str = "r0"
    ):
        self.version = version
        self.homeserver = homeserver
        self.access_token = access_token

    async def client(
        self,
        verb: HttpVerbs,
        path: str,
        *,
        access_token: str = None,
        params: QueryParamTypes = None,
        headers: HeaderTypes = None,
        cookies: CookieTypes = None,
        content: RequestContent = None,
        data: RequestData = None,
        files: RequestFiles = None,
        json: Any = None,
        stream: ByteStream = None,
    ) -> MatrixResponse:
        """DOC:"""
        if access_token is not None:
            if isinstance(params, dict):
                params.setdefault("access_token", access_token)
            else:
                params = dict(access_token=access_token)
        async with httpx.AsyncClient() as client:
            client_config = {
                "params": params,
                "headers": headers,
                "cookies": cookies,
                "content": content,
                "data": data,
                "files": files,
                "json": jsonable_encoder(json)
                if isinstance(json, (dict, list))
                else json,
                "stream": stream,
            }
            request = httpx.Request(
                verb.upper(),
                f"{self.client_path.strip('/')}/{path.lstrip('/')}",
                **dict(filter(lambda x: x[1], client_config.items())),
            )
            response: httpx.Response = await client.send(request)
        return MatrixResponse(response)

    @auth_required
    async def auth_client(self, *args, **kwargs):
        return await self.client(*args, **kwargs)

    @property
    def client_path(self):
        return f"{self.homeserver.strip('/')}/_matrix/client/{self.version}/"

    async def __call__(self, *args, **kwargs) -> MatrixResponse:
        return await self.client(*args, **kwargs)


class MatrixClient(BaseMatrixClient):
    async def login_info(self) -> MatrixResponse:
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
    ) -> MatrixResponse:
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
        if response.ok:
            self.access_token = response.json()["access_token"]
        return response

    async def register(
        self,
        user: str,
        password: str = None,
        kind: UserKind = "user",
        device_name: Optional[str] = "",
        device_id: Optional[str] = "",
    ) -> MatrixResponse:
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
        if response.ok:
            self.access_token = response.json()["access_token"]
        return response

    async def logout(self, all_devices: bool = True) -> MatrixResponse:
        """Logout the session.
        Args:
            all_devices (bool): Logout all sessions from all devices if set to True.

        * Matrix Spec
        5.5.3   POST /_matrix/client/r0/logout
        5.5.4   POST /_matrix/client/r0/logout/all
        Content-Type: application/json
        body = {}
        """
        return await self.auth_client(
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
    ) -> MatrixResponse:
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
        return await self.auth_client(
            "GET",
            "sync",
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

    async def room_send(
        self,
        room_id: str,
        event_type: str,
        body: Dict[Any, Any],
        tx_id: Union[str, UUID],
    ) -> MatrixResponse:
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
        return await self.auth_client(
            "PUT",
            f"rooms/{room_id}/send/{event_type}/{tx_id}",
            json=body,
        )

    async def room_get_event(
        self, room_id: str, event_id: str
    ) -> MatrixResponse:
        """Get a single event based on roomId/eventId.
        Args:
            room_id (str): The room id of the room where the event is in.
            event_id (str): The event id to get.

        * Matrix Spec
        9.5.1   GET /_matrix/client/r0/rooms/{roomId}/event/{eventId}
        params = {
            "roomId": roomId,
            "eventId": eventId
        }

        Rate-limited:   No.
        Requires auth:  Yes.
        """
        return await self.auth_client(
            "GET",
            "rooms/{room_id}/event/{event_id}",
            params={
                "room_id": room_id,
                "event_id": event_id,
            },
        )

    async def room_put_state(
        self,
        room_id: str,
        event_type: str,
        body: Dict[Any, Any],
        state_key: str = "",
    ) -> MatrixResponse:
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
        return await self.auth_client(
            "PUT",
            f"rooms/{room_id}/state/{event_type}/{state_key}",
            json=body,
        )

    async def room_get_state_event(
        self,
        room_id: str,
        event_type: str,
        state_key: str = "",
    ) -> MatrixResponse:
        """Fetch a state event.
        Returns the HTTP method and HTTP path for the request.
        Args:
            room_id (str): The room id of the room where the state is fetched
                from.
            event_type (str): The type of the event that will be fetched.
            state_key: The key of the state to look up. Defaults to an empty
                string.

        * Matrix Spec
        GET /_matrix/client/r0/rooms/{roomId}/state/{eventType}/{stateKey}

        params = {
            "room_id": room_id,
            "event_type": event_type,
            "state_key": state_key
        }

        Rate-limited:   No.
        Requires auth:  Yes.
        """
        return await self.auth_client(
            "GET",
            f"rooms/{room_id}/state/{event_type}/{state_key}",
            params={
                "room_id": room_id,
                "event_type": event_type,
                "state_key": state_key,
            },
        )

    async def room_get_state(self, room_id: str) -> MatrixResponse:
        """Fetch the current state for a room.
        Returns the HTTP method and HTTP path for the request.
        Args:
            room_id (str): The room id of the room where the state is fetched
                from.

        * Matrix Spec
        GET /_matrix/client/r0/rooms/{roomId}/state

        params = {
            "room_id": room_id
        }

        Rate-limited:   No.
        Requires auth:  Yes.
        """
        return await self.auth_client(
            "GET",
            f"rooms/{room_id}/state",
            params={"room_id": room_id},
        )

    async def room_redact(
        self,
        room_id: str,
        event_id: str,
        tx_id: Union[str, UUID],
        reason: Optional[str] = None,
    ) -> MatrixResponse:
        """Strip information out of an event.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            room_id (str): The room id of the room that contains the event that
                will be redacted.
            event_id (str): The ID of the event that will be redacted.
            tx_id (str/UUID, optional): A transaction ID for this event.
            reason(str, optional): A description explaining why the
                event was redacted.

        * Matrix Spec
        PUT /_matrix/client/r0/rooms/{roomId}/redact/{eventId}/{txnId}
        Content-Type: application/json

        {
            "reason": "Indecent material"
        }

        Rate-limited:   No.
        Requires auth:  Yes.
        """
        return await self.auth_client(
            "POST",
            f"rooms/{room_id}/redact/{event_id}/{str(tx_id)}",
            json=dict(
                filter(
                    lambda x: x[1],
                    {"reason": reason}.items(),
                )
            ),
        )

    async def room_kick(
        self, room_id: str, user_id: str, reason: Optional[str] = None
    ) -> MatrixResponse:
        """Kick a user from a room, or withdraw their invitation.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            room_id (str): The room id of the room that the user will be
                kicked from.
            user_id (str): The user_id of the user that should be kicked.
            reason (str, optional): A reason for which the user is kicked.

        * Matrix Spec
        """
        return await self.auth_client(
            "POST",
            f"rooms{room_id}/kick",
            json=dict(
                filter(
                    lambda x: x[1],
                    {"user_id": user_id, "reason": reason}.items(),
                )
            ),
        )

    async def room_ban(
        self,
        room_id: str,
        user_id: str,
        reason: Optional[str] = None,
    ) -> MatrixResponse:
        """Ban a user from a room.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            room_id (str): The room id of the room that the user will be
                banned from.
            user_id (str): The user_id of the user that should be banned.
            reason (str, optional): A reason for which the user is banned.

        * Matrix Spec
        """
        return await self.auth_client(
            "POST",
            f"rooms{room_id}/ban",
            json=dict(
                filter(
                    lambda x: x[1],
                    {"user_id": user_id, "reason": reason}.items(),
                )
            ),
        )

    async def room_unban(
        self,
        room_id: str,
        user_id: str,
    ) -> MatrixResponse:
        """Unban a user from a room.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            room_id (str): The room id of the room that the user will be
                unbanned from.
            user_id (str): The user_id of the user that should be unbanned.

        * Matrix Spec
        """
        return await self.auth_client(
            "POST",
            f"rooms{room_id}/unban",
            json=dict(
                filter(
                    lambda x: x[1],
                    {"user_id": user_id}.items(),
                )
            ),
        )

    async def room_invite(self, room_id: str, user_id: str) -> MatrixResponse:
        """Invite a user to a room.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            room_id (str): The room id of the room that the user will be
                invited to.
            user_id (str): The user id of the user that should be invited.

        * Matrix Spec
        """
        return await self.auth_client(
            "POST",
            f"rooms{room_id}/invite",
            json=dict(
                filter(
                    lambda x: x[1],
                    {"user_id": user_id}.items(),
                )
            ),
        )

    async def room_create(
        self,
        visibility: RoomVisibility = RoomVisibility.private,
        room_alias_name: Optional[str] = None,
        name: Optional[str] = None,
        topic: Optional[str] = None,
        room_version: Optional[str] = None,
        federate: bool = True,
        is_direct: bool = False,
        preset: Optional[RoomPreset] = None,
        invite: Sequence[str] = (),
        initial_state: Sequence[Dict[str, Any]] = (),
        power_level_override: Optional[Dict[str, Any]] = None,
    ) -> MatrixResponse:
        """Create a new room.
        Args:
            visibility (RoomVisibility): whether to have the room published in
                the server's room directory or not.
                Defaults to ``RoomVisibility.private``.
            room_alias_name (str, optional): The desired canonical alias local part.
                For example, if set to "foo" and the room is created on the
                "example.com" server, the room alias will be
                "#foo:example.com".
            name (str, optional): A name to set for the room.
            topic (str, optional): A topic to set for the room.
            room_version (str, optional): The room version to set.
                If not specified, the homeserver will use its default setting.
                If a version not supported by the homeserver is specified,
                a 400 ``M_UNSUPPORTED_ROOM_VERSION`` error will be returned.
            federate (bool): Whether to allow users from other homeservers from
                joining the room. Defaults to ``True``.
                Cannot be changed later.
            is_direct (bool): If this should be considered a
                direct messaging room.
                If ``True``, the server will set the ``is_direct`` flag on
                ``m.room.member events`` sent to the users in ``invite``.
                Defaults to ``False``.
            preset (RoomPreset, optional): The selected preset will set various
                rules for the room.
                If unspecified, the server will choose a preset from the
                ``visibility``: ``RoomVisibility.public`` equates to
                ``RoomPreset.public_chat``, and
                ``RoomVisibility.private`` equates to a
                ``RoomPreset.private_chat``.
            invite (list): A list of user id to invite to the room.
            initial_state (list): A list of state event dicts to send when
                the room is created.
                For example, a room could be made encrypted immediatly by
                having a ``m.room.encryption`` event dict.
            power_level_override (dict): A ``m.room.power_levels content`` dict
                to override the default.
                The dict will be applied on top of the generated
                ``m.room.power_levels`` event before it is sent to the room.

        * Matrix Spec

        POST    /_matrix/client/r0/createRoom
        Content-Type:   application/json

        {
            "preset": "public_chat",
            "room_alias_name": "thepub",
            "name": "The Grand Duke Pub",
            "topic": "All about happy hour",
            "creation_content": {
                "m.federate": false
            }
        }

        Rate-limited:   No.
        Requires auth:  Yes.
        """

        return await self.auth_client(
            "POST",
            "createRoom",
            json=dict(
                filter(
                    lambda x: x[1],
                    {
                        "visibility": visibility,
                        "room_alias_name": room_alias_name,
                        "name": name,
                        "topic": topic,
                        "room_version": room_version,
                        "is_direct": is_direct,
                        "preset": preset,
                        "invite": invite,
                        "initial_state": initial_state,
                        "power_level_content_override": power_level_override,
                        "creation_content": {"m.federate": federate},
                    }.items(),
                )
            ),
        )

    async def join(self, room_id: str) -> MatrixResponse:
        """Join a room.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            room_id (str): The room identifier or alias to join.

        * Matrix Spec
        POST /_matrix/client/r0/join/{roomIdOrAlias}
        Content-Type: application/json
        {}

        Rate-limited:   Yes.
        Requires auth:  Yes.
        """
        return await self.auth_client("POST", f"join/{room_id}", json={})

    async def room_leave(self, room_id: str) -> MatrixResponse:
        """Leave a room.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            room_id (str): The room id of the room that will be left.

        * Matrix Spec
        POST /_matrix/client/r0/rooms/{roomId}/leave

        Rate-limited:   Yes.
        Requires auth:  Yes.
        """
        return await self.auth_client("POST", f"rooms/{room_id}/leave")

    async def room_forget(self, room_id: str) -> MatrixResponse:
        """Forget a room.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            room_id (str): The room id of the room that will be forgotten.

        * Matrix Spec
        POST /_matrix/client/r0/rooms/{roomId}/forget

        Rate-limited:   Yes.
        Requires auth:  Yes.
        """
        return await self.auth_client("POST", f"rooms/{room_id}/forget")

    async def room_messages(
        self,
        room_id: str,
        start: str,
        end: Optional[str] = None,
        direction: MessageDirection = MessageDirection.back,
        limit: int = 10,
        message_filter: Optional[Dict[Any, Any]] = None,
    ) -> MatrixResponse:
        """Get room messages.
        Returns the HTTP method and HTTP path for the request.
        Args:
            room_id (str): room id of the room for which to download the
                messages
            start (str): The token to start returning events from.
            end (str): The token to stop returning events at.
            direction (MessageDirection): The direction to return events from.
            limit (int): The maximum number of events to return.
            message_filter (Optional[Dict[Any, Any]]):
                A filter dict that should be used for this room messages
                request.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def keys_upload(self, key_dict: Dict[str, Any]) -> MatrixResponse:
        """Publish end-to-end encryption keys.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            key_dict (Dict): The dictionary containing device and one-time
                keys that will be published to the server.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def keys_query(
        self, user_set: Iterable[str], token: Optional[str] = None
    ) -> MatrixResponse:
        """Query the current devices and identity keys for the given users.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            user_set (Set[str]): The users for which the keys should be
                downloaded.
            token (Optional[str]): If the client is fetching keys as a result
                of a device update received in a sync request, this should be
                the 'since' token of that sync request, or any later sync
                token.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def keys_claim(self, user_set: Dict[str, Iterable[str]]):
        """Claim one-time keys for use in Olm pre-key messages.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            user_set (Dict[str, List[str]]): The users and devices for which to
                claim one-time keys to be claimed. A map from user ID, to a
                list of device IDs.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def to_device(
        self,
        event_type: str,
        content: Dict[Any, Any],
        tx_id: Union[str, UUID],
    ) -> MatrixResponse:
        """Send to-device events to a set of client devices.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            event_type (str): The type of the event which will be sent.
            content (Dict): The messages to send. A map from user ID, to a map
                from device ID to message body. The device ID may also be *,
                meaning all known devices for the user.
            tx_id (str): The transaction ID for this event.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def devices(self) -> MatrixResponse:
        """Get the list of devices for the current user.
        Returns the HTTP method and HTTP path for the request.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def update_device(
        self, device_id: str, display_name: str = None
    ) -> MatrixResponse:
        """Update the metadata of the given device.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            device_id (str): The device for which the metadata will be updated.
            display_name (str): The new display name for this device. If not given, the display name is unchanged.

        * Matrix Spec
        PUT /_matrix/client/r0/devices/{deviceId} HTTP/1.1
        Content-Type: application/json

        {
            "display_name": "My other phone"
        }

        Rate-limited: No.
        Requires auth: Yes.
        """
        return await self.auth_client(
            "PUT",
            f"devices/{device_id}",
            json={"display_name": display_name},
        )

    async def delete_devices(
        self,
        devices: List[str],
        auth_dict: Optional[Dict[str, str]] = None,
    ) -> MatrixResponse:
        """Delete a device.
        This API endpoint uses the User-Interactive Authentication API.
        This tells the server to delete the given devices and invalidate their
        associated access tokens.
        Should first be called with no additional authentication information.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            devices (List[str]): A list of devices which will be deleted.
            auth_dict (Dict): Additional authentication information for
                the user-interactive authentication API.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def joined_members(self, room_id: str) -> MatrixResponse:
        """Get the list of joined members for a room.
        Returns the HTTP method and HTTP path for the request.
        Args:
            room_id (str): Room id of the room where the user is typing.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def joined_rooms(self) -> MatrixResponse:
        """Get the list of joined rooms for the logged in account.
        Returns the HTTP method and HTTP path for the request.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def room_resolve_alias(self, room_alias: str) -> MatrixResponse:
        """Resolve a room alias to a room ID.
        Returns the HTTP method and HTTP path for the request.
        Args:
            room_alias (str): The alias to resolve

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def room_typing(
        self,
        room_id: str,
        user_id: str,
        typing_state: bool = True,
        timeout: int = 30000,
    ) -> MatrixResponse:
        """Send a typing notice to the server.
        This tells the server that the user is typing for the next N
        milliseconds or that the user has stopped typing.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            room_id (str): Room id of the room where the user is typing.
            user_id (str): The user who has started to type.
            typing_state (bool): A flag representing whether the user started
                or stopped typing
            timeout (int): For how long should the new typing notice be
                valid for in milliseconds.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def update_receipt_marker(
        self,
        room_id: str,
        event_id: str,
        receipt_type: str = "m.read",
    ) -> MatrixResponse:
        """Update the marker of given `receipt_type` to specified `event_id`.
        Returns the HTTP method and HTTP path for the request.
        Args:
            room_id (str): Room id of the room where the marker should
                be updated
            event_id (str): The event ID the read marker should be located at
            receipt_type (str): The type of receipt to send. Currently, only
                `m.read` is supported by the Matrix specification.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def room_read_markers(
        self,
        room_id: str,
        fully_read_event: str,
        read_event: Optional[str] = None,
    ) -> MatrixResponse:
        """Update fully read marker and optionally read marker for a room.
        This sets the position of the read marker for a given room,
        and optionally the read receipt's location.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            room_id (str): Room id of the room where the read
                markers should be updated
            fully_read_event (str): The event ID the read marker should be
                located at.
            read_event (Optional[str]): The event ID to set the read receipt
                location at.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def content_repository_config(self) -> MatrixResponse:
        """Get the content repository configuration, such as upload limits.
        Returns the HTTP method and HTTP path for the request.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def upload(
        self,
        filename: Optional[str] = None,
    ) -> MatrixResponse:
        """Upload a file's content to the content repository.
        Returns the HTTP method, HTTP path and empty data for the request.
        The real data should be read from the file that should be uploaded.
        Note: This requests also requires the Content-Type http header to be
        set.
            filename (str): The name of the file being uploaded

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def download(
        self,
        server_name: str,
        media_id: str,
        filename: Optional[str] = None,
        allow_remote: bool = True,
    ) -> MatrixResponse:
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

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def thumbnail(
        self,
        server_name: str,
        media_id: str,
        width: int,
        height: int,
        method: ResizingMethod = ResizingMethod.scale,
        allow_remote: bool = True,
    ) -> MatrixResponse:
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

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def profile_get(self, user_id: str) -> MatrixResponse:
        """Get the combined profile information for a user.
        Returns the HTTP method and HTTP path for the request.
        Args:
            user_id (str): User id to get the profile for.

        * Matrix Spec
        GET /_matrix/client/r0/profile/{userId} HTTP/1.1

        Rate-limited:   No.
        Requires auth:  No.
        """
        return await self.client("GET", f"profile/{user_id}")

    async def profile_get_displayname(self, user_id: str) -> MatrixResponse:
        """Get display name.
        Returns the HTTP method and HTTP path for the request.
        Args:
            user_id (str): User id to get display name for.

        * Matrix Spec
        11.2.2   GET /_matrix/client/r0/profile/{userId}/displayname

        Rate-limited:   No.
        Requires auth:  No.
        """
        return await self.client("GET", f"profile/{user_id}/displayname")

    async def profile_set_displayname(
        self, user_id: str, display_name: str
    ) -> MatrixResponse:
        """Set display name.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            user_id (str): User id to set display name for.
            display_name (str): Display name for user to set.

        * Matrix Spec
        11.2.1   PUT /_matrix/client/r0/profile/{userId}/displayname
        Content-Type: application/json

        {
        "displayname": "Alice Margatroid"
        }

        Rate-limited:   Yes.
        Requires auth:  Yes.
        """
        return await self.auth_client(
            "PUT",
            f"profile/{user_id}/displayname",
            json={"displayname": display_name},
        )

    async def profile_get_avatar(self, user_id: str) -> MatrixResponse:
        """Get avatar URL.
        Returns the HTTP method and HTTP path for the request.
        Args:
            user_id (str): User id to get avatar for.

        * Matrix Spec
        11.2.4   GET /_matrix/client/r0/profile/{userId}/avatar_url

        Rate-limited: No.
        Requires auth: No.
        """
        return await self.client("GET", f"profile/{user_id}/avatar_url")

    async def profile_set_avatar(
        self, user_id: str, avatar_url: str
    ) -> MatrixResponse:
        """Set avatar url.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            user_id (str): User id to set display name for.
            avatar_url (str): matrix content URI of the avatar to set.

        * Matrix Spec
        11.2.3   PUT /_matrix/client/r0/profile/{userId}/avatar_url

        Rate-limited: Yes.
        Requires auth: Yes.
        """
        return await self.auth_client(
            "PUT",
            f"profile/{user_id}/avatar_url",
            json={"avatar_url": avatar_url},
        )

    async def get_presence(self: str, user_id: str) -> MatrixResponse:
        """Get the given user's presence state.
        Returns the HTTP method and HTTP path for the request.
        Args:
            user_id (str): User id whose presence state to get.

        * Matrix Spec
        13.7.2.2   GET /_matrix/client/r0/presence/{userId}/status

        Rate-limited: No.
        Requires auth: Yes.
        """
        return await self.auth_client(
            "GET",
            f"presence/{user_id}/status",
        )

    async def set_presence(
        self,
        user_id: str,
        presence: Presence = Presence.offline,
        status_msg: str = None,
    ) -> MatrixResponse:
        """This API sets the given user's presence state.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            user_id (str): User id whose presence state to get.
            presence (str): The new presence state.
            status_msg (str, optional): The status message to attach to this state.

        * Matrix Spec
        13.7.2.1   PUT /_matrix/client/r0/presence/{userId}/status
        Content-Type: application/json

        Rate-limited: Yes.
        Requires auth: Yes.
        """

        return await self.auth_client(
            "PUT",
            f"presence/{user_id}/status",
            json=dict(
                filter(
                    lambda x: x[1],
                    {
                        "presence": presence,
                        "status_msg": status_msg,
                    }.items(),
                )
            ),
        )

    async def whoami(self) -> MatrixResponse:
        """Get information about the owner of a given access token.
        Returns the HTTP method, HTTP path and data for the request.

        * Matrix Spec
        5.8.1   GET /_matrix/client/r0/account/whoami

        Rate-limited: Yes.
        Requires auth: Yes.
        """
        return await self.auth_client("GET", "account/whoami")

    async def room_context(
        self, room_id: str, event_id: str, limit: Optional[str] = None
    ) -> MatrixResponse:
        """Fetch a number of events that happened before and after an event.
        This allows clients to get the context surrounding an event.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
            room_id (str): The room_id of the room that contains the event and
                its context.
            event_id (str): The event_id of the event that we wish to get the
                context for.
            limit(int, optional): The maximum number of events to request.

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

    async def upload_filter(
        self,
        user_id: str,
        event_fields: Optional[List[str]] = None,
        event_format: EventFormat = EventFormat.client,
        presence: Optional[Dict[str, Any]] = None,
        account_data: Optional[Dict[str, Any]] = None,
        room: Optional[Dict[str, Any]] = None,
    ) -> MatrixResponse:
        """Upload a new filter definition to the homeserver.
        Returns the HTTP method, HTTP path and data for the request.
        Args:
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

        * Matrix Spec
        """
        return MatrixResponse(httpx.Response(status_code=404, json={}))

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
    # ) -> MatrixResponse:
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
    #     return MatrixResponse(httpx.Response(status_code=404, json={}))

    # async def delete_pushrule(
    #     self,
    #     scope: str,
    #     kind: PushRuleKind,
    #     rule_id: str,
    # ) -> MatrixResponse:
    #     """Delete an existing user-created push rule.
    #     Returns the HTTP method and HTTP path for the request.
    #     Args:
    #         access_token (str): The access token to be used with the request.
    #         scope (str): The scope of this rule, e.g. ``"global"``.
    #         kind (PushRuleKind): The kind of rule.
    #         rule_id (str): The identifier of the rule. Must be unique
    #             within its scope and kind.
    #     """
    #     return MatrixResponse(httpx.Response(status_code=404, json={}))

    # async def enable_pushrule(
    #     self,
    #     scope: str,
    #     kind: PushRuleKind,
    #     rule_id: str,
    #     enable: bool,
    # ) -> MatrixResponse:
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
    #     return MatrixResponse(httpx.Response(status_code=404, json={}))

    # async def set_pushrule_actions(
    #     self,
    #     scope: str,
    #     kind: PushRuleKind,
    #     rule_id: str,
    #     actions: Sequence["PushAction"],
    # ) -> MatrixResponse:
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
    #     return MatrixResponse(httpx.Response(status_code=404, json={}))
