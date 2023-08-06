import http
import json
import logging
import math
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.types import ASGIApp

from py_fastapi_logging.config.config import LogConfigure, init_logger
from py_fastapi_logging.middlewares.utils.request_id import REQUEST_ID_HEADER, generate_request_id
from py_fastapi_logging.schemas.request import RequestPayload
from py_fastapi_logging.schemas.response import ResponsePayload
from py_fastapi_logging.utils.extra import set_extra_to_environ


class LoggingMiddleware(BaseHTTPMiddleware):
    _app_name: str = ""
    _prefix: str = ""
    _logger: logging.Logger = None

    def __init__(
        self,
        app: ASGIApp,
        app_name: str,
        dispatch: DispatchFunction = None,
        prefix: str = None,
        logger: logging.Logger = None,
    ):
        if not logger:
            init_logger(app_name=app_name)
            logger = logging.getLogger("default")
        self.app = app
        self._app_name = app_name
        self._prefix = prefix
        self._logger = logger
        self.dispatch_func = self.dispatch if dispatch is None else dispatch

    @staticmethod
    def get_request_id_header(headers):
        for name, value in headers.items():
            if name.lower() == REQUEST_ID_HEADER.lower():
                try:
                    return value
                except UnicodeDecodeError:
                    return ""

    @staticmethod
    async def get_protocol(request: Request) -> str:
        protocol = str(request.scope.get("type", ""))
        http_version = str(request.scope.get("http_version", ""))
        if protocol.lower() == "http" and http_version:
            return f"{protocol.upper()}/{http_version}"
        return ""

    @staticmethod
    async def set_body(request: Request, body: bytes) -> None:
        async def receive() -> dict:
            return {"type": "http.request", "body": body}

        request._receive = receive

    async def get_body(self, request: Request) -> bytes:
        body = await request.body()
        await self.set_body(request, body)
        return body

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        try:
            raw_request_body = await request.body()
            await self.set_body(request, raw_request_body)
            raw_request_body = await self.get_body(request)
            request_body = raw_request_body.decode()
        except Exception:
            request_body = ""
        request_headers: dict = dict(request.headers.items())
        request_id = self.get_request_id_header(request_headers) or generate_request_id(prefix=self._prefix)
        set_extra_to_environ("request_id", request_id)

        server: tuple = request.get("server", ("localhost", 80))
        request_params = request.query_params

        common_extras = {
            "progname": self._app_name,
            "request_id": request_id,
        }

        request_log_payload = RequestPayload(
            method=request.method,
            path=request.url.path,
            host=f"{server[0]}:{server[1]}",
            params=dict(request_params) if request_params is not None else {},
            body=request_body,
        )
        self._logger.info(
            f"REQUEST {request.method} {request.url.path}",
            extra={
                **common_extras,
                "tags": ["API", "REQUEST"],
                "payload": self._filter_private_data(request_log_payload),
            },
        )

        try:
            response = await call_next(request)
        except Exception as ex:
            response_body = bytes(http.HTTPStatus.INTERNAL_SERVER_ERROR.phrase.encode())
            response = Response(
                content=response_body,
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR.real,
            )
            self._logger.exception("", exc_info=ex)
        else:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        duration: int = math.ceil((time.time() - start_time) * 1000)

        response_log_payload = ResponsePayload(
            status=response.status_code,
            response_time=f"{duration}ms",
            response_body=response_body.decode(),
        )

        self._logger.info(
            f"RESPONSE {response.status_code} {request.url.path}",
            extra={
                **common_extras,
                "tags": ["API", "RESPONSE"],
                "payload": self._filter_private_data(response_log_payload),
            },
        )

        return response

    def _filter_private_data(self, payload: dict):
        _filtered_fields = LogConfigure().get_exclude_fields()
        _marker_filtered = "[filtered]"
        if "params" in payload.keys() and payload["params"] is not None and _filtered_fields is not None:
            for key in list(payload["params"]):
                if key in _filtered_fields:
                    payload["params"][key] = _marker_filtered
            payload = self._filter_json_field("body", payload, _filtered_fields, _marker_filtered)
        elif "response_body" in payload.keys() and _filtered_fields is not None:
            payload = self._filter_json_field("response_body", payload, _filtered_fields, _marker_filtered)
        return payload

    def _filter_json_field(self, key, payload, _filtered_fields, _marker_filtered="[filtered]"):
        try:
            body_dict = json.loads(payload[key])
            if body_dict is not None:
                for body_key in list(body_dict):
                    if body_key in _filtered_fields:
                        body_dict[body_key] = _marker_filtered
                payload[key] = json.dumps(body_dict, ensure_ascii=False)
        except json.decoder.JSONDecodeError:
            pass
        return payload
