"""User class to maintain state and user information.

The User module allows us to collect all of the relevant information for a user and allow the system to access the relevant information about a User that necessary to propagate internally for clear understanding of what's going on with the system.
"""
import sys

from warden_sdk import User
from warden_sdk.hub import Hub
from warden_sdk.client import Client
from warden_sdk.utils import (reraise, event_from_exception)

from typing import (Any, Callable, Optional, Type, List)


class _ScopeGuard(object):
  """ScopeGuard class contains all information about the requester.
    """

  def __init__(self) -> None:
    pass

  @classmethod
  def verify(
      cls,
      scopes: List[str],
      perms: Optional[list] = None,
  ) -> Callable:

    def decorator(function) -> Callable:

      def wrapper(*args, **kwargs) -> Any:
        hub: Hub = Hub.current
        client: Optional[Client] = hub.client
        if client is None:
          return

        try:
          # User.verify_permissions(perms)
          User.verify_scopes(scopes)
        except Exception:
          exc_info: sys._OptExcInfo = sys.exc_info()
          warden_event, hint = event_from_exception(
              exc_info,
              client_options=client.options,
              mechanism={
                  "type": "flask",
                  "handled": False
              },
          )
          hub.capture_event(warden_event, hint=hint)
          reraise(*exc_info)

        return function(*args, **kwargs)

      return wrapper

    return decorator


ScopeGuard: Type[_ScopeGuard] = (lambda: _ScopeGuard)()
