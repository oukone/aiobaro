from aiobaro import __version__


def test_version():
    assert __version__ == "0.1.0"


async def test_login_info(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.login_info(*args, **kwargs)
    assert result.ok


async def test_login(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.login(*args, **kwargs)
    assert result.ok


async def test_register(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.register(*args, **kwargs)
    assert result.ok


async def test_logout(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.logout(*args, **kwargs)
    assert result.ok


async def test_sync(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.sync(*args, **kwargs)
    assert result.ok


async def test_room_send(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_send(*args, **kwargs)
    assert result.ok


async def test_room_get_event(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_get_event(*args, **kwargs)
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


async def test_room_create(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.room_create(*args, **kwargs)
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


async def test_to_device(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.to_device(*args, **kwargs)
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


async def test_profile_get(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.profile_get(*args, **kwargs)
    assert result.ok


async def test_profile_get_displayname(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.profile_get_displayname(*args, **kwargs)
    assert result.ok


async def test_profile_set_displayname(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.profile_set_displayname(*args, **kwargs)
    assert result.ok


async def test_profile_get_avatar(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.profile_get_avatar(*args, **kwargs)
    assert result.ok


async def test_profile_set_avatar(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.profile_set_avatar(*args, **kwargs)
    assert result.ok


async def test_get_presence(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.get_presence(*args, **kwargs)
    assert result.ok


async def test_set_presence(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.set_presence(*args, **kwargs)
    assert result.ok


async def test_whoami(matrix_client):
    args, kwargs = [], {}
    result = await matrix_client.whoami(*args, **kwargs)
    assert result.ok


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
