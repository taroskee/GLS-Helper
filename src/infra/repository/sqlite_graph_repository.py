import sqlite3

from src.domain.model.node import Node


class SqliteGraphRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def setup(self) -> None:
        """Orchestrates the table creation process."""
        pass

    def _create_nodes_table(self, conn: sqlite3.Connection) -> None:
        pass

    def _create_edges_table(self, conn: sqlite3.Connection) -> None:
        pass

    def save_nodes_batch(self, nodes: list[Node]) -> None:
        """Save a batch of nodes. (Pending Implementation)"""
        pass
