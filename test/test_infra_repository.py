import sqlite3

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

        # Check for nodes table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes';"
        )
        assert cursor.fetchone() is not None, "nodes table should exist"

        # Check for edges table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='edges';"
        )
        assert cursor.fetchone() is not None, "edges table should exist"
