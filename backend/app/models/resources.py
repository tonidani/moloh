
import numpy as np
import orjson
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Tuple


class ResourceCreate(BaseModel):
    canonical_key: str | None = None
    path: str | None = None
    response_body: Optional[Any] = None
    response_status: int = 200
    response_headers: Optional[Any] = None
    embedding: Optional[List[float]] = None

    @staticmethod
    def decode_body(raw: bytes) -> Any:
        """
        Dekoduje JSON / HTML / TEXT z bazy.
        Najpierw próbuje JSON, a jeśli się nie da → UTF-8 tekst.
        """
        if not raw:
            return None

        # Spróbuj JSON
        try:
            decoded = orjson.loads(raw)
            if decoded == "None":
                return None
        except Exception:
            pass

        # Jak nie JSON → tekst
        try:
            return raw.decode("utf-8", errors="replace")
        except Exception:

            return str(raw)

    def get_blob(self, key: str) -> bytes:
        """
        Zwraca body w formacie do zapisania w SQLite.
        - JSON → orjson.dumps
        - HTML/TEXT → UTF-8
        """
        if isinstance(getattr(self, key), (dict, list)):
            return orjson.dumps(getattr(self, key))

        # HTML/TEXT
        return str(getattr(self, key)).encode("utf-8")

    def get_insert_query(self) -> Tuple[str, Tuple[Any]]:
        print(self.response_headers)
        sql = """
            INSERT INTO resources (
                canonical_key,
                response_body,
                path,
                response_status,
                response_headers
            )
            VALUES (?, ?, ?, ?, ?)
        """

        params = (
            self.canonical_key,
            self.get_blob('response_body'),
            self.path,
            self.response_status,
            self.get_blob('response_headers')
        )

        return sql, params  # type: ignore

    def get_embedding_blob(self) -> None | bytes:
        if self.embedding is None:
            return None
        return np.asarray(self.embedding, dtype=np.float32).tobytes()


class ResourceDB(BaseModel):
    id: int
    response_body: Optional[Dict[str, Any] | str] = None
    response_status: int = 200
    response_headers: Optional[Any] = None

    @staticmethod
    def decode_body(raw: bytes | str | None) -> Any:
        if raw is None:
            return None

        # STR → spróbuj JSON
        if isinstance(raw, str):
            try:
                val = orjson.loads(raw)
                return None if val == "None" else val
            except Exception:
                return raw

        # BYTES → JSON?
        try:
            val = orjson.loads(raw)
            return None if val == "None" else val
        except Exception:
            pass

        # BYTES → string
        try:
            return raw.decode("utf-8", errors="replace")  # type: ignore
        except Exception:
            return str(raw)

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "ResourceDB":
        return cls(
            id=row["id"],
            response_body=cls.decode_body(row["response_body"]),
            response_status=row["response_status"],
            response_headers=cls.decode_body(row["response_headers"]),
        )
