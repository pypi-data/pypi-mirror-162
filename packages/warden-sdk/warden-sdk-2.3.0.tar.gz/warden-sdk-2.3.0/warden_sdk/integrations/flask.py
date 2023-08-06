"""Flask Integration that wraps a Flask app. 

This integration allows us to capture all exceptions thrown by within a Flask application.

Code reference:
- [warden_sdk](https://github.com/getwarden/warden-python/blob/master/warden_sdk/integrations/flask.py)
"""
from __future__ import absolute_import

import sys

from warden_sdk.hub import Hub
from warden_sdk.utils import (reraise, event_from_exception, capture_internal_exceptions,)
from warden_sdk.integrations import Integration, DidNotEnable
from warden_sdk.auth.headers import (
   add_secure_headers, 
   check_ssl_cert, 
   check_referrer
)
from warden_sdk.integrations._wsgi_common import RequestExtractor
from warden_sdk.integrations.wsgi import WardenWsgiMiddleware
from warden_sdk import User
from warden_sdk import ScopeGuard

try:
  from flask import Flask, Request  # type: ignore
  from flask import __version__ as FLASK_VERSION
  from flask import request as flask_request
  from flask.signals import (
    got_request_exception,
    request_started,
    request_finished,
  )
except ImportError:
  raise DidNotEnable("Flask is not installed")

from typing import (Any, Union)

try:
   import blinker  # noqa
except ImportError:
   raise DidNotEnable("blinker is not installed")

TRANSACTION_STYLE_VALUES = ("endpoint", "url")

class FlaskIntegration(Integration):
   """FlaskIntegration creates a wrapper for any Flask application.
   """
   identifier = "flask"

   def __init__(self, transaction_style="endpoint") -> None:
      if transaction_style not in TRANSACTION_STYLE_VALUES:
         raise ValueError(
            "Invalid value for transaction_style: %s (must be in %s)"
            % (transaction_style, TRANSACTION_STYLE_VALUES)
         )
      self.transaction_style = transaction_style

   @staticmethod
   def setup_once() -> None:
      # This version parsing is absolutely naive but the alternative is to
      # import pkg_resources which slows down the SDK a lot.
      try:
         version = tuple(map(int, FLASK_VERSION.split(".")[:3]))
      except (ValueError, TypeError):
         # It's probably a release candidate, we assume it's fine.
         pass
      else:
         if version < (0, 10):
            raise DidNotEnable("Flask 0.10 or newer is required.")

      request_started.connect(_request_started)
      got_request_exception.connect(_capture_exception)
      request_finished.connect(_request_finished)

      old_app = Flask.__call__

      def warden_patched_wsgi_app(self, environ, start_response):
        if Hub.current.get_integration(FlaskIntegration) is None:
            return old_app(self, environ, start_response)

        return WardenWsgiMiddleware(lambda *a, **kw: old_app(self, *a, **kw))(
            environ, start_response
        )

      Flask.__call__ = warden_patched_wsgi_app


def _request_started(app: Flask, **kwargs: Any) -> None:
   """Run events when Flask request has started.

   This is equivalent to when you use the @app.before_request decorator in a flask app.

   Args:
      app: the flask application.
      **kwargs: any kwargs added on to the flask.
   """
   hub = Hub.current
   integration = hub.get_integration(FlaskIntegration)
   if integration is None:
      return

   client = hub.client

   with hub.configure_scope() as scope:
      # Capture the top request to pull information out of. Flask's global request
      request = flask_request._get_current_object()
      
      try:
         check_ssl_cert(request)
         # check_referrer(request)
         User.setup(request)
      except Exception:
         exc_info = sys.exc_info()
         warden_event, hint = event_from_exception(
            exc_info,
            client_options=client.options,
            mechanism={"type": "flask", "handled": False},
         )
         hub.capture_event(warden_event, hint=hint)
         reraise(*exc_info)

      evt_processor = _make_request_event_processor(app, request, integration)
      scope.add_event_processor(evt_processor)


def _request_finished(sender: Flask, response: Any, **extra: Any) -> None:
   """Run after request has been finished.

   This is equivalent to when you use the @app.after_request decorator in a flask app. We need to add security headers to the responses.

   Args:
      sender: the flask application.
      response: the flask application response.
      **extra: any kwargs added on to the flask.
   """
   response = add_secure_headers(response)


def _capture_exception(sender: Flask, exception: Union[ValueError, BaseException], **kwargs: Any,) -> None:
  hub = Hub.current
  if hub.get_integration(FlaskIntegration) is None:
    return

  # If an integration is there, a client has to be there.
  client = hub.client  # type: Any
  event, hint = event_from_exception(
      exception,
      mechanism={"type": "flask", "handled": False},
  )

  hub.capture_event(event, hint=hint)

def verify_perms(userperms, apiperms):
   if ( (apiperms) and (not any(permission in userperms for permission in apiperms))):
      raise Exception({
            'error': 'invalid_request',
            'error_description': 'Invalid permissions.'
      })

# TODO(MP): if WSGI Middleware is needed, this class will be necessary with a RequestExtractor base class
class FlaskRequestExtractor(RequestExtractor):
   def env(self):
      return self.request.environ

   def cookies(self):
      return {
          k: v[0] if isinstance(v, list) and len(v) == 1 else v
          for k, v in self.request.cookies.items()
      }

   def raw_data(self) -> bytes:
      return self.request.get_data()

   def form(self):
      return self.request.form

   def files(self):
      return self.request.files

   def is_json(self):
      return self.request.is_json

   def json(self):
      return self.request.get_json()

   def size_of_file(self, file):
      return file.content_length

def _make_request_event_processor(app, request, integration):

   def inner(event, hint):
      # if the request is gone we are fine not logging the data from
      # it.  This might happen if the processor is pushed away to
      # another thread.
      if request is None:
         return event

      with capture_internal_exceptions():
         FlaskRequestExtractor(request).extract_into_event(event)

      return event

   return inner
