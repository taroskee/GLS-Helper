import pytest

from src.infra.parser.sdf_stream_parser import SDFStreamParser


@pytest.fixture()
def parser() -> SDFStreamParser:
    return SDFStreamParser()


def test_parse_delays_extracts_interconnect_delays(parser, tmp_path):
    """
    Verify that INTERCONNECT delays are correctly parsed,
    even when spread across multiple lines.
    """
    # Arrange
    sdf_content = """
(DELAYFILE
  (CELL
    (CELLTYPE "CHIPTOP")
    (INSTANCE)
    (DELAY
      (ABSOLUTE
        (INTERCONNECT u1/Q u2/A (0.1::0.2) (0.1::0.2))
        (INTERCONNECT u1/Q u3/B (0.3::0.4)
          (0.3::0.5))
      )
    )
  )
)
    """
    num_edges = 2
    max_1_rise_fall = 0.2
    max_2_rise = 0.4
    max_2_fall = 0.5
    sdf_file = tmp_path / "test.sdf"
    sdf_file.write_text(sdf_content, encoding="utf-8")

    # Act
    batches = tuple(parser.parse_delays(sdf_file, batch_size=10))
    edges = [e for batch in batches for e in batch]

    # Assert
    assert len(edges) == num_edges

    edge1 = next(e for e in edges if e.dst_node == "u2/A")
    assert edge1.src_node == "u1/Q"
    assert edge1.delay_rise == max_1_rise_fall
    assert edge1.delay_fall == max_1_rise_fall

    edge2 = next(e for e in edges if e.dst_node == "u3/B")
    assert edge2.src_node == "u1/Q"
    assert edge2.delay_rise == max_2_rise
    assert edge2.delay_fall == max_2_fall
