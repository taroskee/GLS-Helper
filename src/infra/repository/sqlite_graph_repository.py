import sqlite3

from src.domain.model.node import Node
from src.domain.protocol.graph_repository import GraphRepository

_QUERIES_SETUP = tuple(
    [
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
    ]
)


class SqliteGraphRepository(GraphRepository):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def setup(self) -> None:
        """Orchestrates the database schema initialization."""
        with sqlite3.connect(self.db_path) as connection:
            for script in _QUERIES_SETUP:
                connection.execute(script)

    def save_nodes_batch(self, nodes: list[Node]) -> None:
        """
        [BAD IMPLEMENTATION]
        Intentionally slow implementation using a loop to verify performance tests.
        """
        if not nodes:
            return

        with sqlite3.connect(self.db_path) as connection:
            # 🐌 ここが激遅ポイント
            # 1件ずつインサートするため、毎回ディスクI/Oとロック処理が走る
            for node in nodes:
                connection.execute(
                    "INSERT OR IGNORE INTO nodes (name) VALUES (?)", (node.name,)
                )
