import os
import tempfile
import pytest
from pchess import app


# pytest-flask
# and
# pytest-flask-sqlalchemy

@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            app.init_db()
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def test_empty_db(client):
    # Test we start with an empty database
    rv = client.get("/get_current_board")
    assert b"No current board" in rv.data
