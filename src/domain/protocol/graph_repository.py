from typing import Protocol, runtime_checkable

from src.domain.model.edge import Edge
from src.domain.model.node import Node


@runtime_checkable
class GraphRepository(Protocol):
    """Protocol for graph data persistence."""

    def setup(self) -> None:
        """Initialize the database (create tables, etc.)."""
        ...

    def save_nodes_batch(self, nodes: list[Node]) -> None:
        """Save a batch of nodes to the database."""
        ...

    def save_edges_batch(self, edges: list[Edge]) -> None:
        """Save a batch of edges to the database."""
        ...

    def update_edges_delay_batch(self, edges: list[Edge]) -> None:
        """Update delay information for existing edges."""
        ...
