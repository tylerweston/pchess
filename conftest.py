import pytest
import os
from pchess import db
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

pytest_plugins = "docker_compose",
engine = create_engine("postgres://pchess:pchess@db:5432/pchess")
Session = scoped_session(sessionmaker(bind=engine))


@pytest.fixture(scope="function")  # or "module" (to teardown at a module level)
def db_session():
    db.create_all()
    session = Session()
    yield session
    session.close()
    db.Model.metadata.drop_all(bind=engine)