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

        # 件数確認
        cursor.execute("SELECT count(*) FROM nodes")
        assert cursor.fetchone()[0] == 3

        # 内容確認 (順不同なのでsetで比較、またはORDER BY)
        cursor.execute("SELECT name FROM nodes ORDER BY name")
        names = [row[0] for row in cursor.fetchall()]
        assert names == ["top.cpu.u1", "top.cpu.u2", "top.mem.u3"]
