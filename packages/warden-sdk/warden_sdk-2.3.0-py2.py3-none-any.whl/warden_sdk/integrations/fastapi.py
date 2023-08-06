from warden_sdk.hub import Hub, _should_send_default_pii
from warden_sdk.integrations import DidNotEnable
from warden_sdk.integrations.starlette import (
    StarletteIntegration,
    StarletteRequestExtractor,
)
from warden_sdk.tracing import SOURCE_FOR_STYLE, TRANSACTION_SOURCE_ROUTE
from warden_sdk.utils import transaction_from_function

try:
    import fastapi  # type: ignore
except ImportError:
    raise DidNotEnable("FastAPI is not installed")


_DEFAULT_TRANSACTION_NAME = "generic FastAPI request"


class FastApiIntegration(StarletteIntegration):
    identifier = "fastapi"

    @staticmethod
    def setup_once():
        patch_get_request_handler()


def _set_transaction_name_and_source(event, transaction_style, request):
    name = ""

    if transaction_style == "endpoint":
        endpoint = request.scope.get("endpoint")
        if endpoint:
            name = transaction_from_function(endpoint) or ""

    elif transaction_style == "url":
        route = request.scope.get("route")
        if route:
            path = getattr(route, "path", None)
            if path is not None:
                name = path

    if not name:
        event["transaction"] = _DEFAULT_TRANSACTION_NAME
        event["transaction_info"] = {"source": TRANSACTION_SOURCE_ROUTE}
        return

    event["transaction"] = name
    event["transaction_info"] = {"source": SOURCE_FOR_STYLE[transaction_style]}


def patch_get_request_handler():
    old_get_request_handler = fastapi.routing.get_request_handler # type: ignore

    def _warden_get_request_handler(*args, **kwargs):
        old_app = old_get_request_handler(*args, **kwargs)

        async def _warden_app(*args, **kwargs):
            hub = Hub.current
            integration = hub.get_integration(FastApiIntegration)
            if integration is None:
                return await old_app(*args, **kwargs)

            with hub.configure_scope() as warden_scope:
                request = args[0]
                extractor = StarletteRequestExtractor(request)
                info = await extractor.extract_request_info()

                def _make_request_event_processor(req, integration):
                    def event_processor(event, hint):

                        # Extract information from request
                        request_info = event.get("request", {})
                        if info:
                            if "cookies" in info and _should_send_default_pii():
                                request_info["cookies"] = info["cookies"]
                            if "data" in info:
                                request_info["data"] = info["data"]
                        event["request"] = request_info

                        _set_transaction_name_and_source(
                            event, integration.transaction_style, req
                        )

                        return event

                    return event_processor

                warden_scope._name = FastApiIntegration.identifier
                warden_scope.add_event_processor(
                    _make_request_event_processor(request, integration)
                )

            return await old_app(*args, **kwargs)

        return _warden_app

    fastapi.routing.get_request_handler = _warden_get_request_handler # type: ignore
