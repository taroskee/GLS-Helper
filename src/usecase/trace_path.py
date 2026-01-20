from src.domain.model.edge import Edge
from src.domain.protocol.graph_repository import GraphRepository


class TracePathUseCase:
    """UseCase to find the critical path between two nodes."""

    def __init__(self, repo: GraphRepository) -> None:
        self._repo = repo

    def execute(self, start_node: str, end_node: str | None = None) -> tuple[Edge]:
        return self._repo.find_max_delay_path(start_node, end_node)
