
from pydantic import BaseModel
from typing import Any, Optional
import orjson
from app.models.requests import RequestValidator
from app.models.llm import DEFAULT_HEADERS


class InteractionCreate(BaseModel):
    request: RequestValidator
    response_body: Optional[Any] = None
    response_status: int
    response_headers: Optional[Any] = DEFAULT_HEADERS

    @staticmethod
    def normalize_value(value: Any) -> Any:
        """
        Normalize any Python value into something storable in SQLite:
        - dict -> JSON bytes
        - bytes -> UTF-8 text
        - None -> 'null'
        - everything else -> str()
        """
        if isinstance(value, dict):
            return orjson.dumps(value).decode("utf-8")

        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")

        if value is None:
            return None

        return str(value)
