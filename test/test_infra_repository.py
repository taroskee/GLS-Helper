import sqlite3
from contextlib import closing

from src.domain.model.edge import Edge
from src.domain.model.node import Node
from src.infra.repository.sqlite_graph_repository import SqliteGraphRepository


def test_repository_setup_creates_tables(tmp_path):
    """Verify that setup() creates the necessary tables."""
    # Arrange
    db_path = tmp_path / "test_gls.db"
    repo = SqliteGraphRepository(str(db_path))

    # Act
    repo.setup()

    # Assert
    with closing(sqlite3.connect(db_path)) as conn:
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
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM nodes")
        assert cursor.fetchone()[0] == len(nodes)

        cursor.execute("SELECT name FROM nodes ORDER BY name")
        names = [row[0] for row in cursor.fetchall()]
        assert names == ["top.cpu.u1", "top.cpu.u2", "top.mem.u3"]


def test_save_nodes_batch_performance(tmp_path, benchmark):
    """
    Performance Test for Nodes using pytest-benchmark.
    """
    # Arrange
    db_path = tmp_path / "perf_test_nodes.db"
    repo = SqliteGraphRepository(str(db_path))
    repo.setup()

    node_count = 100_000
    nodes = [Node(name=f"top.module.u{i}") for i in range(node_count)]

    # Act & Measure
    benchmark(repo.save_nodes_batch, nodes)

    # Assert Correctness
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM nodes")
        actual_count = cursor.fetchone()[0]
        assert actual_count >= node_count


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
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT src, dst, delay_rise, delay_fall FROM edges ORDER BY dst"
        )
        rows = cursor.fetchall()

        assert len(rows) == len(edges)
        assert rows[0] == ("top.u1.Y", "top.u2.A", 0.1, 0.08)
        assert rows[1] == ("top.u1.Y", "top.u3.B", 0.2, 0.18)


def test_save_edges_batch_performance(tmp_path, benchmark):
    """
    Performance Test using pytest-benchmark.
    """
    # Arrange
    db_path = tmp_path / "perf_test_edges.db"
    repo = SqliteGraphRepository(str(db_path))
    repo.setup()

    edge_count = 100_000
    edges = [
        Edge(src_node=f"u{i}.Y", dst_node=f"u{i + 1}.A", delay_rise=0.1, delay_fall=0.1)
        for i in range(edge_count)
    ]

    # Act & Measure
    repo.save_edges_batch(edges)  # Warming up

    benchmark(repo.save_edges_batch, edges)

    # Assert correctness
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM edges")
        assert cursor.fetchone()[0] >= edge_count


def test_update_edges_delay_batch_updates_existing_records(tmp_path):
    """Verify that update_edges_delay_batch correctly updates delay values."""
    # Arrange
    db_path = tmp_path / "test_delay_update.db"
    repo = SqliteGraphRepository(str(db_path))
    repo.setup()
    initial_edges = [
        Edge(src_node="u1.Q", dst_node="u2.A", delay_rise=0.0, delay_fall=0.0),
        Edge(src_node="u1.Q", dst_node="u3.B", delay_rise=0.0, delay_fall=0.0),
        Edge(src_node="u1.Q", dst_node="u4.C", delay_rise=0.0, delay_fall=0.0),
    ]
    repo.save_edges_batch(initial_edges)
    updates = [
        Edge(src_node="u1.Q", dst_node="u2.A", delay_rise=0.1, delay_fall=0.15),
        Edge(src_node="u1.Q", dst_node="u4.C", delay_rise=0.2, delay_fall=0.25),
    ]

    # Act
    repo.update_edges_delay_batch(updates)

    # Assert
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT dst, delay_rise, delay_fall FROM edges WHERE src='u1.Q' ORDER BY dst"
        )
        rows = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

        assert rows["u2.A"] == (0.1, 0.15)
        assert rows["u3.B"] == (0.0, 0.0)
        assert rows["u4.C"] == (0.2, 0.25)
