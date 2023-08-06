from __future__ import absolute_import

from warden_sdk import Hub
from warden_sdk.integrations import Integration, DidNotEnable
from warden_sdk.scope import add_global_event_processor
from warden_sdk.utils import walk_exception_chain, iter_stacks

try:
  import executing
except ImportError:
  raise DidNotEnable("executing is not installed")


class ExecutingIntegration(Integration):
  identifier = "executing"

  @staticmethod
  def setup_once():

    @add_global_event_processor
    def add_executing_info(event, hint):
      if Hub.current.get_integration(ExecutingIntegration) is None:
        return event

      if hint is None:
        return event

      exc_info = hint.get("exc_info", None)

      if exc_info is None:
        return event

      exception = event.get("exception", None)

      if exception is None:
        return event

      values = exception.get("values", None)

      if values is None:
        return event

      for exception, (_exc_type, _exc_value,
                      exc_tb) in zip(reversed(values),
                                     walk_exception_chain(exc_info)):
        warden_frames = [
            frame
            for frame in exception.get("stacktrace", {}).get("frames", [])
            if frame.get("function")
        ]
        tbs = list(iter_stacks(exc_tb))
        if len(warden_frames) != len(tbs):
          continue

        for warden_frame, tb in zip(warden_frames, tbs):
          frame = tb.tb_frame
          source = executing.Source.for_frame(frame)
          warden_frame["function"] = source.code_qualname(frame.f_code)

      return event
