import logging
import time
from types import SimpleNamespace
from typing import NamedTuple

from multidict import MultiDict
from yarl import URL

import aiohttp

_ParamsDict = dict[str, str, list[str]]


class _Request(NamedTuple):
    service_name: str | None
    request_id: str | None
    method: str
    url: URL
    start_time: float


def create_logging_trace_config(service_name: str | None) -> aiohttp.TraceConfig:
    def context_factory(**kwargs) -> SimpleNamespace:
        return SimpleNamespace(service_name=service_name, **kwargs)

    trace_config = aiohttp.TraceConfig(context_factory)
    trace_config.on_request_start.append(_on_request_start)
    trace_config.on_request_chunk_sent.append(_on_request_chunk_sent)
    trace_config.on_request_end.append(_on_request_end)
    return trace_config


def _convert_params_to_dict(params_mulitdict: MultiDict) -> _ParamsDict:
    params_dict: _ParamsDict = {}
    for key in params_mulitdict.keys():
        values = params_mulitdict.getall(key)
        params_dict[key] = values[0] if len(values) == 1 else values
    return params_dict


def _make_tags_list(*tags: str | None) -> list[str]:
    return list(filter(None, tags))


async def _on_request_start(
    session: aiohttp.ClientSession,
    context: SimpleNamespace,
    params: aiohttp.TraceRequestStartParams,
) -> None:
    request_id = params.headers.get("x-request-id")
    context.request = _Request(
        service_name=context.service_name,
        request_id=request_id,
        method=params.method,
        url=params.url,
        start_time=time.time(),
    )


async def _on_request_chunk_sent(
    session: aiohttp.ClientSession,
    context: SimpleNamespace,
    params: aiohttp.TraceRequestChunkSentParams,
) -> None:
    request: _Request = context.request
    try:
        request_body = params.chunk.decode("utf8")
    except Exception:
        logging.exception("Failed to decode request body")
        request_body = "(failed to decode)"

    logging.info(
        f"Request {request.method} {request.url}",
        extra={
            "tags": _make_tags_list("SERVICE", request.service_name, "REQUEST"),
            "request_id": request.request_id,
            "payload": {
                "method": request.method,
                "url": str(request.url.with_query(None)),
                "params": _convert_params_to_dict(request.url.query),
                "body": request_body,
            },
        },
    )


async def _on_request_end(
    session: aiohttp.ClientSession,
    context: SimpleNamespace,
    params: aiohttp.TraceRequestEndParams,
):
    request: _Request = context.request
    request_time_ms = int((time.time() - request.start_time) * 1000)
    logging.info(
        f"Response {request.method} {request.url}",
        extra={
            "tags": _make_tags_list("SERVICE", request.service_name, "RESPONSE"),
            "request_id": request.request_id,
            "payload": {
                "status": params.response.status,
                "response_time": f"{request_time_ms}ms",
                "response_body": await params.response.text(),
            },
        },
    )
