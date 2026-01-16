from src.domain.protocol.graph_repository import GraphRepository
from src.domain.protocol.netlist_parser import NetlistParser


class ImportGateUseCase:
    """Orchestrates the import process from Netlist file to Repository."""

    def __init__(self, repo: GraphRepository, parser: NetlistParser) -> None:
        self._repo = repo
        self._parser = parser

    def execute(self, file_path: str) -> None:
        """Parses the file and saves data in batches."""
        pass

    def _import_nodes(self, file_path: str) -> None:
        pass

    def _import_edges(self, file_path: str) -> None:
        pass
