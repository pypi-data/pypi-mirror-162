import hashlib
import json
import math
import sys
from http.cookies import SimpleCookie
from secrets import token_urlsafe
from typing import Dict, Any, Optional, Union

from kameleoon.defaults import KAMELEOON_COOKIE_VALUE_LENGTH, KAMELEOON_VISITOR_CODE_LENGTH, KAMELEOON_COOKIE_NAME, \
    KAMELEOON_KEY_JS_COOKIE
from kameleoon.exceptions import VisitorCodeNotValid


def obtain_hash_double(visitor_code, respool_times=None, container_id='') -> float:
    if respool_times is None:
        respool_times = {}
    identifier = str(visitor_code)
    identifier += str(container_id)
    if respool_times:
        identifier += ''.join([str(v) for k, v in sorted(respool_times.items())])
    return int(hashlib.sha256(identifier.encode('UTF-8')).hexdigest(), 16) / math.pow(2, 256)


def load_params_from_json(json_path) -> Dict[Any, Any]:
    with open(json_path) as f:
        return json.load(f)


def get_size(obj) -> float:
    return sum([sys.getsizeof(v) + sys.getsizeof(k) for k, v in obj.items()])


def check_visitor_code(default_visitor_code: str) -> str:
    """
    default_visitor_code validation
    :param default_visitor_code:
    :type default_visitor_code: str
    :return: default_visitor_code
    """
    if len(default_visitor_code) > KAMELEOON_VISITOR_CODE_LENGTH:
        raise VisitorCodeNotValid('is longer than 255 chars')
    if default_visitor_code == '':
        raise VisitorCodeNotValid('empty visitor code')
    return default_visitor_code


def read_kameleoon_cookie_value(cookies: Union[str, Dict[str, str]],
                                default_visitor_code: Union[str, None]) -> str:
    """
    Reading kameleoon cookie value from cookies.
    :param default_visitor_code:
    :type default_visitor_code: str
    :param cookies: str ot dict
    :return: str or None
    """
    cookie: Any = SimpleCookie()
    cookie.load(cookies)
    kameleoon_cookie = cookie.get(KAMELEOON_COOKIE_NAME)
    if kameleoon_cookie:
        kameleoon_cookie_value = kameleoon_cookie.value
        if kameleoon_cookie_value.startswith(KAMELEOON_KEY_JS_COOKIE):
            kameleoon_cookie_value = kameleoon_cookie_value[
                                     len(KAMELEOON_KEY_JS_COOKIE):]
        return kameleoon_cookie_value
    elif default_visitor_code or default_visitor_code == '':
        return check_visitor_code(default_visitor_code)
    return token_urlsafe(KAMELEOON_COOKIE_VALUE_LENGTH)
