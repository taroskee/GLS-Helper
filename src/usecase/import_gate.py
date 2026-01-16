from src.domain.protocol.graph_repository import GraphRepository
from src.domain.protocol.netlist_parser import NetlistParser


class ImportGateUseCase:
    """Orchestrates the import process from Netlist file to Repository."""

    def __init__(self, repo: GraphRepository, parser: NetlistParser) -> None:
        self._repo = repo
        self._parser = parser

    def execute(self, file_path: str) -> None:
        """Parses the file and saves data in batches."""
        self._import_nodes(file_path)
        self._import_edges(file_path)

    def _import_nodes(self, file_path: str) -> None:
        for batch in self._parser.parse_nodes(file_path):
            self._repo.save_nodes_batch(batch)

    def _import_edges(self, file_path: str) -> None:
        for batch in self._parser.parse_edges(file_path):
            self._repo.save_edges_batch(batch)
