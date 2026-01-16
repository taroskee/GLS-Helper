import sqlite3

from src.domain.model.node import Node


class SqliteGraphRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def setup(self) -> None:
        """Orchestrates the table creation process."""
        with sqlite3.connect(self.db_path) as connection:
            self._create_nodes_table(connection)
            self._create_edges_table(connection)

    def _create_nodes_table(self, connection: sqlite3.Connection) -> None:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )""")

    def _create_edges_table(self, connection: sqlite3.Connection) -> None:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                src TEXT NOT NULL,
                dst TEXT NOT NULL,
                delay_rise REAL,
                delay_fall REAL
            )""")

    def save_nodes_batch(self, nodes: list[Node]) -> None:
        """Save a batch of nodes. (Pending Implementation)"""
        pass
