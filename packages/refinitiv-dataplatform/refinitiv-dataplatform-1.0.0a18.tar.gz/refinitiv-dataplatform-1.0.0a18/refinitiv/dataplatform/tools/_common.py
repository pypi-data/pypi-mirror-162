from typing import Union
from urllib.parse import ParseResult, urlparse, ParseResultBytes

import numpy as np


def get_from_path(obj, path, delim="."):
    splitted = path.split(delim)
    for k in splitted:
        if hasattr(obj, "get"):
            obj = obj.get(k)
        elif iterable(obj) and is_int(k):
            obj = obj[int(k)]
    return obj


def is_int(obj):
    if isinstance(obj, str):
        try:
            int(obj)
        except Exception:
            return False
        else:
            return True
    return isinstance(obj, int)


def iterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True


def urljoin(*pieces):
    # first piece have a leading slash
    if pieces and len(pieces[0]) > 1 and pieces[0][0] == "/":
        pieces = ("/",) + pieces
    # last piece have a trailing slash
    if pieces and len(pieces[-1]) > 1 and pieces[-1][-1] == "/":
        pieces = pieces + ("/",)
    return "/".join(s.strip("/") for s in pieces)


def is_any_defined(*args):
    return any(args)


def is_all_defined(*args):
    return all(args)


def is_all_same_type(item_type, iterable):
    return all(isinstance(item, item_type) for item in iterable)


def make_counter():
    i = 0

    def counter():
        nonlocal i
        i += 1
        return i

    return counter


def get_response_reason(response):
    if hasattr(response, "reason_phrase"):
        assert not hasattr(response, "reason")
        return response.reason_phrase
    elif hasattr(response, "reason"):
        return response.reason
    return "unknown reason"


class cached_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result


def parse_list_of_str(param: Union[str, list]) -> list:
    if isinstance(param, str):
        return [param]

    if isinstance(param, list):
        if is_all_same_type(str, param):
            return param
        else:
            raise ValueError(f"Not all elements are strings in {param}")

    raise ValueError(f"Invalid type, expected str or list:{type(param)} is given")


class ArgsParser:
    def __init__(self, parse) -> None:
        self.parse = parse

    def get_str(self, *args, delim=None) -> str:
        if delim is not None:
            retval = delim.join(str(item) for item in self.get_list(*args))
        else:
            retval = self.parse(*args)
            if not isinstance(retval, str):
                retval = str(retval)
        return retval

    def get_list(self, *args) -> list:
        retval = self.parse(*args)
        if not isinstance(retval, list):
            retval = [retval]
        return retval

    def get_float(self, *args) -> float:
        retval = self.parse(*args)
        if isinstance(retval, np.datetime64):
            retval = retval.astype(float)
        else:
            retval = float(retval)
        return retval

    def get_bool(self, *args) -> bool:
        retval = self.parse(*args)
        if not isinstance(retval, bool):
            retval = bool(retval)
        return retval


universe_arg_parser = ArgsParser(parse_list_of_str)


def parse_url(url: str) -> ParseResult:
    import sys

    py_ver = sys.version_info
    if py_ver.major == 3 and py_ver.minor < 9:

        result_urlparse = urlparse(url)

        if isinstance(result_urlparse, ParseResultBytes):
            return result_urlparse

        scheme = result_urlparse.scheme
        netloc = result_urlparse.netloc
        path = result_urlparse.path
        query = result_urlparse.query
        fragment = result_urlparse.fragment

        if not scheme and not netloc and path and ":" in path:
            splitted = path.split(":")
            if len(splitted) == 2:
                scheme, path = splitted

        result = ParseResult(
            scheme=scheme,
            netloc=netloc,
            path=path,
            params=result_urlparse.params,
            query=query,
            fragment=fragment,
        )
    else:

        result = urlparse(url)

    return result


def get_scheme_port(scheme, port):
    if not scheme and not port:
        scheme = "ws"
        port = 80

    elif not scheme and port:
        scheme = "ws"
        if port == 443:
            scheme = "wss"

    elif scheme and not port:
        port = 80
        if scheme == "wss":
            port = 443

    return scheme, port
