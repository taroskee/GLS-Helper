from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, runtime_checkable

from src.domain.model.edge import Edge


@runtime_checkable
class SDFParser(Protocol):
    """Protocol for parsing SDF files to extract delay information."""

    def parse_delays(
        self, path_sdf: Path, batch_size: int = 10000
    ) -> Iterator[tuple[Edge, ...]]:
        """
        Parses SDF and yields batches of Edges with delay information.
        Note: The returned Edges act as DTOs containing (src, dst, delay).
        """
        ...
