"""User class to maintain state and user information.

The User module allows us to collect all of the relevant information for a user and allow the system to access the relevant information about a User that necessary to propagate internally for clear understanding of what's going on with the system.
"""
from warden_sdk.hub import Hub
from warden_sdk.utils import (get_options, logger, get_user, DotDict)
# from warden_sdk.integrations.flask import FlaskIntegration
from warden_sdk.integrations.awslambda import AwsLambdaIntegration

from typing import (Any, Optional, List)


class _User(object):
  """User class contains all information about the requester.
   """
  fid: str
  details: Any
  __scope: list
  __permission: Optional[list] = None

  def __init__(self) -> None:
    pass

  def setup(self, request: Any) -> None:
    hub = Hub.current
    client = hub.client
    options = get_options(client.options)

    # flask_integration = hub.get_integration(FlaskIntegration)
    aws_integration = hub.get_integration(AwsLambdaIntegration)

    if options['debug']:
      if options['user_fid'] is None or options['user_scope'] is None:
        logger.warning(
            'User cannot be setup. Missing parameters: user_fid or user_scope')
        return

    # TODO(MP): ugly and complex section. Need to fix-up how we can debug
    #  the API without having to turn it off... Can we simulate another
    #  User? Should be included in the `options`... Let's try.
    __context = None
    if options['debug']:
      logger.info(f"Setting up proto-user for debugging: {options['user_fid']}")
      self.fid = options['user_fid']
      self.scope = options['user_scope']
    else:
      if aws_integration:
        __context = request.environ['serverless.event']['requestContext'][
            'authorizer']

        self.fid = __context['fid']
        self.scope = __context['scope']
      else:
        if options['user_fid'] is None or options['user_scope'] is None:
          raise ValueError('Missing user_fid or user_scope')
        self.fid = options['user_fid']
        self.scope = options['user_scope']

    user: Optional[Any] = get_user(self.fid)
    if user is None:
      raise ValueError('Requesting user does not exist')

    self.details = DotDict(user)

    # permgroups = user['permission_groups']
    # userPermissionsList = getUserPermissions(permgroups)
    # verify_perms(userPermissionsList, ScopeGuard.permissions)

    if options['scopes'] is None:
      raise ValueError('Missing scopes.')

    # Check user scopes against the API general scopes.
    self.verify_scopes(options['scopes'])

    # self.__get_permissions()

  @property
  def scope(self) -> List[str]:
    return self.__scope

  @scope.setter
  def scope(self, scope) -> None:
    try:
      self.__scope = scope.split(' ')
    except:
      self.__scope = scope

  def verify_scopes(self, scopes: List[str]) -> bool:
    '''Check if the user has permitting scopes for the action.
    
    If the scope isn't present in the user's scopes, the app will be abruptly 
    ended through a raised exception.

    Args:
        scopes (List[str]): List of scopes to verify against

    Raises:
        Exception: If the scope isn't present, an exception is raised.

    Returns:
        bool: If `True`, scopes are verified.
    '''
    if not any(scope in self.scope for scope in scopes):
      raise Exception({
          'error': 'invalid_request',
          'error_description': 'Invalid scopes.'
      })

    return True

  # START: Not implemented yet
  @property
  def permission(self) -> Optional[list]:
    return self.__permission

  @permission.setter
  def permission(self, perms):
    self.__permission = perms

  def verify_permissions(self, perms) -> bool:
    # TODO
    raise NotImplementedError
    if not any(permission in self.permission for permission in perms):
      raise Exception({
          'error': 'invalid_request',
          'error_description': 'Invalid permissions.'
      })

    return True


User = (lambda: _User)()
