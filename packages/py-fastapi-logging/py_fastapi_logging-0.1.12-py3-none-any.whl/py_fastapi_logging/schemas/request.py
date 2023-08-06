from typing import TypedDict


class RequestPayload(TypedDict):
    method: str
    path: str
    host: str
    subject_type: str | None
    subject_id: str | None
    params: dict | None
    body: str
