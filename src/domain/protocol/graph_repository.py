from typing import Protocol
from .models import Node, Edge


class GraphRepository(Protocol):
    """Protocol for graph data persistence."""

    def setup(self) -> None:
        """Initialize the database (create tables, etc.)."""
        ...

    def save_nodes_batch(self, nodes: list[Node]) -> None:
        """Save a batch of nodes to the database."""
        ...
