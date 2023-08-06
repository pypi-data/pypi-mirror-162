from inspect import Signature
from typing import TYPE_CHECKING, cast

from starlite.exceptions import ImproperlyConfiguredException
from starlite.handlers.base import BaseRouteHandler
from starlite.utils import is_async_callable

if TYPE_CHECKING:
    from pydantic.typing import AnyCallable

    from starlite.types import AsyncAnyCallable


class WebsocketRouteHandler(BaseRouteHandler["WebsocketRouteHandler"]):
    def __call__(self, fn: "AsyncAnyCallable") -> "WebsocketRouteHandler":
        """
        Replaces a function with itself
        """
        self.fn = fn
        self.validate_handler_function()
        return self

    def validate_handler_function(self) -> None:
        """
        Validates the route handler function once it's set by inspecting its return annotations
        """
        super().validate_handler_function()
        signature = Signature.from_callable(cast("AnyCallable", self.fn))

        if signature.return_annotation is not None:
            raise ImproperlyConfiguredException("Websocket handler functions should return 'None'")
        if "socket" not in signature.parameters:
            raise ImproperlyConfiguredException("Websocket handlers must set a 'socket' kwarg")
        if "request" in signature.parameters:
            raise ImproperlyConfiguredException("The 'request' kwarg is not supported with websocket handlers")
        if "data" in signature.parameters:
            raise ImproperlyConfiguredException("The 'data' kwarg is not supported with websocket handlers")
        if not is_async_callable(self.fn):
            raise ImproperlyConfiguredException("Functions decorated with 'websocket' must be async functions")


websocket = WebsocketRouteHandler
