import time

import sqlite3

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
        assert cursor.fetchone()[0] == 3

        cursor.execute("SELECT name FROM nodes ORDER BY name")
        names = [row[0] for row in cursor.fetchall()]
        assert names == ["top.cpu.u1", "top.cpu.u2", "top.mem.u3"]


def test_save_nodes_batch_performance(tmp_path):
    """
    Performance Test:
    Ensures that bulk insert handles 100,000 records within a reasonable time (e.g., < 2.0s).
    If 'executemany' is implemented correctly, this should take less than 1 second.
    If implemented with a loop, it would take > 60 seconds.
    """
    # Arrange
    db_path = tmp_path / "perf_test.db"
    repo = SqliteGraphRepository(str(db_path))
    repo.setup()

    # 10万件のダミーデータを生成 (この時間は計測に含めない)
    node_count = 1_000_000
    nodes = [Node(name=f"top.module.u{i}") for i in range(node_count)]

    # Act: 計測開始
    start_time = time.perf_counter()

    repo.save_nodes_batch(nodes)

    end_time = time.perf_counter()
    # Act: 計測終了

    # Assert
    duration = end_time - start_time
    threshold_seconds = 2.0  # Docker環境でも余裕を持ってクリアできるライン

    print(f"\n[Performance] Inserted {node_count} records in {duration:.4f} seconds.")

    assert duration < threshold_seconds, (
        f"Performance regression detected! "
        f"Took {duration:.4f}s for {node_count} records (Threshold: {threshold_seconds}s)"
    )
