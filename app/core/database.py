import logging
from contextlib import contextmanager
from typing import Generator

from psycopg2.extensions import connection
from psycopg2.pool import ThreadedConnectionPool

logger = logging.getLogger(__name__)


class DatabasePool:
    def __init__(self, dsn: str, min_size: int, max_size: int) -> None:
        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._pool: ThreadedConnectionPool | None = None

    def open(self) -> None:
        if self._pool is None:
            self._pool = ThreadedConnectionPool(
                minconn=self._min_size,
                maxconn=self._max_size,
                dsn=self._dsn,
            )

    def close(self) -> None:
        if self._pool is not None:
            self._pool.closeall()
            self._pool = None

    @contextmanager
    def connection(self) -> Generator[connection, None, None]:
        pool = self._pool
        if pool is None:
            raise RuntimeError("Database pool is not initialized")

        db_connection = pool.getconn()
        try:
            yield db_connection
        finally:
            discard = bool(db_connection.closed)
            if not discard:
                try:
                    db_connection.rollback()
                except Exception:
                    logger.exception(
                        "Could not reset PostgreSQL connection; discarding it"
                    )
                    discard = True
            pool.putconn(db_connection, close=discard)
