from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, runtime_checkable

from src.domain.model.edge import Edge
from src.domain.model.node import Node


@runtime_checkable
class VerilogParser(Protocol):
    """Protocol for parsing Verilog files using streams."""

    def parse_nodes(
        self, path_verilog: Path, batch_size: int = 10000
    ) -> Iterator[tuple[Node]]:
        """Yields batches of nodes from the file."""
        ...

    def parse_edges(
        self, path_verilog: Path, batch_size: int = 10000
    ) -> Iterator[tuple[Edge]]:
        """Yields batches of edges from the file."""
        ...
