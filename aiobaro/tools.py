import hashlib
import hmac
import typing

import httpx
import requests as _requests
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from httpx._models import (
    ByteStream,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
)

from .models import HttpVerbs


def request_registration(
    user,
    password,
    server_location,
    shared_secret,
    admin=False,
    user_type=None,
    requests=_requests,
):

    url = "%s/_synapse/admin/v1/register" % (server_location.rstrip("/"),)

    # Get the nonce
    r = requests.get(url, verify=False)

    if r.status_code != 200:
        return r

    nonce = r.json()["nonce"]
    mac = hmac.new(key=shared_secret.encode("utf8"), digestmod=hashlib.sha1)

    mac.update(nonce.encode("utf8"))
    mac.update(b"\x00")
    mac.update(user.encode("utf8"))
    mac.update(b"\x00")
    mac.update(password.encode("utf8"))
    mac.update(b"\x00")
    mac.update(b"admin" if admin else b"notadmin")
    if user_type:
        mac.update(b"\x00")
        mac.update(user_type.encode("utf8"))

    mac = mac.hexdigest()

    data = {
        "nonce": nonce,
        "username": user,
        "password": password,
        "mac": mac,
        "admin": admin,
        "user_type": user_type,
    }
    return requests.post(url, json=data, verify=False)


async def synapse_client(
    homeserver: str,
    method: HttpVerbs,
    uri,
    *,
    params: QueryParamTypes = None,
    headers: HeaderTypes = None,
    cookies: CookieTypes = None,
    content: RequestContent = None,
    data: RequestData = None,
    files: RequestFiles = None,
    json: typing.Any = None,
    stream: ByteStream = None,
):
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
            method.upper(),
            f"{homeserver.strip('/')}/{uri.lstrip('/')}",
            **dict(filter(lambda x: x[1], client_config.items())),
        )
        response: httpx.Response = await client.send(request)
    return response


def login_required(method):
    async def inner(
        self,
        uri,
        verb: HttpVerbs,
        *,
        params: QueryParamTypes = None,
        headers: HeaderTypes = None,
        cookies: CookieTypes = None,
        content: RequestContent = None,
        data: RequestData = None,
        files: RequestFiles = None,
        json: typing.Any = None,
        stream: ByteStream = None,
    ):
        if isinstance(params, dict):
            params.setdefault("access_token", self.access_token)
        else:
            params = dict(access_token=self.access_token)

        if not params["access_token"]:
            raise HTTPException(details=401, detail="Invalid access_token")

        return await method(
            self,
            uri,
            verb,
            params=params,
            headers=headers,
            cookies=cookies,
            content=content,
            data=data,
            files=files,
            json=json,
            stream=stream,
        )

    return inner


def admin_required(method):
    async def inner(
        self,
        uri,
        verb: HttpVerbs,
        *,
        params: QueryParamTypes = None,
        headers: HeaderTypes = None,
        cookies: CookieTypes = None,
        content: RequestContent = None,
        data: RequestData = None,
        files: RequestFiles = None,
        json: typing.Any = None,
        stream: ByteStream = None,
    ):
        result = await synapse_client(
            self.homeserver,
            "GET",
            "/_synapse/admin/v1/users/@admin:fogo/admin",
            params=params or {},
        )
        if result.status_code != 200:
            return result

        return await method(
            self,
            uri,
            verb,
            params=params,
            headers=headers,
            cookies=cookies,
            content=content,
            data=data,
            files=files,
            json=json,
            stream=stream,
        )

    return inner


def mimetype_to_msgtype(mimetype: str) -> str:
    """Turn a mimetype into a matrix message type."""
    if mimetype.startswith("image"):
        return "m.image"
    elif mimetype.startswith("video"):
        return "m.video"
    elif mimetype.startswith("audio"):
        return "m.audio"

    return "m.file"
