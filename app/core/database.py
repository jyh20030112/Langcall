from collections.abc import Generator
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from app.core.config import settings


@contextmanager
def get_db_connection() -> Generator[psycopg.Connection, None, None]:
    connection = psycopg.connect(
        settings.database_url,
        row_factory=dict_row,
    )
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
