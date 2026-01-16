import sqlite3

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
)

_SQL_INSERT_NODE: str = "INSERT OR IGNORE INTO nodes (name) VALUES (?)"
_SQL_INSERT_EDGE: str = """
    INSERT INTO edges (src, dst, delay_rise, delay_fall)
    VALUES (?, ?, ?, ?)
"""


class SqliteGraphRepository(GraphRepository):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def setup(self) -> None:
        """
        Orchestrates the database schema initialization.
        Also applies performance tuning for massive write operations.
        """
        with sqlite3.connect(self.db_path) as connection:
            # WAL mode: To improve multi-thred in writing
            connection.execute("PRAGMA journal_mode = WAL")
            # NORMAL mode: To improve writing but less stable
            connection.execute("PRAGMA synchronous = NORMAL")

            for script in _SQLS_SETUP:
                connection.execute(script)

    def save_nodes_batch(self, nodes: list[Node]) -> None:
        """Save a batch of nodes using fast executemany."""
        if not nodes:
            return

        data = [(n.name,) for n in nodes]

        with sqlite3.connect(self.db_path) as connection:
            connection.executemany(_SQL_INSERT_NODE, data)

    def save_edges_batch(self, edges: list[Edge]) -> None:
        """Save a batch of edges using fast executemany."""
        if not edges:
            return

        data = [(e.src_node, e.dst_node, e.delay_rise, e.delay_fall) for e in edges]

        with sqlite3.connect(self.db_path) as connection:
            connection.executemany(_SQL_INSERT_EDGE, data)
