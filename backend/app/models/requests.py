from datetime import datetime
import hashlib

import re
import orjson
from pydantic import BaseModel, Field, field_validator
from typing import Any
from fastapi import HTTPException, Response


class RequestValidator(BaseModel):
    client_ip: str | None
    full_path: str
    method: str
    query_params: Any | None = None
    body: dict[str, Any] | None = None
    headers: dict[str, Any] | None
    requested_at: datetime = Field(default_factory=datetime.utcnow)  # type: ignore

    @property
    def semantic_key(self) -> str:
        return f"{self.method} {self.full_path} {orjson.dumps(self.query_params)} {orjson.dumps(self.body)}"

    @property
    def hash(self) -> str:
        signature_raw = f"{self.method}:{self.full_path}:{self.query_params}:{self.body}"
        return hashlib.sha256(signature_raw.encode()).hexdigest()

    def canonicalize(self, method: str | None = None):
        qp = "&".join(f"{k}={v}" for k, v in sorted(self.query_params.items())) if self.query_params else None
        return f"{method}:{self.full_path}{"?" + qp if qp else ""}"

    @field_validator("full_path")
    @classmethod
    def validate_uuid_ids(cls, v: str) -> str | Response:
        UUID_V4_RE = re.compile(
            r'^[0-9a-f]{8}-?[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-?[0-9a-f]{12}$',
            re.I,
        )
        API_VERSION_RE = re.compile(r'^v[1-3]$', re.I)

        segments = [s for s in v.split("/") if s]

        if len(segments) > 5:
            raise HTTPException(status_code=204)

        for seg in segments:

            if API_VERSION_RE.fullmatch(seg):
                continue

            if seg.isalpha():
                continue

            if not seg.isalnum():
                continue

            if not UUID_V4_RE.fullmatch(seg):
                raise HTTPException(
                    status_code=404,
                    detail=f"Segment '{seg}' must be a valid UUID v4 for resource identifiers."
                )

        return v
