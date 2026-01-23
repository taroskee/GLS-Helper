import sqlite3
from contextlib import closing, contextmanager
from typing import Any

from src.domain.model.edge import Edge
from src.domain.model.node import Node
from src.domain.protocol.graph_repository import GraphRepository

_SQLS_SETUP: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS edges (
        src TEXT NOT NULL,
        dst TEXT NOT NULL,
        delay_rise REAL,
        delay_fall REAL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_edges_src_dst ON edges(src, dst)",
)

_SQL_INSERT_NODE: str = "INSERT OR IGNORE INTO nodes (name) VALUES (?)"
_SQL_INSERT_EDGE: str = """
    INSERT INTO edges (src, dst, delay_rise, delay_fall)
    VALUES (?, ?, ?, ?)
"""


class SqliteGraphRepository(GraphRepository):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._active_connection: sqlite3.Connection | None = None

    def setup(self) -> None:
        """Initialize DB schema with performance tuning."""
        with closing(self._connect()) as connection:
            with connection:
                for script in _SQLS_SETUP:
                    connection.execute(script)

    @contextmanager
    def bulk_mode(self):
        """Use a single connection for multiple batch operations."""
        if self._active_connection:
            yield
            return

        self._active_connection = self._connect()
        try:
            yield
        finally:
            if self._active_connection:
                self._active_connection.close()
                self._active_connection = None

    def _get_connection(self) -> sqlite3.Connection:
        """Returns active connection or opens a new temporary one."""
        if self._active_connection:
            return self._active_connection
        return self._connect()

    def save_nodes_batch(self, nodes: tuple[Node]) -> None:
        data = [(n.name,) for n in nodes]
        self._executemany(_SQL_INSERT_NODE, data)

    def save_edges_batch(self, edges: tuple[Edge]) -> None:
        data = [(e.src_node, e.dst_node, e.delay_rise, e.delay_fall) for e in edges]
        self._executemany(_SQL_INSERT_EDGE, data)

    def update_edges_delay_batch(self, edges: tuple[Edge, ...]) -> None:
        if not edges:
            return

        data = [(e.dst_node, e.delay_rise, e.delay_fall) for e in edges]
        connection = self._get_connection()
        should_close = self._active_connection is None

        try:
            with connection:
                connection.execute(
                    "CREATE TEMPORARY TABLE IF NOT EXISTS batch_updates "
                    "(node TEXT PRIMARY KEY, rise REAL, fall REAL)"
                )
                connection.executemany(
                    "INSERT OR REPLACE INTO batch_updates (node, rise, fall) VALUES (?, ?, ?)",
                    data,
                )
                connection.execute("""
                    UPDATE edges
                    SET delay_rise = batch_updates.rise,
                        delay_fall = batch_updates.fall
                    FROM batch_updates
                    WHERE edges.src = batch_updates.node
                """)
                connection.execute("DELETE FROM batch_updates")
        finally:
            if should_close:
                connection.close()

    def find_max_delay_path(
        self, start_node: str, end_node: str | None = None, max_depth: int = 100
    ) -> tuple[Edge, ...]:
        """Finds the max delay path using Recursive CTE."""
        path_str = self._fetch_max_delay_path_string(start_node, end_node, max_depth)

        if not path_str:
            return tuple()

        return self._reconstruct_edges_from_path(path_str)

    def _connect(self) -> sqlite3.Connection:
        """Creates a connection with performance settings."""
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")
        connection.execute("PRAGMA temp_store = MEMORY")
        connection.execute("PRAGMA cache_size = -64000")
        return connection

    def _executemany(self, sql: str, data: list[Any]) -> None:
        if not data:
            return

        connection = self._get_connection()
        should_close = self._active_connection is None
        try:
            with connection:  # Commit transaction
                connection.executemany(sql, data)
        finally:
            if should_close:
                connection.close()

    def _fetch_max_delay_path_string(
        self, start: str, end: str | None, depth: int
    ) -> str | None:
        sql = self._build_recursive_query(end is not None)
        params = [start, depth]
        if end:
            params.append(end)

        with closing(self._connect()) as connection:
            row = connection.execute(sql, tuple(params)).fetchone()
            return row[0] if row else None

    def _build_recursive_query(self, has_end_node: bool) -> str:
        base_sql = """
        WITH RECURSIVE paths(current_node, path_str, total_delay, depth) AS (
            SELECT dst, src || ',' || dst, MAX(delay_rise, delay_fall), 1
            FROM edges WHERE src = ?
            UNION ALL
            SELECT e.dst, p.path_str || ',' || e.dst,
                   p.total_delay + MAX(e.delay_rise, e.delay_fall), p.depth + 1
            FROM edges e JOIN paths p ON e.src = p.current_node
            WHERE p.depth < ? AND instr(p.path_str, e.dst) = 0
        )
        SELECT path_str FROM paths
        """
        where = "WHERE current_node = ?" if has_end_node else ""
        order = "ORDER BY total_delay DESC LIMIT 1"
        return f"{base_sql} {where} {order}"

    def _reconstruct_edges_from_path(self, path_str: str) -> tuple[Edge, ...]:
        nodes = path_str.split(",")
        edges: list[Edge] = []
        sql = "SELECT src, dst, delay_rise, delay_fall FROM edges WHERE src=? AND dst=?"

        with closing(self._connect()) as connection:
            cursor = connection.cursor()
            for i in range(len(nodes) - 1):
                if row := cursor.execute(sql, (nodes[i], nodes[i + 1])).fetchone():
                    edges.append(Edge(*row))

        return tuple(edges)
