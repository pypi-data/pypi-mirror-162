import sys
import logging

from warden_sdk import utils
from warden_sdk.hub import Hub
from warden_sdk.utils import logger
from warden_sdk.client import _client_init_debug
from logging import LogRecord


class _HubBasedClientFilter(logging.Filter):

  def filter(self, record):
    if _client_init_debug.get(False):
      return True
    hub = Hub.current
    if hub is not None and hub.client is not None:
      return hub.client.options["debug"]
    return False


def init_debug_support():
  if not logger.handlers:
    configure_logger()
  configure_debug_hub()


def configure_logger():
  _handler = logging.StreamHandler(sys.stderr)
  _handler.setFormatter(
      logging.Formatter(" [warden] %(levelname)s: %(message)s"))
  logger.addHandler(_handler)
  logger.setLevel(logging.DEBUG)
  logger.addFilter(_HubBasedClientFilter())


def configure_debug_hub():

  def _get_debug_hub():
    return Hub.current

  utils._get_debug_hub = _get_debug_hub
