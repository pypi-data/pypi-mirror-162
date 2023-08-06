"""Client class that controls everything in `warden_sdk`.

Client class is in-charge of bringing all of the components of the `warden_sdk` together; considered the engine. Use this module to call and instantiate a Client class when required such as when initializing a new thread for asyncio or multithreading. Otherwise, there's no need to instantiate a new Client class again.

  Typical usage example:

  from warden_sdk.client import Client
  client = Client(*args, **kwargs)

Code reference:
- [warden_sdk](https://github.com/getwarden/warden-python/blob/master/warden_sdk/client.py)
"""
from datetime import datetime
import logging
import uuid
import os
import random
import socket

from warden_sdk.integrations import setup_integrations
from warden_sdk.utils import ContextVar
from warden_sdk.utils import (
    iteritems,
    text_type,
    string_types,
    format_timestamp,
    capture_internal_exceptions,
    handle_in_app,
    current_stacktrace,
    logger,
    get_default_release,
    get_type_name,
    disable_capture_event,
)
from warden_sdk.transport import make_transport
from warden_sdk.consts import DEFAULT_OPTIONS, SDK_INFO
from warden_sdk.serializer import serialize
from warden_sdk.auth import verify_client
from warden_sdk.sessions import SessionFlusher
from warden_sdk.envelope import Envelope
from warden_sdk.tracing_utils import (
    has_tracestate_enabled,
    reinflate_tracestate,
)

from typing import (
    Union,
    List,
    Optional,
)

_client_init_debug = ContextVar("client_init_debug")


def _get_options(*args, **kwargs):
  """Gets options from the arguments.

   Retrieves the options from the arguments passed to the function and verifies if they are the allowed options based on the `DEFAULT_OPTIONS` class in the `const.py` file.

   Args:
      *args
      **kwargs

   Returns:
      A dict mapping keys to the corresponding args data fetched. Each option points of the corresponding argument passed For example:

      {
         'creds': {'client_id': '','client_secret': ''},
         'service': 'clerk',
         'api': 'datastore',
         'scopes': ['scope.1'],
         'integrations': [FlaskIntegration()]
      }

   Raises:
      TypeError: Unknown option was passed.
   """
  if args and (isinstance(args[0], (text_type, bytes, str)) or args[0] is None):
    dsn = args[0]    # type: Optional[str]
    args = args[1:]
  else:
    dsn = None

  if len(args) > 1:
    raise TypeError("Only single positional argument is expected")

  rv = dict(DEFAULT_OPTIONS)
  options = dict(*args, **kwargs)
  if dsn is not None and options.get("dsn") is None:
    options["dsn"] = dsn

  if rv["release"] is None:
    rv["release"] = get_default_release()

  if rv["environment"] is None:
    rv["environment"] = os.environ.get("WARDEN_ENVIRONMENT") or "production"

  for key, value in iteritems(options):
    if key not in rv:
      raise TypeError("Unknown option %r" % (key,))

    if key == 'creds':
      if not isinstance(value, dict):
        raise TypeError("`creds` is not a dictionary.")
      if ['client_id', 'client_secret'] != list(value.keys()):
        raise TypeError(
            "`creds` is missing either `client_id` or `client_secret`")
      if value['client_id'] == '' or value['client_secret'] == '':
        raise TypeError(
            "`creds` is missing either `client_id` or `client_secret`")

    if key == 'environment':
      value = value.lower()
      _env_types: List[str] = [
          'dev', 'development', 'prod', 'production', 'testing'
      ]
      if not any(value == _env_type for _env_type in _env_types):
        logger.warning(
            f'Environment type is not accepted. Use one of the following: \n {_env_types}'
        )

    if key == 'scopes':
      if value == [] or len(value) == 0:
        raise TypeError("Missing `scopes`")

    if key == 'service' or key == 'api':
      if value == '':
        raise TypeError(f"Missing `{key}`")

    # if rv["dsn"] is None:
    #     rv["dsn"] = os.environ.get("WARDEN_DSN")

    if rv["release"] is None:
      rv["release"] = get_default_release()

    if rv["environment"] is None:
      rv["environment"] = os.environ.get("WARDEN_ENVIRONMENT") or "production"

    if rv["server_name"] is None and hasattr(socket, "gethostname"):
      rv["server_name"] = socket.gethostname()

    rv[key] = value

  return rv


