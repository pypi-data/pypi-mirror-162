"""Utility functions used to simplify redundant work across the SDK.

Code reference:
- [sentry_sdk](https://github.com/getsentry/sentry-python/blob/master/sentry_sdk/utils.py)
"""
import linecache
import json
import logging
import sys
import threading
import os
import traceback

from datetime import datetime
from typing import (Union, Optional, Any, Dict, Type, ContextManager, Tuple,
                    List, TypeVar, Iterator, NoReturn)
from types import (FrameType, TracebackType)

import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr

from dotenv import load_dotenv

load_dotenv()

from warden_sdk.consts import (DEFAULT_OPTIONS, TABLES)

epoch: datetime = datetime(1970, 1, 1)

# The logger is created here but initialized in the debug support module
logger: logging.Logger = logging.getLogger("warden_sdk.errors")

text_type = str
string_types = (text_type,)
number_types = (int, float)

MAX_STRING_LENGTH = 512
MAX_FORMAT_PARAM_LENGTH = 128

__region: Any = boto3.session.Session().region_name    # type: ignore
if os.getenv('ENV') == 'testing':
  dynamodb: Any = boto3.resource(
      'dynamodb',
      endpoint_url='http://localhost:4566',
  )
else:
  dynamodb: Any = boto3.resource('dynamodb')


def iteritems(x) -> Any:
  return x.items()


def json_dumps(data) -> bytes:
  """Serialize data into a compact JSON representation encoded as UTF-8."""
  return json.dumps(data, allow_nan=False,
                    separators=(",", ":")).encode("utf-8")


def get_options(options: Any) -> dict:
  rv: dict[str, Any] = dict(DEFAULT_OPTIONS)
  options = dict(options)

  for key, value in iteritems(options):
    if key not in rv:
      raise TypeError("Unknown option %r" % (key,))
    rv[key] = value

  return rv


def _get_debug_hub():
  # This function is replaced by debug.py
  pass


def reraise(tp, value, tb=None) -> NoReturn:
  assert value is not None
  if value.__traceback__ is not tb:
    raise value.with_traceback(tb)
  raise value


def _get_contextvars():
  if sys.version_info >= (3, 7):
    # On Python 3.7 context vars are functional
    from contextvars import ContextVar

    return True, ContextVar
  else:
    raise ImportError


def format_timestamp(value) -> str:
  return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


HAS_REAL_CONTEXTVARS, ContextVar = _get_contextvars()

disable_capture_event = ContextVar("disable_capture_event")


def to_timestamp(value: datetime) -> float:
  return (value - epoch).total_seconds()


def to_string(value: str) -> str:
  try:
    return text_type(value)
  except UnicodeDecodeError:
    return repr(value)[1:-1]


class ServerlessTimeoutWarning(Exception):
  """Raised when a serverless method is about to reach its timeout."""

  pass


class TimeoutThread(threading.Thread):
  """Creates a Thread which runs (sleeps) for a time duration equal to
    waiting_time and raises a custom ServerlessTimeout exception.
    """

  def __init__(self, waiting_time, configured_timeout) -> None:
    # type: (float, int) -> None
    threading.Thread.__init__(self)
    self.waiting_time = waiting_time
    self.configured_timeout = configured_timeout
    self._stop_event = threading.Event()

  def stop(self) -> None:
    self._stop_event.set()

  def run(self) -> None:
    self._stop_event.wait(self.waiting_time)

    if self._stop_event.is_set():
      return

    integer_configured_timeout = int(self.configured_timeout)

    # Setting up the exact integer value of configured time(in seconds)
    if integer_configured_timeout < self.configured_timeout:
      integer_configured_timeout = integer_configured_timeout + 1

    # Raising Exception after timeout duration is reached
    raise ServerlessTimeoutWarning(
        "WARNING : Function is expected to get timed out. Configured timeout duration = {} seconds."
        .format(integer_configured_timeout))


acceptablePrefixes = ['dev', 'qa', 'testing']


def get_table(table: str):
  """ """
  try:
    table_dict = DotDict(TABLES[table])
    if os.environ.get('ENV'):
      if os.environ.get('ENV').lower() == 'prod':
        return table_dict
      if os.environ.get('ENV').lower() in acceptablePrefixes:
        table_dict.table_name = os.environ.get(
            'ENV').lower() + '-' + table_dict.table_name
        return table_dict
    raise KeyError(
        f'ENV variable is undefined or not in acceptable prefixes:{acceptablePrefixes}'
    )
  except KeyError as reException:
    raise KeyError(f"Table '{table}' does not") from reException


