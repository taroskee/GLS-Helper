from collections.abc import Iterator
from typing import Protocol, runtime_checkable

from src.domain.model.edge import Edge
from src.domain.model.node import Node


@runtime_checkable
class NetlistParser(Protocol):
    """Protocol for parsing Gate Netlist files using streams."""

    def parse_nodes(
        self, file_path: str, batch_size: int = 10000
    ) -> Iterator[tuple[Node]]:
        """Yields batches of nodes from the file."""
        ...

    def parse_edges(
        self, file_path: str, batch_size: int = 10000
    ) -> Iterator[tuple[Edge]]:
        """Yields batches of edges from the file."""
        ...
