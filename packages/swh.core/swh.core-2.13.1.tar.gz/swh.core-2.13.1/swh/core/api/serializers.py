# Copyright (C) 2015-2020  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import base64
import datetime
from enum import Enum
import json
import traceback
import types
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from uuid import UUID

import iso8601
import msgpack
from requests import Response

from swh.core.api.classes import PagedResult


def encode_datetime(dt: datetime.datetime) -> str:
    """Wrapper of datetime.datetime.isoformat() that forbids naive datetimes."""
    if dt.tzinfo is None:
        raise TypeError("can not serialize naive 'datetime.datetime' object")
    return dt.isoformat()


def _encode_paged_result(obj: PagedResult) -> Dict[str, Any]:
    """Serialize PagedResult to a Dict."""
    return {
        "results": obj.results,
        "next_page_token": obj.next_page_token,
    }


def _decode_paged_result(obj: Dict[str, Any]) -> PagedResult:
    """Deserialize Dict into PagedResult"""
    return PagedResult(
        results=obj["results"],
        next_page_token=obj["next_page_token"],
    )


def exception_to_dict(exception: Exception) -> Dict[str, Any]:
    tb = traceback.format_exception(None, exception, exception.__traceback__)
    exc_type = type(exception)
    return {
        "type": exc_type.__name__,
        "module": exc_type.__module__,
        "args": exception.args,
        "message": str(exception),
        "traceback": tb,
    }


def dict_to_exception(exc_dict: Dict[str, Any]) -> Exception:
    temp = __import__(exc_dict["module"], fromlist=[exc_dict["type"]])
    try:
        return getattr(temp, exc_dict["type"])(*exc_dict["args"])
    except Exception:
        # custom Exception type cannot be rebuilt, fallback to base Exception type
        return Exception(exc_dict["message"])


def encode_timedelta(td: datetime.timedelta) -> Dict[str, int]:
    return {
        "days": td.days,
        "seconds": td.seconds,
        "microseconds": td.microseconds,
    }


ENCODERS: List[Tuple[type, str, Callable]] = [
    (UUID, "uuid", str),
    (datetime.timedelta, "timedelta", encode_timedelta),
    (PagedResult, "paged_result", _encode_paged_result),
    (Exception, "exception", exception_to_dict),
]

JSON_ENCODERS: List[Tuple[type, str, Callable]] = [
    (datetime.datetime, "datetime", encode_datetime),
    (bytes, "bytes", lambda o: base64.b85encode(o).decode("ascii")),
]

DECODERS: Dict[str, Callable] = {
    "timedelta": lambda d: datetime.timedelta(**d),
    "uuid": UUID,
    "paged_result": _decode_paged_result,
    "exception": dict_to_exception,
    # for BW compat, to be moved in JSON_DECODERS ASAP
    "datetime": lambda d: iso8601.parse_date(d, default_timezone=None),
}

JSON_DECODERS: Dict[str, Callable] = {
    "bytes": base64.b85decode,
}


def get_encoders(
    extra_encoders: Optional[List[Tuple[Type, str, Callable]]], with_json: bool = False
) -> List[Tuple[Type, str, Callable]]:
    encoders = ENCODERS
    if with_json:
        encoders = [*encoders, *JSON_ENCODERS]
    if extra_encoders:
        encoders = [*encoders, *extra_encoders]
    return encoders


def get_decoders(
    extra_decoders: Optional[Dict[str, Callable]], with_json: bool = False
) -> Dict[str, Callable]:
    decoders = DECODERS
    if with_json:
        decoders = {**decoders, **JSON_DECODERS}
    if extra_decoders is not None:
        decoders = {**decoders, **extra_decoders}
    return decoders


class MsgpackExtTypeCodes(Enum):
    LONG_INT = 1
    LONG_NEG_INT = 2


def encode_data_client(data: Any, extra_encoders=None) -> bytes:
    try:
        return msgpack_dumps(data, extra_encoders=extra_encoders)
    except OverflowError as e:
        raise ValueError("Limits were reached. Please, check your input.\n" + str(e))


def decode_response(response: Response, extra_decoders=None) -> Any:
    content_type = response.headers["content-type"]

    if content_type.startswith("application/x-msgpack"):
        r = msgpack_loads(response.content, extra_decoders=extra_decoders)
    elif content_type.startswith("application/json"):
        r = json_loads(response.text, extra_decoders=extra_decoders)
    elif content_type.startswith("text/"):
        r = response.text
    else:
        raise ValueError("Wrong content type `%s` for API response" % content_type)

    return r


