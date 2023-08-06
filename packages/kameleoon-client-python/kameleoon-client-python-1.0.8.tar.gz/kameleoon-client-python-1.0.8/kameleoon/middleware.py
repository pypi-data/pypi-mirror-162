""" WSGIMiddlewares """
import datetime
from http.cookies import Morsel
from typing import Optional, Any

from kameleoon.defaults import KAMELEOON_COOKIE_NAME, EXPIRE_DAYS, MAX_AGE
from kameleoon.helpers.functions import read_kameleoon_cookie_value

__all__ = ["KameleoonWSGIMiddleware", ]


class KameleoonWSGIMiddleware:
    """
    Automatically set kameleoon cookies
    """
    def __init__(self, app, top_level_domain: str, default_visitor_code: Optional[str] = None):
        self.app = app
        self.default_visitor_code = default_visitor_code
        self.top_level_domain = top_level_domain

    def __call__(self, environ, start_response):
        http_cookie = environ.get('HTTP_COOKIE') or {}
        kameleoon_cookie_value = read_kameleoon_cookie_value(http_cookie,
                                                             self.default_visitor_code)
        new_kameleoon_cookie: Any = Morsel()
        new_kameleoon_cookie.set(KAMELEOON_COOKIE_NAME, kameleoon_cookie_value, kameleoon_cookie_value)
        date_expires = datetime.datetime.utcnow() + datetime.timedelta(days=EXPIRE_DAYS)
        expires = date_expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
        new_kameleoon_cookie['expires'] = expires
        new_kameleoon_cookie['domain'] = self.top_level_domain
        new_kameleoon_cookie['path'] = '/'
        new_kameleoon_cookie['max-age'] = str(MAX_AGE)
        if KAMELEOON_COOKIE_NAME not in http_cookie:
            if 'HTTP_COOKIE' in environ:
                environ['HTTP_COOKIE'] += f"; {KAMELEOON_COOKIE_NAME}={kameleoon_cookie_value}"
            else:
                environ['HTTP_COOKIE'] = f"{KAMELEOON_COOKIE_NAME}={kameleoon_cookie_value}"

        def _custom_start_response(status, headers, exc_info=None):
            headers.append(('Set-Cookie', new_kameleoon_cookie.output(header='')))
            return start_response(status, headers, exc_info)

        return self.app(environ, _custom_start_response)
