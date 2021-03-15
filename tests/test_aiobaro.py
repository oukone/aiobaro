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
async def test_room_create(matrix_client):
    await test_register(matrix_client)
    await test_login(matrix_client)

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
async def test_room_send(matrix_client):
    room_id = None
    event_type = None
    body = None
    tx_id = None
    result = await matrix_client.room_send(
        room_id,
        event_type,
        body,
        tx_id,
    )
    assert result.ok


@pytest.mark.asyncio
async def test_room_get_event(matrix_client):
    room_id, event_id = None, None
    result = await matrix_client.room_get_event(room_id, event_id)
    assert result.ok


async def test_room_put_state(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_put_state(*args, **kwargs)
    assert result.ok


async def test_room_get_state_event(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_get_state_event(*args, **kwargs)
    assert result.ok


async def test_room_get_state(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_get_state(*args, **kwargs)
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
async def test_to_device(matrix_client):
    await test_register(matrix_client)
    await test_login(matrix_client)

    event_type = "m.new_device"
    tx_id = "35"
    messages = {
        "@test_user:baro": {"TLLBEANAAG": {"example_content_key": "value"}}
    }
    result = await matrix_client.to_device(event_type, messages, tx_id)
    assert result.ok


async def test_devices(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.devices(*args, **kwargs)
    assert result.ok


async def test_update_device(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.update_device(*args, **kwargs)
    assert result.ok


async def test_delete_devices(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.delete_devices(*args, **kwargs)
    assert result.ok


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
