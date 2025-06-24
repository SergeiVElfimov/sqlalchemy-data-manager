import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, User


@pytest.fixture(scope="session")
def sqlite_file_path(tmp_path_factory):
    file_path = tmp_path_factory.mktemp("data") / "sqlalchemy_data_manager.sqlite"
    yield file_path


@pytest.fixture(scope="session")
def database_url(sqlite_file_path) -> str:
    return f"sqlite:///{sqlite_file_path}"


@pytest.fixture(scope="session")
def engine(database_url):
    return create_engine(database_url)


@pytest.fixture(scope="session")
def SessionLocal(engine):
    return sessionmaker(engine, autoflush=True)


@pytest.fixture(scope="function")
def db_session(engine, SessionLocal):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        yield session

    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def users(db_session):
    user_instances = [
        User(
            first_name="User1",
            last_name="User1",
            email="user1@mail.com",
        ),
        User(
            first_name="User2",
            last_name="User2",
            email="user2@mail.com",
        ),
        User(
            first_name="User3",
            last_name="User3",
            email="user3@mail.com",
        ),
    ]
    db_session.add_all(user_instances)
    db_session.commit()
    yield user_instances
