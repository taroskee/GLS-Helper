from contextlib import AbstractContextManager
from typing import Protocol, runtime_checkable

from src.domain.model.edge import Edge
from src.domain.model.node import Node


@runtime_checkable
class GraphRepository(Protocol):
    """Protocol for graph data persistence."""

    def setup(self) -> None:
        """Initialize the database (create tables, etc.)."""
        ...

    def save_nodes_batch(self, nodes: tuple[Node]) -> None:
        """Save a batch of nodes to the database."""
        ...

    def save_edges_batch(self, edges: tuple[Edge]) -> None:
        """Save a batch of edges to the database."""
        ...

    def update_edges_delay_batch(self, edges: tuple[Edge]) -> None:
        """Update delay information for existing edges."""
        ...

    def find_max_delay_path(
        self, start_node: str, end_node: str | None = None, max_depth: int = 100
    ) -> tuple[Edge]:
        """
        Finds the path with the maximum accumulated delay between start and end nodes.
        Returns the tuple of edges forming that path.
        """

        ...

    def bulk_mode(self) -> AbstractContextManager:
        """Context manager for bulk operations."""
