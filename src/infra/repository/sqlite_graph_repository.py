import sqlite3
from contextlib import closing

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
_SQL_UPDATE_EDGE_DELAY: str = """
    UPDATE edges
    SET delay_rise = ?, delay_fall = ?
    WHERE src = ?
"""


class SqliteGraphRepository(GraphRepository):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def setup(self) -> None:
        with closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                connection.execute("PRAGMA journal_mode = WAL")
                connection.execute("PRAGMA synchronous = NORMAL")
                for script in _SQLS_SETUP:
                    connection.execute(script)

    def save_nodes_batch(self, nodes: tuple[Node]) -> None:
        if not nodes:
            return
        data = [(n.name,) for n in nodes]
        connection = sqlite3.connect(self.db_path)
        try:
            with connection:
                connection.executemany(_SQL_INSERT_NODE, data)
        finally:
            connection.close()

    def save_edges_batch(self, edges: tuple[Edge]) -> None:
        if not edges:
            return
        data = [(e.src_node, e.dst_node, e.delay_rise, e.delay_fall) for e in edges]
        connection = sqlite3.connect(self.db_path)
        try:
            with connection:
                connection.executemany(_SQL_INSERT_EDGE, data)
        finally:
            connection.close()

    def update_edges_delay_batch(self, edges: tuple[Edge]) -> None:
        if not edges:
            return
        data = [(e.delay_rise, e.delay_fall, e.dst_node) for e in edges]
        connection = sqlite3.connect(self.db_path)
        try:
            with connection:
                connection.executemany(_SQL_UPDATE_EDGE_DELAY, data)
        finally:
            connection.close()

    def find_max_delay_path(
        self, start_node: str, end_node: str | None = None, max_depth: int = 100
    ) -> tuple[Edge]:
        """Finds the max delay path using Recursive CTE."""

        sql_recursive_base = """
        WITH RECURSIVE paths(current_node, path_str, total_delay, depth) AS (
            SELECT
                dst,
                src || ',' || dst,
                MAX(delay_rise, delay_fall),
                1
            FROM edges
            WHERE src = ?

            UNION ALL

            SELECT
                e.dst,
                p.path_str || ',' || e.dst,
                p.total_delay + MAX(e.delay_rise, e.delay_fall),
                p.depth + 1
            FROM edges e
            JOIN paths p ON e.src = p.current_node
            WHERE p.depth < ?
              AND instr(p.path_str, e.dst) = 0
        )
        SELECT path_str FROM paths
        """
        query_select = "SELECT src, dst, delay_rise, delay_fall"

        where_clause = "WHERE current_node = ? " if end_node else ""
        order_clause = "ORDER BY total_delay DESC LIMIT 1"

        final_sql = f"{sql_recursive_base} {where_clause} {order_clause}"

        params = [start_node, max_depth]
        if end_node:
            params.append(end_node)

        path_str = None
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(final_sql, tuple(params))
            row = cursor.fetchone()
            if row:
                path_str = row[0]

        if not path_str:
            return tuple()

        nodes = path_str.split(",")
        edges = []
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            for i in range(len(nodes) - 1):
                src = nodes[i]
                dst = nodes[i + 1]
                cursor.execute(
                    f"{query_select} FROM edges WHERE src = ? AND dst = ?", (src, dst)
                )
                row = cursor.fetchone()
                if row:
                    edges.append(Edge(row[0], row[1], row[2], row[3]))

        return tuple(edges)
