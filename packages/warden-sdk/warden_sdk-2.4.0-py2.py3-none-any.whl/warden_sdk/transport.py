"""Transport module sends all of the queued data in `warden_sdk`.

TODO(MP): document
"""
from __future__ import print_function

import io
import gzip
# pylint: disable=import-error
import requests
import time

from datetime import datetime, timedelta
from collections import defaultdict

from warden_sdk.utils import logger, json_dumps, capture_internal_exceptions
from warden_sdk.consts import WARDEN_LOGGING_API_LINK, VERSION
from warden_sdk.worker import BackgroundWorker
from warden_sdk.envelope import Envelope, Item, PayloadRef

from typing import (
    Dict,
    Optional,
    Any,
    Type,
)


class Transport(object):
  """Baseclass for all transports.

   A transport is used to send an event to warden_sdk.
   """

  def __init__(self, options=None):
    self.options = options

  def capture_event(self, event):
    """
      This gets invoked with the event dictionary when an event should
      be sent to warden.
      """
    raise NotImplementedError()

  def capture_envelope(self, envelope):
    """
      Send an envelope to Warden.
      Envelopes are a data container format that can hold any type of data
      submitted to Warden. We use it for transactions and sessions, but
      regular "error" events should go through `capture_event` for backwards
      compat.
      """
    raise NotImplementedError()

  def flush(
      self,
      timeout,
      callback=None,
  ):
    """Wait `timeout` seconds for the current events to be sent out."""
    pass

  def kill(self):
    """Forcefully kills the transport."""
    pass

  def record_lost_event(
      self,
      reason,
      data_category=None,
      item=None,
  ):
    """This increments a counter for event loss by reason and
      data category.
      """
    return None

  def __del__(self):
    try:
      self.kill()
    except Exception:
      pass


def _parse_rate_limits(header, now=None):
  if now is None:
    now = datetime.utcnow()

  for limit in header.split(","):
    try:
      retry_after, categories, _ = limit.strip().split(":", 2)
      retry_after = now + timedelta(seconds=int(retry_after))
      for category in categories and categories.split(";") or (None,):
        yield category, retry_after
    except (LookupError, ValueError):
      continue


