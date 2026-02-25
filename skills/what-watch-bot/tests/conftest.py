import pytest
import sqlite3
from typing import Generator
from src.database import _init_db

@pytest.fixture
def mock_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Fixture that provides an isolated in-memory SQLite database connection.
    Follows Pattern 2 from python-testing-patterns.
    """
    # Arrange: Setup in-memory DB mimicking the actual DB initialization
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    _init_db(conn)

    # Act: Provide to test
    yield conn

    # Teardown: Clean up
    conn.close()
