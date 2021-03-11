import hashlib
import hmac
import typing
from collections import defaultdict
from enum import Enum
from pathlib import PurePath
from types import GeneratorType
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import httpx
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from pydantic.json import ENCODERS_BY_TYPE  # pylint: disable=no-name-in-module

from .exceptions import LoginRequiredException
from .models import (
    ByteStream,
    CookieTypes,
    HeaderTypes,
    HttpVerbs,
    MatrixResponse,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
)

SetIntStr = Set[Union[int, str]]
DictIntStrAny = Dict[Union[int, str], Any]


def generate_encoders_by_class_tuples(
    type_encoder_map: Dict[Any, Callable[[Any], Any]]
) -> Dict[Callable[[Any], Any], Tuple[Any, ...]]:
    encoders_by_class_tuples: Dict[
        Callable[[Any], Any], Tuple[Any, ...]
    ] = defaultdict(tuple)
    for type_, encoder in type_encoder_map.items():
        encoders_by_class_tuples[encoder] += (type_,)
    return encoders_by_class_tuples


encoders_by_class_tuples = generate_encoders_by_class_tuples(ENCODERS_BY_TYPE)

# flake8: noqa: C901
def jsonable_encoder(
    obj: Any,
    include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    custom_encoder: Dict[Any, Callable[[Any], Any]] = {},
    sqlalchemy_safe: bool = True,
) -> Any:
    if include is not None and not isinstance(include, set):
        include = set(include)
    if exclude is not None and not isinstance(exclude, set):
        exclude = set(exclude)
    if isinstance(obj, BaseModel):
        encoder = getattr(obj.__config__, "json_encoders", {})
        if custom_encoder:
            encoder.update(custom_encoder)
        obj_dict = obj.dict(
            include=include,  # type: ignore # in Pydantic
            exclude=exclude,  # type: ignore # in Pydantic
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
        )
        if "__root__" in obj_dict:
            obj_dict = obj_dict["__root__"]
        return jsonable_encoder(
            obj_dict,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
            custom_encoder=encoder,
            sqlalchemy_safe=sqlalchemy_safe,
        )
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, PurePath):
        return str(obj)
    if isinstance(obj, (str, int, float, type(None))):
        return obj
    if isinstance(obj, dict):
        encoded_dict = {}
        for key, value in obj.items():
            if (
                (
                    not sqlalchemy_safe
                    or (not isinstance(key, str))
                    or (not key.startswith("_sa"))
                )
                and (value is not None or not exclude_none)
                and (
                    (include and key in include)
                    or not exclude
                    or key not in exclude
                )
            ):
                encoded_key = jsonable_encoder(
                    key,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_value = jsonable_encoder(
                    value,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_dict[encoded_key] = encoded_value
        return encoded_dict
    if isinstance(obj, (list, set, frozenset, GeneratorType, tuple)):
        encoded_list = []
        for item in obj:
            encoded_list.append(
                jsonable_encoder(
                    item,
                    include=include,
                    exclude=exclude,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
            )
        return encoded_list

    if custom_encoder:
        if type(obj) in custom_encoder:
            return custom_encoder[type(obj)](obj)
        else:
            for encoder_type, encoder in custom_encoder.items():
                if isinstance(obj, encoder_type):
                    return encoder(obj)

    if type(obj) in ENCODERS_BY_TYPE:
        return ENCODERS_BY_TYPE[type(obj)](obj)
    for encoder, classes_tuple in encoders_by_class_tuples.items():
        if isinstance(obj, classes_tuple):
            return encoder(obj)

    errors: List[Exception] = []
    try:
        data = dict(obj)
    except Exception as e:
        errors.append(e)
        try:
            data = vars(obj)
        except Exception as e:
            errors.append(e)
            raise ValueError(errors)
    return jsonable_encoder(
        data,
        by_alias=by_alias,
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults,
        exclude_none=exclude_none,
        custom_encoder=custom_encoder,
        sqlalchemy_safe=sqlalchemy_safe,
    )


def request_registration(
    user,
    password,
    server_location,
    shared_secret,
    admin=False,
    user_type=None,
    requests=httpx,
):

    url = "%s/_synapse/admin/v1/register" % (server_location.rstrip("/"),)

    # Get the nonce
    r = requests.get(url, trust_env=False)

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


def auth_required(method):
    async def inner(
        self,
        verb: HttpVerbs,
        path: str,
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
            raise LoginRequiredException(
                status_code=401, message="Invalid access_token"
            )
        return await method(
            self,
            verb,
            path,
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


async def matrix_client(
    homeserver: str,
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
    json: typing.Any = None,
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
            f"{homeserver.strip('/')}/{path.lstrip('/')}",
            **dict(filter(lambda x: x[1], client_config.items())),
        )
        response: httpx.Response = await client.send(request)
    return MatrixResponse(response)


def mimetype_to_msgtype(mimetype: str) -> str:
    """Turn a mimetype into a matrix message type."""
    if mimetype.startswith("image"):
        return "m.image"
    elif mimetype.startswith("video"):
        return "m.video"
    elif mimetype.startswith("audio"):
        return "m.audio"

    return "m.file"
