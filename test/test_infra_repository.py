import sqlite3
from time import perf_counter

from src.domain.model.edge import Edge
from src.domain.model.node import Node
from src.infra.repository.sqlite_graph_repository import SqliteGraphRepository


def test_repository_setup_creates_tables(tmp_path):
    """Verify that setup() creates the necessary tables."""
    # Arrange: Use a temporary path for the DB
    db_path = tmp_path / "test_gls.db"
    repo = SqliteGraphRepository(str(db_path))

    # Act
    repo.setup()

    # Assert
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes';"
        )
        assert cursor.fetchone() is not None, "nodes table should exist"

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='edges';"
        )
        assert cursor.fetchone() is not None, "edges table should exist"


def test_save_nodes_batch_inserts_data(tmp_path):
    """Verify that save_nodes_batch inserts multiple records correctly."""
    # Arrange
    db_path = tmp_path / "test_gls.db"
    repo = SqliteGraphRepository(str(db_path))
    repo.setup()

    nodes = [Node(name="top.cpu.u1"), Node(name="top.cpu.u2"), Node(name="top.mem.u3")]

    # Act
    repo.save_nodes_batch(nodes)

    # Assert
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT count(*) FROM nodes")
        assert cursor.fetchone()[0] == len(nodes)

        cursor.execute("SELECT name FROM nodes ORDER BY name")
        names = [row[0] for row in cursor.fetchall()]
        assert names == ["top.cpu.u1", "top.cpu.u2", "top.mem.u3"]


def test_save_nodes_batch_performance(tmp_path):
    """
    Performance Test:
    Ensures that bulk insert handles 1,000,000 records within a reasonable time.
    If 'executemany' is implemented correctly, this should take less than 1 second.
    If implemented with a loop, it would take > 60 seconds.
    """
    # Arrange
    db_path = tmp_path / "perf_test.db"
    repo = SqliteGraphRepository(str(db_path))
    repo.setup()

    node_count = 1_000_000
    nodes = [Node(name=f"top.module.u{i}") for i in range(node_count)]

    # Act
    start_time = perf_counter()
    repo.save_nodes_batch(nodes)
    duration = perf_counter() - start_time

    # Assert
    threshold_seconds = 2.0
    print(f"\n[Performance] Inserted {node_count} records in {duration:.4f} seconds.")
    assert duration < threshold_seconds, (
        f"Performance regression detected! "
        f"Took {duration:.4f}s for {node_count} records (over {threshold_seconds}s)"
    )


def test_save_edges_batch_inserts_data(tmp_path):
    """Verify that save_edges_batch inserts edge records correctly."""
    # Arrange
    db_path = tmp_path / "test_gls_edges.db"
    repo = SqliteGraphRepository(str(db_path))
    repo.setup()

    edges = [
        Edge(src_node="top.u1.Y", dst_node="top.u2.A", delay_rise=0.1, delay_fall=0.08),
        Edge(src_node="top.u1.Y", dst_node="top.u3.B", delay_rise=0.2, delay_fall=0.18),
    ]

    # Act
    repo.save_edges_batch(edges)

    # Assert
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT src, dst, delay_rise, delay_fall FROM edges ORDER BY dst"
        )
        rows = cursor.fetchall()

        assert len(rows) == len(edges)
        assert rows[0] == ("top.u1.Y", "top.u2.A", 0.1, 0.08)
        assert rows[1] == ("top.u1.Y", "top.u3.B", 0.2, 0.18)


def test_save_edges_batch_performance(tmp_path):
    """
    Performance Test:
    Ensures that bulk insert handles 1,000,000 records within a reasonable time.
    Must also verify that data is ACTUALLY saved.
    """
    time_threshold = 2.0

    # Arrange
    db_path = tmp_path / "perf_test_edges.db"
    repo = SqliteGraphRepository(str(db_path))
    repo.setup()

    edge_count = 1_000_000
    edges = [
        Edge(src_node=f"u{i}.Y", dst_node=f"u{i + 1}.A", delay_rise=0.1, delay_fall=0.1)
        for i in range(edge_count)
    ]

    # Act
    start_time = perf_counter()
    repo.save_edges_batch(edges)
    duration = perf_counter() - start_time

    # Assert 1: Time
    print(f"\n[Performance] Inserted {edge_count} edges in {duration:.4f} seconds.")
    assert duration < time_threshold, f"Too slow! Took {duration:.4f}s"

    # Assert 2: Correctness
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM edges")
        actual_count = cursor.fetchone()[0]
        assert actual_count == edge_count, f"Expected {edge_count}, got {actual_count}"
