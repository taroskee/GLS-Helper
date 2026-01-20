from pathlib import Path

from src.domain.protocol.graph_repository import GraphRepository
from src.domain.protocol.verilog_parser import VerilogParser


class ImportVerilogUseCase:
    """Orchestrates the import process from verilog file to Repository."""

    def __init__(self, repo: GraphRepository, parser: VerilogParser) -> None:
        self._repo = repo
        self._parser = parser

    def execute(self, file_path: Path) -> None:
        """Parses the file and saves data in batches."""
        self._import_nodes(file_path)
        self._import_edges(file_path)

    def _import_nodes(self, file_path: Path) -> None:
        for batch in self._parser.parse_nodes(file_path):
            self._repo.save_nodes_batch(batch)

    def _import_edges(self, file_path: Path) -> None:
        for batch in self._parser.parse_edges(file_path):
            self._repo.save_edges_batch(batch)
