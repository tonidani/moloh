import orjson
import uuid

from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, Field, model_validator

DEFAULT_HEADERS = {
    "Server": "nginx/1.22.1",
    "X-Request-ID": str(uuid.uuid4()),
    "X-Trace-ID": str(uuid.uuid4()),
    "X-Response-Time": "auto",
    "Date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),  # type: ignore
    "Cache-Control": "no-cache",
    "Vary": "Accept-Encoding",
}


class LLMResponse(BaseModel):
    body: Dict[str, Any] | str = Field(default_factory=dict)
    status_code: int = 200
    headers: Dict[str, Any] = DEFAULT_HEADERS

    @model_validator(mode="before")
    @classmethod
    def clean_llm_output(cls, raw: Any) -> Dict[str, Any]:  # type: ignore

        if isinstance(raw, dict):
            return raw  # type: ignore

        if not isinstance(raw, str):
            raise ValueError(f"LLMResponse expects dict or str, got: {type(raw)}")

        txt = raw.strip()

        if txt.startswith("```"):
            nl = txt.find("\n")
            if nl != -1:
                txt = txt[nl + 1:].lstrip()
        if txt.endswith("```"):
            txt = txt[:-3].rstrip()

        txt = txt.strip()

        try:
            parsed = orjson.loads(txt)
        except Exception:
            return {
                "body": txt.replace("\r", "").replace("\n", ""),
                "status_code": 200,
                "headers": {}
            }

        body_val = parsed.get("body")

        if isinstance(body_val, str):
            inner = body_val.strip()

            if inner.startswith("```"):
                nl = inner.find("\n")
                if nl != -1:
                    inner = inner[nl + 1:].lstrip()
            if inner.endswith("```"):
                inner = inner[:-3].rstrip()

            inner = inner.strip()
            inner = inner.replace("\r", "").replace("\n", "")

            parsed["body"] = inner

        headers_val = parsed.get("headers")

        clean_headers = {}
        for k, v in headers_val.items():
            if isinstance(v, str):
                clean_headers[k] = v.strip()
            else:
                clean_headers[k] = v
        parsed["headers"] = clean_headers

        return parsed