def get_user(fid: str) -> Optional[Any]:
  '''
   Retrieve the details for the user from DynamoDB.
   '''
  global dynamodb
  _table_data = get_table('users')
  table = dynamodb.Table(_table_data.table_name)    # type: ignore

  # Here FID is the FID we will receive from the authorizer once I walk you through that.
  return table.get_item(Key={
      _table_data.primary_key: fid,
  })['Item']


# def getUserPermissions(groups: list):
#    '''
#    Retrieve the details for the user from DynamoDB.
#    '''
#    global dynamodb
#    table = dynamodb.Table('permission-group-name')

#    perms = []

#    for group in groups:
#       thisPerms = getGroupPermissions(group)
#       perms = list(set(perms + thisPerms))

#    return perms

# def getGroupPermissions(groupname: str):
#    '''
#    Retrieve the details for the user from DynamoDB.
#    '''
#    global dynamodb
#    table = dynamodb.Table('dev-permission-groups')

#    # Here FID is the FID we will receive from the authorizer once I walk you through that.
#    response = table.get_item(
#       Key={
#          'permission-group-name': groupname,
#       }
#    )['Item']['perms-scopes']
#    return response


class CaptureInternalException(object):
  """Capture internal exceptions.

  Class is setup to be used in a `with ...` statement. Once the `with ...` statement exits, the error is caught and sent to the `capture_internal_exception()`.
  """
  __slots__ = ()

  def __enter__(self) -> ContextManager[Any]:
    return self

  def __exit__(self, ty: Optional[Type[BaseException]],
               value: Optional[BaseException],
               tb: Optional[TracebackType]) -> bool:
    if ty is not None and value is not None:
      capture_internal_exception((ty, value, tb))

    return True


# Instantiate the CaptureInternalException
_CAPTURE_INTERNAL_EXCEPTION = CaptureInternalException()


def capture_internal_exceptions() -> ContextManager[Any]:
  return _CAPTURE_INTERNAL_EXCEPTION


def capture_internal_exception(exc_info):
  # TODO(Michael Podsiadly): send to hub to capture internal exception
  traceback.print_tb(exc_info[2])

  hub = _get_debug_hub()
  if hub is not None:
    hub._capture_internal_exception(exc_info)