class SWHJSONEncoder(json.JSONEncoder):
    """JSON encoder for data structures generated by Software Heritage.

    This JSON encoder extends the default Python JSON encoder and adds
    awareness for the following specific types:

    - bytes (get encoded as a Base85 string);
    - datetime.datetime (get encoded as an ISO8601 string).

    Non-standard types get encoded as a a dictionary with two keys:

    - swhtype with value 'bytes' or 'datetime';
    - d containing the encoded value.

    SWHJSONEncoder also encodes arbitrary iterables as a list
    (allowing serialization of generators).

    Caveats: Limitations in the JSONEncoder extension mechanism
    prevent us from "escaping" dictionaries that only contain the
    swhtype and d keys, and therefore arbitrary data structures can't
    be round-tripped through SWHJSONEncoder and SWHJSONDecoder.

    """

    def __init__(self, extra_encoders=None, **kwargs):
        super().__init__(**kwargs)
        self.encoders = get_encoders(extra_encoders, with_json=True)

    def default(self, o: Any) -> Union[Dict[str, Union[Dict[str, int], str]], list]:
        for (type_, type_name, encoder) in self.encoders:
            if isinstance(o, type_):
                return {
                    "swhtype": type_name,
                    "d": encoder(o),
                }
        try:
            return super().default(o)
        except TypeError as e:
            try:
                iterable = iter(o)
            except TypeError:
                raise e from None
            else:
                return list(iterable)


class SWHJSONDecoder(json.JSONDecoder):
    """JSON decoder for data structures encoded with SWHJSONEncoder.

    This JSON decoder extends the default Python JSON decoder,
    allowing the decoding of:

    - bytes (encoded as a Base85 string);
    - datetime.datetime (encoded as an ISO8601 string).

    Non-standard types must be encoded as a a dictionary with exactly
    two keys:

    - swhtype with value 'bytes' or 'datetime';
    - d containing the encoded value.

    To limit the impact our encoding, if the swhtype key doesn't
    contain a known value, the dictionary is decoded as-is.

    """

    def __init__(self, extra_decoders=None, **kwargs):
        super().__init__(**kwargs)
        self.decoders = get_decoders(extra_decoders, with_json=True)

    def decode_data(self, o: Any) -> Any:
        if isinstance(o, dict):
            if set(o.keys()) == {"d", "swhtype"}:
                if o["swhtype"] == "bytes":
                    return base64.b85decode(o["d"])
                decoder = self.decoders.get(o["swhtype"])
                if decoder:
                    return decoder(self.decode_data(o["d"]))
            return {key: self.decode_data(value) for key, value in o.items()}
        if isinstance(o, list):
            return [self.decode_data(value) for value in o]
        else:
            return o

    def raw_decode(self, s: str, idx: int = 0) -> Tuple[Any, int]:
        data, index = super().raw_decode(s, idx)
        return self.decode_data(data), index


def json_dumps(data: Any, extra_encoders=None) -> str:
    return json.dumps(data, cls=SWHJSONEncoder, extra_encoders=extra_encoders)


def json_loads(data: str, extra_decoders=None) -> Any:
    return json.loads(data, cls=SWHJSONDecoder, extra_decoders=extra_decoders)


def msgpack_dumps(data: Any, extra_encoders=None) -> bytes:
    """Write data as a msgpack stream"""
    encoders = get_encoders(extra_encoders)

    def encode_types(obj):
        if isinstance(obj, int):
            # integer overflowed while packing. Handle it as an extended type
            if obj > 0:
                code = MsgpackExtTypeCodes.LONG_INT.value
            else:
                code = MsgpackExtTypeCodes.LONG_NEG_INT.value
                obj = -obj
            length, rem = divmod(obj.bit_length(), 8)
            if rem:
                length += 1
            return msgpack.ExtType(code, int.to_bytes(obj, length, "big"))

        if isinstance(obj, types.GeneratorType):
            return list(obj)

        for (type_, type_name, encoder) in encoders:
            if isinstance(obj, type_):
                return {
                    b"swhtype": type_name,
                    b"d": encoder(obj),
                }
        return obj

    return msgpack.packb(
        data,
        use_bin_type=True,
        datetime=True,  # encode datetime as msgpack.Timestamp
        default=encode_types,
    )


def msgpack_loads(data: bytes, extra_decoders=None) -> Any:
    """Read data as a msgpack stream.

    .. Caution::
       This function is used by swh.journal to decode the contents of the
       journal. This function **must** be kept backwards-compatible.
    """
    decoders = get_decoders(extra_decoders)

    def ext_hook(code, data):
        if code == MsgpackExtTypeCodes.LONG_INT.value:
            return int.from_bytes(data, "big")
        elif code == MsgpackExtTypeCodes.LONG_NEG_INT.value:
            return -int.from_bytes(data, "big")
        raise ValueError("Unknown msgpack extended code %s" % code)

    def decode_types(obj):
        # Support for current encodings
        if set(obj.keys()) == {b"d", b"swhtype"}:
            decoder = decoders.get(obj[b"swhtype"])
            if decoder:
                return decoder(obj[b"d"])

        # Fallthrough
        return obj

    return msgpack.unpackb(
        data,
        raw=False,
        object_hook=decode_types,
        ext_hook=ext_hook,
        strict_map_key=False,
        timestamp=3,  # convert Timestamp in datetime objects (tz UTC)
    )
