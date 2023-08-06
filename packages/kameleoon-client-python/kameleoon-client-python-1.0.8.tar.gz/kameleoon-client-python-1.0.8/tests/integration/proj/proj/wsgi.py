"""
WSGI config for proj project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import sys
import uuid

from kameleoon import KameleoonWSGIMiddleware

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')

application = KameleoonWSGIMiddleware(get_wsgi_application(), '127.0.0.1', uuid.uuid4().hex)
