from pathlib import Path
from unittest.mock import MagicMock, call

from src.domain.model.node import Node
from src.usecase.import_verilog import ImportVerilogUseCase


def test_execute_orchestrates_parsing_and_saving():
    """
    Verify UseCase receives batch from Parser to Repository
    """
    # Arrange
    mock_repo = MagicMock()
    mock_parser = MagicMock()

    batch_1: tuple[Node, ...] = (Node("u1"), Node("u2"))
    batch_2: tuple[Node, ...] = (Node("u3"),)
    batches: tuple[tuple[Node, ...]] = (batch_1, batch_2)

    mock_parser.parse_nodes.return_value = iter(batches)
    mock_parser.parse_edges.return_value = iter(tuple())

    use_case = ImportVerilogUseCase(repo=mock_repo, parser=mock_parser)
    dummy_path = Path("dummy.v")  # str -> Path

    # Act
    use_case.execute(dummy_path)

    # Assert
    assert mock_repo.save_nodes_batch.call_count == len(batches)
    mock_repo.save_nodes_batch.assert_has_calls([call(batch_1), call(batch_2)])

    mock_parser.parse_nodes.assert_called_with(dummy_path)
