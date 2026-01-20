from pathlib import Path

from src.domain.protocol.graph_repository import GraphRepository
from src.domain.protocol.progress_observer import ProgressObserver
from src.domain.protocol.verilog_parser import VerilogParser


class ImportVerilogUseCase:
    def __init__(self, repo: GraphRepository, parser: VerilogParser) -> None:
        self._repo = repo
        self._parser = parser

    def execute(
        self, file_path: Path, observer: ProgressObserver | None = None
    ) -> None:
        if observer:
            observer.set_description("Importing Nodes...")

        for batch in self._parser.parse_nodes(file_path, observer=observer):
            self._repo.save_nodes_batch(batch)

        if observer:
            observer.set_description("Importing Edges...")

        for batch in self._parser.parse_edges(file_path, observer=observer):
            self._repo.save_edges_batch(batch)
