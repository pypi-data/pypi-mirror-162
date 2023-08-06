"""OAuth2 class handler.

This module contains all the necessary functionality and class to verify the JWT coming in using the OAuth2 policy.
"""
import json
import requests

from typing import (Any, Optional)

from warden_sdk.auth.exceptions import JWT


class OAuth2(object):
  """
   TODO(MP): document the class
   """

  def __init__(self) -> None:
    self.__payload: dict[Any, Any] = {}

  def verify(self, token: str) -> None:
    """
      Verify method verifies the token by sending it to the backend for Warden to access a private database to request a Public key for the token to verify it's signature IF the token passes the other verifications. If the token is valid and authentic, the method does not return anything. If the token is invalid, the method will raise an error and prevent the API from continuing.

      Args::
         token (str):

      Raises::
         InvalidToken
      """
    resp: Any = requests.get('https://api.warden_sdk.ferant.io/oauth2/v1/auth',
                             headers={'Authorization': 'Bearer ' + token})

    if 'error' in resp.keys():
      raise JWT.InvalidToken

    self.__payload = resp if type(resp) == dict else json.loads(resp)

  @property
  def payload(self) -> Optional[Any]:
    return self.__payload

  @property
  def scopes(self) -> Optional[Any]:
    return self.__payload['scopes']

  # @staticmethod
  def refresh(self, token: str) -> str:
    resp: Any = requests.post(
        'https://api.warden_sdk.ferant.io/oauth2/v1/refresh',
        headers={'Authorization': 'Bearer ' + token},
    )

    return resp