class HttpTransport(Transport):
  """The default HTTP transport."""

  def __init__(self, options):
    Transport.__init__(self, options)
    self.options = options
    self._worker = BackgroundWorker(queue_size=options["transport_queue_size"])
    self._disabled_until = {}
    self._discarded_events = defaultdict(int)
    self._last_client_report_sent = time.time()

    from warden_sdk import Hub

    self.hub_cls = Hub

  def _send_request(
      self,
      body: bytes,
      headers: Dict[str, str],
      endpoint_type="store",
      envelope=None,
  ) -> None:

    def record_loss(reason):
      if envelope is None:
        self.record_lost_event(reason, data_category="error")
      else:
        for item in envelope.items:
          self.record_lost_event(reason, item=item)

    # TODO(MP): add authentication headers to logging
    headers.update({
        "User-Agent":
            str("warden.python/%s" % VERSION),
        "X-Warden-Auth":
            f"Warden warden_client={self.options['creds']['client_id']}, warden_secret={self.options['creds']['client_secret']}",
    })
    try:
      url = self.options["dsn"]
      if url is None:
        url = WARDEN_LOGGING_API_LINK(self.options['environment'])

      if url[-3] != 'log':
        url = f'{url}/log'

      response = requests.post(
          url,
          data=body,
          headers=headers,
      )
    except Exception as e:
      self.on_dropped_event("network")
      record_loss("network_error")
      raise e

    try:
      self._update_rate_limits(response)

      if response.status_code == 429:
        # if we hit a 429.  Something was rate limited but we already
        # acted on this in `self._update_rate_limits`.  Note that we
        # do not want to record event loss here as we will have recorded
        # an outcome in relay already.
        self.on_dropped_event("status_429")
        pass

      elif response.status_code >= 300 or response.status_code < 200:
        logger.error(
            "Unexpected status code: %s (body: %s)",
            response.status_code,
            response.raw,
        )
        self.on_dropped_event("status_{}".format(response.status_code))
        record_loss("network_error")
    finally:
      response.close()

  def on_dropped_event(self, reason):
    # type: (str) -> None
    return None

  def _check_disabled(self, category: str) -> bool:

    def _disabled(bucket: Any) -> bool:
      ts = self._disabled_until.get(bucket)
      return ts is not None and ts > datetime.utcnow()

    return _disabled(category) or _disabled(None)

  def _send_event(self, event) -> None:
    if self._check_disabled("error"):
      self.on_dropped_event("self_rate_limits")
      self.record_lost_event("ratelimit_backoff", data_category="error")
      return None

    body = io.BytesIO()
    with gzip.GzipFile(fileobj=body, mode="w") as f:
      f.write(json_dumps(event))

    logger.debug("Sending event, type:%s level:%s event_id:%s" % (
        event.get("type") or "null",
        event.get("level") or "null",
        event.get("event_id") or "null",
    ))
    self._send_request(
        body.getvalue(),
        headers={
            "Content-Type": "application/json",
            "Content-Encoding": "gzip"
        },
    )
    return None

  def _send_envelope(self, envelope):
    # remove all items from the envelope which are over quota
    new_items = []
    for item in envelope.items:
      if self._check_disabled(item.data_category):
        if item.data_category in ("transaction", "error", "default"):
          self.on_dropped_event("self_rate_limits")
        self.record_lost_event("ratelimit_backoff", item=item)
      else:
        new_items.append(item)

    # Since we're modifying the envelope here make a copy so that others
    # that hold references do not see their envelope modified.
    envelope = Envelope(headers=envelope.headers, items=new_items)

    # envelope.items[:] = [x for x in envelope.items]
    if not envelope.items:
      return None

    # since we're already in the business of sending out an envelope here
    # check if we have one pending for the stats session envelopes so we
    # can attach it to this enveloped scheduled for sending.  This will
    # currently typically attach the client report to the most recent
    # session update.
    client_report_item = self._fetch_pending_client_report(interval=30)
    if client_report_item is not None:
      envelope.items.append(client_report_item)

    body = io.BytesIO()
    with gzip.GzipFile(fileobj=body, mode="w") as f:
      envelope.serialize_into(f)

    self._send_request(
        body.getvalue(),
        headers={
            "Content-Type": "application/json",
            "Content-Encoding": "gzip",
        },
        endpoint_type="envelope",
        envelope=envelope,
    )
    return None

  def capture_event(self, event) -> None:
    hub = self.hub_cls.current

    def send_event_wrapper() -> None:
      with hub:
        with capture_internal_exceptions():
          self._send_event(event)
          self._flush_client_reports()

    if not self._worker.submit(send_event_wrapper):
      self.on_dropped_event("full_queue")
      self.record_lost_event("queue_overflow", data_category="error")

  def capture_envelope(self, envelope):
    hub = self.hub_cls.current

    def send_envelope_wrapper() -> None:
      with hub:
        with capture_internal_exceptions():
          self._send_envelope(envelope)
          self._flush_client_reports()

    if not self._worker.submit(send_envelope_wrapper):
      self.on_dropped_event("full_queue")
      for item in envelope.items:
        self.record_lost_event("queue_overflow", item=item)

  def flush(
      self,
      timeout,
      callback=None,
  ) -> None:
    logger.debug("Flushing HTTP transport")

    if timeout > 0:
      self._worker.submit(lambda: self._flush_client_reports(force=True))
      self._worker.flush(timeout, callback)

  def _fetch_pending_client_report(self, force=False, interval=60):
    if not self.options["send_client_reports"]:
      return None

    if not (force or self._last_client_report_sent < time.time() - interval):
      return None

    discarded_events = self._discarded_events
    self._discarded_events = defaultdict(int)
    self._last_client_report_sent = time.time()

    if not discarded_events:
      return None

    return Item(
        PayloadRef(
            json={
                "timestamp":
                    time.time(),
                "discarded_events": [{
                    "reason": reason,
                    "category": category,
                    "quantity": quantity
                } for (
                    (category, reason),
                    quantity,
                ) in discarded_events.items()],
            }),
        type="client_report",
    )

  def _flush_client_reports(self, force=False):
    client_report = self._fetch_pending_client_report(force=force, interval=60)
    if client_report is not None:
      self.capture_envelope(Envelope(items=[client_report]))

  def record_lost_event(
      self,
      reason,
      data_category=None,
      item=None,
  ):
    if not self.options["send_client_reports"]:
      return

    quantity = 1
    if item is not None:
      data_category = item.data_category
      if data_category == "attachment":
        # quantity of 0 is actually 1 as we do not want to count
        # empty attachments as actually empty.
        quantity = len(item.get_bytes()) or 1
    elif data_category is None:
      raise TypeError("data category not provided")

    self._discarded_events[data_category, reason] += quantity

  def _update_rate_limits(self, response: requests.Response):
    # new sentries with more rate limit insights.  We honor this header
    # no matter of the status code to update our internal rate limits.
    header = response.headers.get("x-warden-rate-limits")
    if header:
      logger.warning("Rate-limited via x-warden-rate-limits")
      self._disabled_until.update(_parse_rate_limits(header))

      # old sentries only communicate global rate limit hits via the
      # retry-after header on 429.  This header can also be emitted on new
      # sentries if a proxy in front wants to globally slow things down.
    elif response.status_code == 429:
      logger.warning("Rate-limited via 429")
      self._disabled_until[None] = datetime.utcnow() + timedelta(seconds=60)

  def kill(self):
    logger.debug("Killing HTTP transport")
    self._worker.kill()


class _FunctionTransport(Transport):

  def __init__(
      self,
      func    # type: Callable[[Event], None]
  ) -> None:
    Transport.__init__(self)
    self._func = func

  def capture_event(
      self,
      event    # type: Event
  ) -> None:
    self._func(event)
    return None


def make_transport(options: Dict[str, Any]) -> Optional[Transport]:
  ref_transport = options["transport"]    # This will be none for now!

  if ref_transport is None:
    transport_cls: Type[Transport] = HttpTransport
  elif isinstance(ref_transport, Transport):
    return ref_transport
  elif isinstance(ref_transport, type) and issubclass(ref_transport, Transport):
    transport_cls = ref_transport
  elif callable(ref_transport):
    return _FunctionTransport(ref_transport)    # type: ignore

  if options['creds']['client_id'] and options['creds']['client_secret']:
    return transport_cls(options)    # type: ignore

  return None
