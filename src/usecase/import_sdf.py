from pathlib import Path

from src.domain.protocol.graph_repository import GraphRepository
from src.domain.protocol.progress_observer import ProgressObserver
from src.domain.protocol.sdf_parser import SDFParser


class ImportSDFUseCase:
    def __init__(self, repo: GraphRepository, parser: SDFParser) -> None:
        self._repo = repo
        self._parser = parser

    def execute(
        self, file_path: Path, observer: ProgressObserver | None = None
    ) -> None:
        if observer:
            observer.set_description("Importing Delays...")

        with self._repo.bulk_mode():
            for batch in self._parser.parse_delays(
                file_path, batch_size=100000, observer=observer
            ):
                self._repo.update_edges_delay_batch(batch)
