import os

from datetime import datetime
from pathlib import Path
from typing import Any, Dict


SECRET = os.getenv("SECRET")

DB_PATH = os.getenv("DB_NAME", Path(f"/volume/{datetime.now().strftime("%Y-%m-%d")}.db"))
REDIS_HOST = os.getenv("REDIS_HOST", "honeypot-redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
OLLAMA_URL = os.getenv("OLLAMA_BASE_URLS", "http://localhost:11434")
OPEN_API_KEY = os.getenv("OPEN_API_KEY", None)

RESOURCES_SQL = Path("app/sql/resources.sql")
INTERACTION_SQL = Path("app/sql/interactions.sql")
USERS_SQL = Path("app/sql/users.sql")


SCHEMAS = [RESOURCES_SQL, INTERACTION_SQL, USERS_SQL]


EXT_VECTOR = Path("/usr/local/lib/sqlite/vector0.so")
EXT_VSS = Path("/usr/local/lib/sqlite/vss0.so")

EXTENSIONS = [EXT_VECTOR, EXT_VSS]

PRAGMAS = [
    "PRAGMA foreign_keys=ON;",
    "PRAGMA journal_mode=WAL;",
    "PRAGMA synchronous=NORMAL;",
    "PRAGMA temp_store=MEMORY;",
    "PRAGMA cache_size=-64000;",
    "PRAGMA busy_timeout=5000;",
]


MODEL = os.getenv("MODEL", "llama3.1:8b")
OPEN_API_MODEL = os.getenv("OPEN_API_MODEL", "gpt-5-nano")

PROMPT_DIR = Path("templates")


def load_prompt(name: str) -> str:
    path = PROMPT_DIR / name
    return path.read_text(encoding="utf-8")


def load_attack_template(name: str) -> Dict[str, Any] | None:
    try:
        with open(PROMPT_DIR / name, "r", encoding="utf-8") as f:  # type: ignore
            data = orjson.loads(f.read())  # type: ignore
        return data
    except:
        return None


SYSTEM_PROMPT_NAME = "mega_system_prompt_template.txt" if OPEN_API_KEY else "small_system_prompt_template.txt"
AUGMENT_PROMPT_MAME = "mega_prompt_template.txt" if OPEN_API_KEY else "small_prompt_template.txt"

SYSTEM_PROMPT = load_prompt(SYSTEM_PROMPT_NAME)
AUGMENT_TEMPLATE = load_prompt(AUGMENT_PROMPT_MAME)
ATTACK_TEMPLATE = load_attack_template("attack_templates.json")
