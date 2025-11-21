import os
import aiosqlite

from typing import Any

from app.variables import DB_PATH, EXTENSIONS, SCHEMAS, PRAGMAS


async def init_db(init_if_missing: bool = False) -> Any:
    db_exists = os.path.exists(DB_PATH)

    db = await aiosqlite.connect(DB_PATH)

    db.row_factory = aiosqlite.Row

    await db.enable_load_extension(True)

    for ext in EXTENSIONS:
        try:
            await db.execute(f"SELECT load_extension('{ext}');")
        except Exception as e:
            print(f"[db] Failed loading {ext}: {e}")

    if init_if_missing and not db_exists:
        for sql in SCHEMAS:
            schema = sql.read_text(encoding="utf-8")
            await db.executescript(schema)
            await db.commit()
            print("[db] Schema applied.")

    for p in PRAGMAS:
        try:
            await db.execute(p)
        except Exception as e:
            print(f"[db] Failed PRAGMA {p}: {e}")

    await db.commit()
    return db