class _Client(object):
  """Client class controls all actions of `warden_sdk`.

   Client class setups the authentication to verify whether the API is registered correctly with a point-of-contact to 'blame' and refer to for information (project manager). Also setups up required integrations for logging such as `LoggingIntegration', 'ExcepthookIntegration', and 'FlaskIntegration'.

   This class also has a `self.captured` variable where all captured events are 'queued' and once the program exits, it runs `self.flush` in order to submit all captured events.

   Attributes:
      options: A dictionary containing all of the data when initialized to be used to verify and log events.
    """

  captured = []

  def __init__(self, *args, **kwargs) -> None:
    self.options = _get_options(*args, **kwargs)
    self._init_impl()

  def __getstate__(self):
    return {"options": self.options}

  def __setstate__(self, state):
    self.options = state["options"]
    self._init_impl()

  def _init_impl(self):
    old_debug = _client_init_debug.get(False)

    def _capture_envelope(envelope):
      # type: (Envelope) -> None
      if self.transport is not None:
        self.transport.capture_envelope(envelope)

    try:
      _client_init_debug.set(self.options["debug"])
      # verify_client(self.options)
      self.transport = make_transport(self.options)

      self.session_flusher = SessionFlusher(capture_func=_capture_envelope)

      request_bodies = ("always", "never", "small", "medium")
      if self.options["request_bodies"] not in request_bodies:
        raise ValueError(
            "Invalid value for request_bodies. Must be one of {}".format(
                request_bodies))

      self.integrations = setup_integrations(
          self.options["integrations"],
          with_defaults=self.options["default_integrations"],
          with_auto_enabling_integrations=self.
          options["auto_enabling_integrations"],
      )
    finally:
      _client_init_debug.set(old_debug)

  def capture_event(
      self,
      event,
      hint=None,    # type: ignore
      scope=None,
  ):
    """Captures an event.
    
    :param event: A ready-made event that can be directly sent to Warden.
    :param hint: Contains metadata about the event that can be read from `before_send`, such as the original exception object or a HTTP request object.
    
    :returns: An event ID. May be `None` if there is no DSN set or of if the SDK decided to discard the event for other reasons. In such situations setting `debug=True` on `init()` may help.
    """
    if disable_capture_event.get(False):
      return None

    if self.transport is None:
      return None
    if hint is None:
      hint = {}
    event_id = event.get("event_id")
    hint = dict(hint or ())

    if event_id is None:
      event["event_id"] = event_id = uuid.uuid4().hex
    if not self._should_capture(event, hint, scope):
      return None

    event_opt = self._prepare_event(event, hint, scope)
    if event_opt is None:
      return None

    # whenever we capture an event we also check if the session needs
    # to be updated based on that information.
    session = scope._session if scope else None
    if session:
      self._update_session_from_event(session, event)

    is_transaction = event_opt.get("type") == "transaction"

    if not is_transaction and not self._should_sample_error(event):
      return None

    attachments = hint.get("attachments")

    # this is outside of the `if` immediately below because even if we don't
    # use the value, we want to make sure we remove it before the event is
    # sent
    raw_tracestate = (event_opt.get(
        "contexts",
        {},
    ).get(
        "trace",
        {},
    ).pop(
        "tracestate",
        "",
    ))

    dynamic_sampling_context = (event_opt.get(
        "contexts",
        {},
    ).get(
        "trace",
        {},
    ).pop(
        "dynamic_sampling_context",
        {},
    ))

    # Transactions or events with attachments should go to the /envelope/
    # endpoint.
    if is_transaction or attachments:

      headers = {
          "event_id": event_opt["event_id"],
          "sent_at": format_timestamp(datetime.utcnow()),
          "level": event_opt.get("level", "info")
      }

      if has_tracestate_enabled():
        tracestate_data = raw_tracestate and reinflate_tracestate(
            raw_tracestate.replace("sentry=", ""))

        if tracestate_data:
          headers["trace"] = tracestate_data
      elif dynamic_sampling_context:
        headers["trace"] = dynamic_sampling_context

      # Transactions or events with attachments should go to the
      # /envelope/ endpoint.
      envelope = Envelope(headers=headers)

      if is_transaction:
        envelope.add_transaction(event_opt)
      else:
        envelope.add_event(event_opt)

      for attachment in attachments or ():
        envelope.add_item(attachment.to_envelope_item())

      self.transport.capture_envelope(envelope)
      self.captured.append(envelope)
    else:
      # All other events go to the /store/ endpoint.
      self.transport.capture_event(event_opt)

    return event_id

  def _should_capture(
      self,
      event,
      hint,
      scope=None,
  ):
    # Transactions are sampled independent of error events.
    is_transaction = event.get("type") == "transaction"
    if is_transaction:
      return True

    ignoring_prevents_recursion = scope is not None and not scope._should_capture
    if ignoring_prevents_recursion:
      return False

    ignored_by_config_option = self._is_ignored_error(event, hint)
    if ignored_by_config_option:
      return False

    return True

  def _is_ignored_error(self, event, hint):
    exc_info = hint.get("exc_info")
    if exc_info is None:
      return False

    error = exc_info[0]
    error_type_name = get_type_name(exc_info[0])
    error_full_name = "%s.%s" % (exc_info[0].__module__, error_type_name)

    for ignored_error in self.options["ignore_errors"]:
      # String types are matched against the type name in the
      # exception only
      if isinstance(ignored_error, string_types):
        if ignored_error == error_full_name or ignored_error == error_type_name:
          return True
      else:
        if issubclass(error, ignored_error):
          return True

    return False

  def _should_sample_error(
      self,
      event,
  ):
    not_in_sample_rate = (self.options["sample_rate"] < 1.0
                          and random.random() >= self.options["sample_rate"])
    if not_in_sample_rate:
      # because we will not sample this event, record a "lost event".
      if self.transport:
        self.transport.record_lost_event("sample_rate", data_category="error")

      return False

    return True

  def _update_session_from_event(
      self,
      session,
      event,
  ):
    crashed = False
    errored = False
    user_agent = None

    exceptions = (event.get("exception") or {}).get("values")
    if exceptions:
      errored = True
      for error in exceptions:
        mechanism = error.get("mechanism")
        if mechanism and mechanism.get("handled") is False:
          crashed = True
          break

    user = event.get("user")

    if session.user_agent is None:
      headers = (event.get("request") or {}).get("headers")
      for (k, v) in iteritems(headers or {}):
        if k.lower() == "user-agent":
          user_agent = v
          break

    session.update(
        status="crashed" if crashed else None,
        user=user,
        user_agent=user_agent,
        errors=session.errors + (errored or crashed),
    )

  def capture_session(
      self,
      session    # type: Session
  ):
    # type: (...) -> None
    if not session.release:
      logger.info("Discarded session update because of missing release")
    else:
      self.session_flusher.add_session(session)

  def get_captured(self):
    return self.captured

  def set_test_user(self,
                    user_fid: Optional[str] = None,
                    user_scope: Optional[Union[str, List[str]]] = None) -> bool:
    """
      Set the test user for testing APIs, at the same time setting options.debug
      to true for comprehensive debugging.

      To turn off debug, use the `debug()` function.
      """
    self.options['debug'] = True
    logging.warn(f'System set DEBUG to: {self.options["debug"]}')

    if user_fid is None or user_scope is None:
      logging.warn(f'Test user cannot be setup. DEBUG mode is turned off')
      self.options['debug'] = False
      return self.options['debug']

    self.options['user_fid'] = user_fid
    self.options['user_scope'] = user_scope

    logging.warn(f'Test user setup: "user_fid": {self.options["user_fid"]}')
    return self.options['debug']

  def debug(self, val: Optional[bool] = None) -> bool:
    """f
      Returns the value of options.debug and if `val` is a boolean, it sets the 
      property of options.debug.
      """
    if val is not None:
      self.options['debug'] = val

    return self.options['debug']

  def env(self, env: Optional[str] = None) -> str:
    """
      Returns the value of options.debug and if `val` is a boolean, it sets the 
      property of options.debug.
      """
    if env is not None:
      env = env.lower()
      _env_types: List[str] = ['dev', 'development', 'prod', 'production']
      if any(env == _env_type for _env_type in _env_types):
        self.options['environment'] = env
      else:
        raise Exception(
            f'Environment type is not accepted. Use one of the following: \n {_env_types}'
        )

    _dev_types: List[str] = ['dev', 'development']
    if any(
        self.options['environment'] == _env_type for _env_type in _dev_types):
      return 'dev'

    _prod_types: List[str] = ['prod', 'production']
    if any(
        self.options['environment'] == _env_type for _env_type in _prod_types):
      return 'prod'

    return self.options['environment']

  def _prepare_event(
      self,
      event,
      hint,
      scope,
  ) -> Optional[dict]:
    if event.get("timestamp") is None:
      event["timestamp"] = datetime.utcnow()

    if scope is not None:
      is_transaction = event.get("type") == "transaction"
      event_ = scope.apply_to_event(event, hint)

      # one of the event/error processors returned None
      if event_ is None:
        if self.transport:
          self.transport.record_lost_event(
              "event_processor",
              data_category=("transaction" if is_transaction else "error"),
          )
        return None

      event = event_

    if (self.options["attach_stacktrace"] and "exception" not in event
        and "stacktrace" not in event and "threads" not in event):
      with capture_internal_exceptions():
        event["threads"] = {
            "values": [{
                "stacktrace": current_stacktrace(self.options["with_locals"]),
                "crashed": False,
                "current": True,
            }]
        }

    for key in "release", "environment", "server_name", "dist":
      if event.get(key) is None and self.options[key] is not None:
        event[key] = text_type(self.options[key]).strip()
    if event.get("sdk") is None:
      sdk_info = dict(SDK_INFO)
      sdk_info["integrations"] = sorted(self.integrations.keys())
      event["sdk"] = sdk_info

    if event.get("platform") is None:
      event["platform"] = "python"

    event = handle_in_app(
        event,
        self.options["in_app_exclude"],
        self.options["in_app_include"],
    )

    # Postprocess the event here so that annotated types do
    # generally not surface in before_send
    if event is not None:
      event = serialize(
          event,
          smart_transaction_trimming=self.options["_experiments"].get(
              "smart_transaction_trimming"),
      )

    before_send = self.options["before_send"]
    if before_send is not None and event.get("type") != "transaction":
      new_event = None
      with capture_internal_exceptions():
        new_event = before_send(event, hint or {})
      if new_event is None:
        logger.info("before send dropped event (%s)", event)
        if self.transport:
          self.transport.record_lost_event(
              "before_send",
              data_category="error",
          )
      event = new_event    # type: ignore

    return event

  # def __iter__(self):
  #    return iter(self.captured)

  def close(
      self,
      timeout=None,
      callback=None,
  ) -> None:
    """
    Close the client and shut down the transport. Arguments have the same
    semantics as :py:meth:`Client.flush`.
    """
    if self.transport is not None:
      self.flush(timeout=timeout, callback=callback)
      self.session_flusher.kill()
      self.transport.kill()
      self.transport = None

  def flush(
      self,
      timeout=None,
      callback=None,
  ) -> None:
    """Send the final results collected."""
    if self.transport is not None:
      if timeout is None:
        timeout = self.options["shutdown_timeout"]
      self.session_flusher.flush()
      self.transport.flush(timeout=timeout, callback=callback)

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, tb):
    self.close()


Client = (lambda: _Client)()
