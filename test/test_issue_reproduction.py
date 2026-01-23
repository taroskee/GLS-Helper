import sqlite3
from contextlib import closing

import pytest

from src.domain.model.edge import Edge
from src.infra.parser.sdf_stream_parser import SDFStreamParser
from src.infra.repository.sqlite_graph_repository import SqliteGraphRepository
from src.usecase.import_sdf import ImportSDFUseCase


@pytest.fixture
def repo_with_data(tmp_path):
    db_path = tmp_path / "repro.db"
    repo = SqliteGraphRepository(str(db_path))
    repo.setup()

    edge = Edge("u_cell_3491.ZN", "net1966", 0.0, 0.0)
    repo.save_edges_batch((edge,))

    return repo


def test_reproduce_sdf_update_mismatch(tmp_path):
    """
    reproducing hierarchy name mismatches (SDF vs. DB)
    and update-logic inconsistencies caused by INTERCONNECT destination pins.
    """
    # Arrange
    db_path = tmp_path / "repro.db"
    repo = SqliteGraphRepository(str(db_path))
    repo.setup()

    initial_edges = [
        Edge(
            src_node="u_cell_3486.A1",
            dst_node="net1966",
            delay_rise=0.0,
            delay_fall=0.0,
        ),
        Edge(
            src_node="u_cell_3491.ZN",
            dst_node="net1966",
            delay_rise=0.0,
            delay_fall=0.0,
        ),
    ]
    repo.save_edges_batch(initial_edges)

    delay_rise = 0.1
    delay_fall = 0.2
    rises = f"({delay_rise}::{delay_rise})"
    falls = f"({delay_fall}::{delay_fall})"
    sdf_content = f"""
(DELAYFILE
  (CELL
    (CELLTYPE "CHIPTOP")
    (INSTANCE)
    (DELAY
      (ABSOLUTE
        (INTERCONNECT CHIPTOP/u_cell_3491/ZN CHIPTOP/u_cell_3486/A1 {rises} {falls})
      )
    )
  )
)
    """
    sdf_file = tmp_path / "test.sdf"
    sdf_file.write_text(sdf_content, encoding="utf-8")

    # Act
    parser = SDFStreamParser()
    use_case = ImportSDFUseCase(repo, parser)
    use_case.execute(sdf_file)

    # Assert
    edges = _fetch_edges(db_path)
    target_edge = next(e for e in edges if e.src_node == "u_cell_3486.A1")

    assert target_edge.delay_rise == delay_rise, (
        f"Expected {delay_rise} but got {target_edge.delay_rise}"
    )
    assert target_edge.delay_fall == delay_fall, (
        f"Expected {delay_fall} but got {target_edge.delay_fall}"
    )


def _fetch_edges(db_path) -> list[Edge]:
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT src, dst, delay_rise, delay_fall FROM edges")
        return [
            Edge(src_node=row[0], dst_node=row[1], delay_rise=row[2], delay_fall=row[3])
            for row in cursor.fetchall()
        ]


def test_anchor_query_works(repo_with_data):
    with sqlite3.connect(repo_with_data.db_path) as conn:
        row = conn.execute(
            "SELECT src, dst FROM edges WHERE src = ?", ("u_cell_3491.ZN",)
        ).fetchone()

    assert row is not None, "Anchor query failed! Source node not found in DB."
    assert row[0] == "u_cell_3491.ZN"
    assert row[1] == "net1966"


def test_fetch_path_string_returns_csv(repo_with_data):
    start = "u_cell_3491.ZN"
    end = "net1966"

    path_str = repo_with_data._fetch_max_delay_path_string(start, end, depth=10)

    assert path_str is not None, (
        "CTE returned None! The recursive query logic is broken."
    )
    assert path_str == "u_cell_3491.ZN,net1966"


def test_reconstruct_edges_works(repo_with_data):
    """【Step 3】CSV文字列から Edge オブジェクトを復元できるか？"""
    path_str = "u_cell_3491.ZN,net1966"

    edges = repo_with_data._reconstruct_edges_from_path(path_str)

    assert len(edges) == 1, "Reconstruction failed! Could not fetch edge from DB."
    assert edges[0].src_node == "u_cell_3491.ZN"
    assert edges[0].dst_node == "net1966"


def test_end_to_end(repo_with_data):
    path = repo_with_data.find_max_delay_path("u_cell_3491.ZN", "net1966")

    assert path is not None
    assert len(path) == 1
    assert path[0].dst_node == "net1966"