def event_from_exception(
    exc_info: Union[BaseException, Any],
    client_options: Optional[Dict[str, Any]] = None,
    mechanism: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
  exc_info = exc_info_from_error(exc_info)
  hint = event_hint_with_exc_info(exc_info)
  return (
      {
          "level": "error",
          "exception": {
              "values":
                  exceptions_from_error_tuple(exc_info, client_options,
                                              mechanism)
          },
      },
      hint,
  )


def exc_info_from_error(error: Union[BaseException, Any]) -> Any:
  if isinstance(error, tuple) and len(error) == 3:
    exc_type, exc_value, tb = error
  elif isinstance(error, BaseException):
    tb = getattr(error, "__traceback__", None)
    if tb is not None:
      exc_type = type(error)
      exc_value = error
    else:
      exc_type, exc_value, tb = sys.exc_info()
      if exc_value is not error:
        tb = None
        exc_value = error
        exc_type = type(error)

  else:
    raise ValueError("Expected Exception object to report, got %s!" %
                     type(error))

  return exc_type, exc_value, tb


def event_hint_with_exc_info(
    exc_info: Optional[Any] = None) -> Dict[str, Optional[Any]]:
  """Creates a hint with the exc info filled in."""
  if exc_info is None:
    exc_info = sys.exc_info()
  else:
    exc_info = exc_info_from_error(exc_info)
  if exc_info[0] is None:
    exc_info = None
  return {"exc_info": exc_info}


def exceptions_from_error_tuple(
    exc_info,
    client_options: Optional[Dict[str, Any]] = None,
    mechanism: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
  exc_type, exc_value, tb = exc_info
  rv = []
  for exc_type, exc_value, tb in walk_exception_chain(exc_info):
    rv.append(
        single_exception_from_error_tuple(exc_type, exc_value, tb,
                                          client_options, mechanism))

  rv.reverse()

  return rv


def walk_exception_chain(exc_info):
  yield exc_info


class AnnotatedValue(object):
  __slots__ = ("value", "metadata")

  def __init__(self, value: Optional[Any], metadata: Dict[str, Any]) -> None:
    self.value = value
    self.metadata = metadata


T = TypeVar("T")
Annotated = Union[AnnotatedValue, T]


def get_lines_from_file(
    filename: str,
    lineno: int,
    loader: Optional[Any] = None,
    module: Optional[Any] = None,
) -> Tuple[List[Annotated[str]], Optional[Annotated[str]],
           List[Annotated[str]]]:
  context_lines = 5
  source = None
  if loader is not None and hasattr(loader, "get_source"):
    try:
      source_str: Optional[str] = loader.get_source(module)
    except (ImportError, IOError):
      source_str = None
    if source_str is not None:
      source = source_str.splitlines()

  if source is None:
    try:
      source = linecache.getlines(filename)
    except (OSError, IOError):
      return [], None, []

  if not source:
    return [], None, []

  lower_bound = max(0, lineno - context_lines)
  upper_bound = min(lineno + 1 + context_lines, len(source))

  try:
    pre_context = [
        strip_string(line.strip("\r\n")) for line in source[lower_bound:lineno]
    ]
    context_line = strip_string(source[lineno].strip("\r\n"))
    post_context = [
        strip_string(line.strip("\r\n"))
        for line in source[(lineno + 1):upper_bound]
    ]
    return pre_context, context_line, post_context
  except IndexError:
    # the file may have changed since it was loaded into memory
    return [], None, []


def get_source_context(
    frame: FrameType,
    tb_lineno: int,
) -> Tuple[List[Annotated[str]], Optional[Annotated[str]],
           List[Annotated[str]]]:
  try:
    abs_path: Optional[str] = frame.f_code.co_filename
  except Exception:
    abs_path = None
  try:
    module = frame.f_globals["__name__"]
  except Exception:
    return [], None, []
  try:
    loader = frame.f_globals["__loader__"]
  except Exception:
    loader = None
  lineno = tb_lineno - 1
  if lineno is not None and abs_path:
    return get_lines_from_file(abs_path, lineno, loader, module)
  return [], None, []


def serialize_frame(frame: FrameType,
                    tb_lineno: Optional[int] = None,
                    with_locals: bool = True) -> Dict[str, Any]:
  f_code = getattr(frame, "f_code", None)
  if not f_code:
    abs_path = None
    function = None
  else:
    abs_path = frame.f_code.co_filename
    function = frame.f_code.co_name
  try:
    module = frame.f_globals["__name__"]
  except Exception:
    module = None

  if tb_lineno is None:
    tb_lineno = frame.f_lineno

  pre_context, context_line, post_context = get_source_context(frame, tb_lineno)

  rv: Dict[str, Any] = {
      "filename": filename_for_module(module, abs_path) or None,
      "abs_path": os.path.abspath(abs_path) if abs_path else None,
      "function": function or "<unknown>",
      "module": module,
      "lineno": tb_lineno,
      "pre_context": pre_context,
      "context_line": context_line,
      "post_context": post_context,
  }
  if with_locals:
    rv["vars"] = frame.f_locals

  return rv


def filename_for_module(module: Optional[str],
                        abs_path: Optional[str]) -> Optional[str]:
  if not abs_path or not module:
    return abs_path

  try:
    if abs_path.endswith(".pyc"):
      abs_path = abs_path[:-1]

    base_module = module.split(".", 1)[0]
    if base_module == module:
      return os.path.basename(abs_path)

    base_module_path = sys.modules[base_module].__file__
    return abs_path.split(base_module_path.rsplit(os.sep, 2)[0],
                          1)[-1].lstrip(os.sep)
  except Exception:
    return abs_path


def get_errno(exc_value: BaseException) -> Optional[Any]:
  return getattr(exc_value, "errno", None)


def single_exception_from_error_tuple(
    exc_type: Optional[type],
    exc_value: Optional[BaseException],
    tb: Optional[TracebackType],
    client_options: Optional[Dict[str, Any]] = None,
    mechanism: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
  if exc_value is not None:
    errno = get_errno(exc_value)
  else:
    errno = None

  if errno is not None:
    mechanism = mechanism or {"type": "generic"}
    mechanism.setdefault("meta", {}).setdefault("errno",
                                                {}).setdefault("number", errno)

  if client_options is None:
    with_locals = True
  else:
    with_locals = client_options["with_locals"]

  frames = [
      serialize_frame(tb.tb_frame,
                      tb_lineno=tb.tb_lineno,
                      with_locals=with_locals) for tb in iter_stacks(tb)
  ]

  rv = {
      "module": get_type_module(exc_type),
      "type": get_type_name(exc_type),
      "value": safe_str(exc_value),
      "mechanism": mechanism,
  }

  if frames:
    rv["stacktrace"] = {"frames": frames}

  return rv


def safe_repr(value: Any) -> str:
  try:
    return repr(value)
  except Exception:
    return "<broken repr>"


def safe_str(value: Any) -> str:
  try:
    return str(value)
  except Exception:
    return safe_repr(value)


def get_type_name(cls: Optional[type]) -> Optional[str]:
  return getattr(cls, "__qualname__", None) or getattr(cls, "__name__", None)


def get_type_module(cls: Optional[type]) -> Optional[str]:
  mod = getattr(cls, "__module__", None)
  if mod not in (None, "builtins", "__builtins__"):
    return mod
  return None


def current_stacktrace(with_locals: bool = True) -> Any:
  __tracebackhide__: bool = True
  frames = []

  f: Optional[FrameType] = sys._getframe()
  while f is not None:
    if not should_hide_frame(f):
      frames.append(serialize_frame(f, with_locals=with_locals))
    f = f.f_back

  frames.reverse()

  return {"frames": frames}


def should_hide_frame(frame: FrameType) -> bool:
  try:
    mod = frame.f_globals["__name__"]
    if mod.startswith("warden_sdk."):
      return True
  except (AttributeError, KeyError):
    pass

  for flag_name in "__traceback_hide__", "__tracebackhide__":
    try:
      if frame.f_locals[flag_name]:
        return True
    except Exception:
      pass

  return False


def iter_stacks(tb: Optional[TracebackType]) -> Iterator[TracebackType]:
  tb_: Optional[TracebackType] = tb
  while tb_ is not None:
    if not should_hide_frame(tb_.tb_frame):
      yield tb_
    tb_ = tb_.tb_next


def strip_string(
    value: str, max_length: Optional[int] = None) -> Union[AnnotatedValue, str]:
  # TODO: read max_length from config
  if not value:
    return value

  if max_length is None:
    # This is intentionally not just the default such that one can patch `MAX_STRING_LENGTH` and affect `strip_string`.
    max_length = MAX_STRING_LENGTH

  length = len(value)

  if length > max_length:
    return AnnotatedValue(
        value=value[:max_length - 3] + u"...",
        metadata={
            "len": length,
            "rem": [["!limit", "x", max_length - 3, max_length]],
        },
    )
  return value


def iter_event_stacktraces(event):
  # type: (Dict[str, Any]) -> Iterator[Dict[str, Any]]
  if "stacktrace" in event:
    yield event["stacktrace"]
  if "threads" in event:
    for thread in event["threads"].get("values") or ():
      if "stacktrace" in thread:
        yield thread["stacktrace"]
  if "exception" in event:
    for exception in event["exception"].get("values") or ():
      if "stacktrace" in exception:
        yield exception["stacktrace"]


def iter_event_frames(event):
  # type: (Dict[str, Any]) -> Iterator[Dict[str, Any]]
  for stacktrace in iter_event_stacktraces(event):
    for frame in stacktrace.get("frames") or ():
      yield frame


def handle_in_app(event, in_app_exclude=None, in_app_include=None):
  # type: (Dict[str, Any], Optional[List[str]], Optional[List[str]]) -> Dict[str, Any]
  for stacktrace in iter_event_stacktraces(event):
    handle_in_app_impl(
        stacktrace.get("frames"),
        in_app_exclude=in_app_exclude,
        in_app_include=in_app_include,
    )

  return event


def handle_in_app_impl(frames, in_app_exclude, in_app_include):
  # type: (Any, Optional[List[str]], Optional[List[str]]) -> Optional[Any]
  if not frames:
    return None

  any_in_app = False
  for frame in frames:
    in_app = frame.get("in_app")
    if in_app is not None:
      if in_app:
        any_in_app = True
      continue

    module = frame.get("module")
    if not module:
      continue
    elif _module_in_set(module, in_app_include):
      frame["in_app"] = True
      any_in_app = True
    elif _module_in_set(module, in_app_exclude):
      frame["in_app"] = False

  if not any_in_app:
    for frame in frames:
      if frame.get("in_app") is None:
        frame["in_app"] = True

  return frames


def _module_in_set(name, set):
  # type: (str, Optional[List[str]]) -> bool
  if not set:
    return False
  for item in set or ():
    if item == name or name.startswith(item + "."):
      return True
  return False


class DotDict(dict):
  """dot.notation access to dictionary attributes"""

  __getattr__ = dict.get
  __setattr__ = dict.__setitem__    # type: ignore
  __delattr__ = dict.__delitem__    # type: ignore


CONTEXTVARS_ERROR_MESSAGE = """
With asyncio/ASGI applications, the Warden SDK requires a functional
installation of `contextvars` to avoid leaking scope/context data across
requests.
Please refer to https://docs.sentry.io/platforms/python/contextvars/ for more information.
"""


def transaction_from_function(func):
  # Methods in Python 2
  try:
    return "%s.%s.%s" % (
        func.im_class.__module__,    # type: ignore
        func.im_class.__name__,    # type: ignore
        func.__name__,
    )
  except Exception:
    pass

  func_qualname = (getattr(func, "__qualname__", None)
                   or getattr(func, "__name__", None)
                   or None)    # type: Optional[str]

  if not func_qualname:
    # No idea what it is
    return None

  # Methods in Python 3
  # Functions
  # Classes
  try:
    return "%s.%s" % (func.__module__, func_qualname)
  except Exception:
    pass

  # Possibly a lambda
  return func_qualname
