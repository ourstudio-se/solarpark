# pylint: skip-file

import os

os.environ["CONNECTIONSTRING_DB"] = "sqlite://"

os.environ["DOMAIN"] = "test"
os.environ["API_AUDIENCE"] = "test"
os.environ["ISSUER"] = "test"
os.environ["ALGORITHMS"] = "RS256"
os.environ["LOOPIA_PASSWORD"] = "test"
os.environ["LOOPIA_EMAIL_FROM"] = "test@test.com"
os.environ["SHARE_PRICE"] = "3000"
os.environ["ALLOW_ORIGINS"] = "test"
os.environ["ECONOMICS_BACKGROUND_BATCH"] = "20"


from dataclasses import dataclass
from typing import Any, Callable

import pytest
from fastapi import BackgroundTasks, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from solarpark.authentication import api_security
from solarpark.persistence.database import Base, get_db
from solarpark.setup import add_routes

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


class FakeBackgroundTasks:
    def __init__(self):
        self.tasks = []

    def add_task(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        pass


@dataclass
class Fixture:
    client: TestClient


@pytest.fixture
def fixture() -> Fixture:
    app = FastAPI()

    add_routes(app)

    client = TestClient(app)

    def fake_auth():
        pass

    def fake_background_tasks():
        FakeBackgroundTasks()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[api_security] = fake_auth
    app.dependency_overrides[BackgroundTasks] = fake_background_tasks

    return Fixture(client=client)
