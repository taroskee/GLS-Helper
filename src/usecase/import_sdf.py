from pathlib import Path

from src.domain.protocol.graph_repository import GraphRepository
from src.domain.protocol.sdf_parser import SDFParser


class ImportSDFUseCase:
    """Orchestrates the import process from SDF file to Repository."""

    def __init__(self, repo: GraphRepository, parser: SDFParser) -> None:
        self._repo = repo
        self._parser = parser

    def execute(self, file_path: Path) -> None:
        """Parses the SDF file and updates edge delays in batches."""
        for batch in self._parser.parse_delays(file_path):
            self._repo.update_edges_delay_batch(batch)
