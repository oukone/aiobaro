import uuid

import pytest

from aiobaro import __version__


def test_version():
    assert __version__ == "0.1.0"


@pytest.mark.asyncio
async def test_login_info(matrix_client):
    result = await matrix_client.login_info()
    assert result.ok


@pytest.mark.asyncio
async def test_register(matrix_client):
    result = await matrix_client.register(
        "test_user", password="test_password"
    )
    assert result.ok


@pytest.mark.asyncio
async def test_login(matrix_client):
    result = await matrix_client.login("test_user", password="test_password")
    assert result.ok


@pytest.mark.asyncio
async def test_room_create(matrix_client, seed_data):

    room_alias_name = None
    name = "Room"
    topic = None
    room_version = None
    federate = True
    is_direct = False
    preset = None
    invite = None
    initial_state = None
    power_level_override = None

    result = await matrix_client.room_create(
        name=name,
        room_alias_name=room_alias_name,
        topic=topic,
        room_version=room_version,
        federate=federate,
        is_direct=is_direct,
        preset=preset,
        invite=invite,
        initial_state=initial_state,
        power_level_override=power_level_override,
    )
    assert result.ok
    assert result.json().get("room_id")


@pytest.mark.asyncio
async def test_sync(matrix_client):
    since = None
    timeout = None
    data_filter = None
    full_state = None
    set_presence = None
    result = await matrix_client.sync(
        since=since,
        timeout=timeout,
        data_filter=data_filter,
        full_state=full_state,
        set_presence=set_presence,
    )
    assert result.ok


@pytest.mark.asyncio
async def test_room_send(matrix_client, seed_data):
    room_id = seed_data.room.json()["room_id"]
    event_type = "m.aiobaro.text.msg"
    body = {"body": "hello"}
    tx_id = str(uuid.uuid1())
    result = await matrix_client.room_send(
        room_id,
        event_type,
        body,
        tx_id,
    )
    assert result.ok
    assert result.json()["event_id"]


@pytest.mark.asyncio
async def test_room_get_event(matrix_client, seed_data):
    # Create an event
    room_id = seed_data.room.json()["room_id"]
    result = await matrix_client.room_send(
        room_id,
        "m.aiobaro.text.msg",
        {"body": "TEST 0"},
        str(uuid.uuid1()),
    )
    assert result.ok
    event_id = result.json()["event_id"]

    # get the event
    result = await matrix_client.room_get_event(room_id, event_id)
    assert result.ok
    assert result.json()["content"]["body"] == "TEST 0"


@pytest.mark.asyncio
async def test_room_put_state(matrix_client, seed_data):
    result = await matrix_client.room_put_state(
        room_id=seed_data.room.json()["room_id"],
        event_type="m.aiobaro.state.event.tests",
        body={"test.key": "test.value"},
        state_key="state-key-test",
    )
    assert result.ok
    assert result.json()["event_id"]


@pytest.mark.asyncio
async def test_room_get_state_event(matrix_client, seed_data):
    room_id = seed_data.room.json()["room_id"]
    event_type = "m.aiobaro.state.event.tests"
    state_key = "state-key-test"

    result = await matrix_client.room_put_state(
        room_id=room_id,
        event_type="m.aiobaro.state.event.tests",
        body={"test.key": "test.value.1"},
        state_key=state_key,
    )
    assert result.ok

    result = await matrix_client.room_get_state_event(
        room_id, event_type, state_key=state_key
    )
    assert result.ok
    assert result.json()["test.key"] == "test.value.1"


@pytest.mark.asyncio
async def test_room_get_state(matrix_client, seed_data):
    room_id = seed_data.room.json()["room_id"]
    result = await matrix_client.room_get_state(room_id)
    assert result.ok


