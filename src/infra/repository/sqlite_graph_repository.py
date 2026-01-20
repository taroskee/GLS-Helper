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
        """
        Orchestrates the database schema initialization.
        Also applies performance tuning for massive write operations.
        """
        with closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                connection.execute("PRAGMA journal_mode = WAL")
                connection.execute("PRAGMA synchronous = NORMAL")
                for script in _SQLS_SETUP:
                    connection.execute(script)

    def save_nodes_batch(self, nodes: list[Node]) -> None:
        """Save a batch of nodes using fast executemany."""
        if not nodes:
            return

        data = [(n.name,) for n in nodes]

        connection = sqlite3.connect(self.db_path)
        try:
            with connection:
                connection.executemany(_SQL_INSERT_NODE, data)
        finally:
            connection.close()

    def save_edges_batch(self, edges: list[Edge]) -> None:
        """Save a batch of edges using fast executemany."""
        if not edges:
            return

        data = [(e.src_node, e.dst_node, e.delay_rise, e.delay_fall) for e in edges]

        connection = sqlite3.connect(self.db_path)
        try:
            with connection:
                connection.executemany(_SQL_INSERT_EDGE, data)
        finally:
            connection.close()

    def update_edges_delay_batch(self, edges: list[Edge]) -> None:
        """Updates delay information mapping SDF destination to DB source pin."""
        if not edges:
            return

        data = [(e.delay_rise, e.delay_fall, e.dst_node) for e in edges]

        connection = sqlite3.connect(self.db_path)
        try:
            with connection:
                connection.executemany(_SQL_UPDATE_EDGE_DELAY, data)
        finally:
            connection.close()
