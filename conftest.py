import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError

from pchess import db


@pytest.fixture(scope='session', autouse=True)
def create_database():
    """
    One thing I'm not sure about si whether this will always run
    first, and it has to run first.
    """
    engine = create_engine('postgres://pchess:pchess@db:5432/pchess')
    db_name = 'postgres://pchess:pchess@db:5432/pchess'
    conn = engine.connect()
    conn.execute('commit')
    try:
        conn.execute('CREATE DATABASE %s;' % db_name)
        print('CREATE DATABASE %s;' % db_name)
    except ProgrammingError:
        print('Database %s already exists' % db_name)
        pass


@pytest.fixture(scope='session', autouse=True)
def drop_db():
    db.drop_all()
    db.create_all()


@pytest.fixture(scope='function', autouse=True)
def session():
    db.session.begin_nested()
    yield db.session
    db.session.rollback()
    db.session.remove()