async def test_room_redact(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_redact(*args, **kwargs)
    assert result.ok


async def test_room_kick(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_kick(*args, **kwargs)
    assert result.ok


async def test_room_ban(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_ban(*args, **kwargs)
    assert result.ok


async def test_room_unban(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_unban(*args, **kwargs)
    assert result.ok


async def test_room_invite(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_invite(*args, **kwargs)
    assert result.ok


async def test_join(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.join(*args, **kwargs)
    assert result.ok


async def test_room_leave(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_leave(*args, **kwargs)
    assert result.ok


async def test_room_forget(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_forget(*args, **kwargs)
    assert result.ok


async def test_room_messages(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_messages(*args, **kwargs)
    assert result.ok


async def test_keys_upload(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.keys_upload(*args, **kwargs)
    assert result.ok


async def test_keys_query(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.keys_query(*args, **kwargs)
    assert result.ok


async def test_keys_claim(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.keys_claim(*args, **kwargs)
    assert result.ok


@pytest.mark.asyncio
async def test_to_device(matrix_client, seed_data):

    devices_info = seed_data.devices
    device_id = devices_info.json()["devices"][0]["device_id"]

    event_type = "m.new_device"
    tx_id = str(uuid.uuid1())
    user = seed_data.users[0].json()

    content = {
        "messages": {
            user["user_id"]: {device_id: {"example_content_key": "value"}}
        }
    }

    result = await matrix_client.to_device(event_type, content, tx_id)
    assert result.ok


@pytest.mark.asyncio
async def test_devices(matrix_client, seed_data):
    result = await matrix_client.devices()
    assert result.ok
    assert len(result.json()["devices"]) == 2


@pytest.mark.asyncio
async def test_update_device(matrix_client, seed_data):

    devices_info = seed_data.devices
    assert (
        devices_info.json()["devices"][0]["display_name"]
        == "Seed_user_1' device"
    )

    device_id = devices_info.json()["devices"][0]["device_id"]

    content = {"display_name": "Test User's Phone"}

    result = await matrix_client.update_device(device_id, content)
    assert result.ok
    devices = await matrix_client.devices()
    assert list(
        filter(
            lambda d: d["display_name"] == "Test User's Phone",
            devices.json()["devices"],
        )
    )


@pytest.mark.asyncio
async def test_delete_devices(matrix_client, seed_data):

    devices_to_delete = [seed_data.devices.json()["devices"][0]["device_id"]]

    user = await matrix_client.whoami()
    assert user.ok

    auth = {
        "type": "m.login.password",
        "identifier": {"type": "m.id.user", "user": user.json()["user_id"]},
        "password": "seed_password",
    }
    result = await matrix_client.delete_devices(devices_to_delete, auth=auth)
    assert result.ok

    devices = await matrix_client.devices()
    assert devices.ok
    assert not set(
        map(lambda d: d["device_id"], devices.json()["devices"])
    ) & set(devices_to_delete)


async def test_joined_members(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.joined_members(*args, **kwargs)
    assert result.ok


async def test_joined_rooms(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.joined_rooms(*args, **kwargs)
    assert result.ok


async def test_room_resolve_alias(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_resolve_alias(*args, **kwargs)
    assert result.ok


async def test_room_typing(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_typing(*args, **kwargs)
    assert result.ok


async def test_update_receipt_marker(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.update_receipt_marker(*args, **kwargs)
    assert result.ok


async def test_room_read_markers(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_read_markers(*args, **kwargs)
    assert result.ok


async def test_content_repository_config(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.content_repository_config(*args, **kwargs)
    assert result.ok


async def test_upload(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.upload(*args, **kwargs)
    assert result.ok


async def test_download(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.download(*args, **kwargs)
    assert result.ok


async def test_thumbnail(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.thumbnail(*args, **kwargs)
    assert result.ok


@pytest.mark.asyncio
async def test_profile_set_displayname(matrix_client):
    await test_register(matrix_client)
    await test_login(matrix_client)

    user_id = "@test_user:baro"
    display_name = "Test USER"
    result = await matrix_client.profile_set_displayname(user_id, display_name)
    assert result.ok


@pytest.mark.asyncio
async def test_profile_get_displayname(matrix_client):
    await test_profile_set_displayname(matrix_client)

    user_id = "@test_user:baro"
    result = await matrix_client.profile_get_displayname(user_id)
    assert result.ok
    assert result.json().get("displayname") == "Test USER"


@pytest.mark.asyncio
async def test_profile_set_avatar(matrix_client):
    await test_register(matrix_client)
    await test_login(matrix_client)

    user_id = "@test_user:baro"
    avatar_url = "mxc://matrix.org/avatar_url"
    result = await matrix_client.profile_set_avatar(user_id, avatar_url)
    assert result.ok


@pytest.mark.asyncio
async def test_profile_get_avatar(matrix_client):
    await test_profile_set_avatar(matrix_client)

    user_id = "@test_user:baro"
    result = await matrix_client.profile_get_avatar(user_id)
    assert result.ok
    assert result.json().get("avatar_url") == "mxc://matrix.org/avatar_url"


@pytest.mark.asyncio
async def test_profile_get(matrix_client):
    await test_register(matrix_client)
    await test_login(matrix_client)

    user_id = "@test_user:baro"
    result = await matrix_client.profile_get(user_id)
    assert result.ok
    assert result.json().get("displayname") == "test_user"


@pytest.mark.asyncio
async def test_set_presence(matrix_client):
    await test_register(matrix_client)
    await test_login(matrix_client)

    user_id = "@test_user:baro"
    presence = "online"

    result = await matrix_client.set_presence(user_id, presence)
    assert result.ok


@pytest.mark.asyncio
async def test_get_presence(matrix_client):
    await test_set_presence(matrix_client)

    user_id = "@test_user:baro"
    result = await matrix_client.get_presence(user_id)
    assert result.ok
    assert result.json().get("presence") == "online"


@pytest.mark.asyncio
async def test_whoami(matrix_client):
    await test_register(matrix_client)
    await test_login(matrix_client)

    result = await matrix_client.whoami()
    assert result.ok
    assert result.json().get("user_id")


async def test_room_context(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_context(*args, **kwargs)
    assert result.ok


async def test_upload_filter(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.upload_filter(*args, **kwargs)
    assert result.ok


async def test_set_pushrule(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.set_pushrule(*args, **kwargs)
    assert result.ok


async def test_delete_pushrule(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.delete_pushrule(*args, **kwargs)
    assert result.ok


async def test_enable_pushrule(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.enable_pushrule(*args, **kwargs)
    assert result.ok


async def test_set_pushrule_actions(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.set_pushrule_actions(*args, **kwargs)
    assert result.ok


@pytest.mark.asyncio
async def test_logout(matrix_client):
    result = await matrix_client.logout()
    assert result.ok
