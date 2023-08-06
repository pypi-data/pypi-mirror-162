"""File containing all of the constants for the sdk.

  Typical usage example:

  from warden_sdk.consts import 
  bar = foo.FunctionBar()
  
Code reference:
- [sentry_sdk](https://github.com/getsentry/sentry-python/blob/master/sentry_sdk/consts.py)
"""

from inspect import ArgSpec, FullArgSpec
from typing import (
    Callable,
    Union,
    Optional,
    List,
    Any,
    Literal,
)

DEFAULT_QUEUE_SIZE: Literal[100] = 100
DEFAULT_MAX_BREADCRUMBS: Literal[100] = 100


class ClientConstructor(object):
  """Client Constructor is a base class for the default options allowed.
   """

  def __init__(
      self,
      integrations: list = [],    # type: Sequence[Integration]  # noqa: B006
      creds: dict[str, Any] = {
          'client_id': '',
          'client_secret': '',
      },
      service: str = '',
      api: str = '',
      scopes: Union[list, str] = [],
    # flask: bool = True
      with_locals: bool = True,
      max_breadcrumbs: int = DEFAULT_MAX_BREADCRUMBS,
      release: Optional[str] = None,
      environment: Optional[str] = None,
      server_name: Optional[str] = None,
      shutdown_timeout: int = 2,
      in_app_include: List[str] = [],    # noqa: B006
      in_app_exclude: List[str] = [],    # noqa: B006
      default_integrations: bool = True,
      dist: Optional[str] = None,
      transport=None,
      transport_queue_size: int = DEFAULT_QUEUE_SIZE,
      sample_rate: float = 1.0,
      send_default_pii: bool = False,
      http_proxy: Optional[str] = None,
      https_proxy: Optional[str] = None,
      ignore_errors: List[Union[type, str]] = [],    # noqa: B006
      request_bodies: str = "medium",
      before_send=None,
      before_breadcrumb=None,
      debug: bool = False,
      attach_stacktrace: bool = False,
      ca_certs: Optional[str] = None,
      propagate_traces: bool = True,
      traces_sample_rate: Optional[float] = None,
      traces_sampler=None,
      auto_enabling_integrations: bool = True,
      auto_session_tracking: bool = True,
      _experiments={},
      user_fid: Optional[str] = None,
      user_scope: Optional[str] = None,
      chatty: bool = True,
  ) -> None:
    pass


def __get_default_options() -> dict[str, Any]:
  import inspect

  if hasattr(inspect, "getfullargspec"):
    getargspec: Callable = inspect.getfullargspec
  else:
    getargspec: Callable = inspect.getargspec

  a: Union[FullArgSpec, ArgSpec] = getargspec(ClientConstructor.__init__)
  defaults: Union[tuple[Any, ...], tuple[()]] = a.defaults or ()
  return dict(zip(a.args[-len(defaults):], defaults))


DEFAULT_OPTIONS: dict[str, Any] = __get_default_options()


def WARDEN_LOGGING_API_LINK(env=None) -> str:
  if env == None:
    raise Exception('Environment has not be set.')

  if env.lower() == 'development' or env.lower() == 'dev':
    return "https://dev-api.warden.ferant.io/log"
  elif env.lower() == 'production' or env.lower() == 'prod':
    return "https://api.warden.ferant.io/log"
  else:
    _env_types: List[str] = ['dev', 'development', 'prod', 'production']
    raise Exception(
        f'Environment type is not accepted. Use one of the following: \n {_env_types}'
    )


VERSION: str = "2.3.0"
SDK_INFO: dict[str, Any] = {
    "name": "warden.python",
    "version": VERSION,
    "packages": [{
        "name": "pypi:warden-sdk",
        "version": VERSION
    }],
}

TABLES = {
    'users': {
        'table_name': 'ferant-users',
        'primary_key': 'fid',
        'sort_key': ''
    },
    'settings': {
        'table_name': 'ferant-settings',
        'primary_key': 'fid',
        'sort_key': 'item'
    },
    'usersEmail': {
        'table_name': 'ferant-users',
        'indexKey': 'email-index',
        'primary_key': 'email',
        'sort_key': ''
    },
    'integration-accounts': {
        'table_name': 'integration-accounts',
        'region': '',
        'primary_key': 'productId',
        'sort_key': 'clientId'
    },
}
