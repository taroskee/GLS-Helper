from pathlib import Path
from unittest.mock import MagicMock, call

from src.domain.model.edge import Edge
from src.usecase.import_sdf import ImportSDFUseCase


def test_execute_orchestrates_parsing_and_updating():
    """
    Verify that UseCase fetches batches from Parser and updates Repository.
    """
    # Arrange
    mock_repo = MagicMock()
    mock_parser = MagicMock()

    batch_1 = (
        Edge(src_node="u1.Q", dst_node="u2.A", delay_rise=0.1, delay_fall=0.1),
        Edge(src_node="u1.Q", dst_node="u3.B", delay_rise=0.2, delay_fall=0.2),
    )
    batch_2 = (Edge(src_node="u2.Z", dst_node="u4.D", delay_rise=0.3, delay_fall=0.3),)

    mock_parser.parse_delays.return_value = iter((batch_1, batch_2))

    use_case = ImportSDFUseCase(repo=mock_repo, parser=mock_parser)
    dummy_path = Path("dummy.sdf")

    # Act
    use_case.execute(dummy_path)

    # Assert
    mock_parser.parse_delays.assert_called_once_with(dummy_path)

    assert mock_repo.update_edges_delay_batch.call_count == len([batch_1, batch_2])
    mock_repo.update_edges_delay_batch.assert_has_calls([call(batch_1), call(batch_2)])
