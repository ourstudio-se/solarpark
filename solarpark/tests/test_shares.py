# pylint: disable=W0621

import pytest

from solarpark.tests.conftest import Fixture


@pytest.fixture
def create_member():
    return {
        "bank": "",
        "birth_date": "2023-11-08T09:57:48.506Z",
        "email": "test@test.com",
        "firstname": "Test",
        "lastname": "Tester",
        "street_address": "Test street 1",
        "swish": "",
        "telephone": "123456",
        "year": "2023-01-01T00:00:00.000Z",
        "zip_code": "12345",
    }


@pytest.fixture
def create_share():
    return {
        "comment": "test",
        "purchased_at": "2023-11-08T09:57:48.506Z",
        "member_id": "1",
        "initial_value": "3000",
        "from_internal_account": "false",
    }


@pytest.fixture
def update_share():
    return {
        "comment": "test update",
        "purchased_at": "2023-11-08T09:57:48.506Z",
        "member_id": "1",
        "initial_value": "3000",
        "current_value": "2000",
        "from_internal_account": "false",
    }


def test_create_member(fixture: Fixture, create_member):
    response = fixture.client.post("/members", json=create_member)
    assert response.status_code == 200
    assert response.json()["data"]["firstname"] == "Test"
    assert response.json()["data"]["lastname"] == "Tester"
    assert response.json()["data"]["created_at"] is not None


def test_create_share(fixture: Fixture, create_share):
    response = fixture.client.post("/shares", json=create_share)
    assert response.status_code == 200
    assert response.json()["data"]["comment"] == "test"
    assert response.json()["data"]["from_internal_account"] == 0
    assert response.json()["data"]["initial_value"] == 3000


def test_update_share(fixture: Fixture, update_share):
    response = fixture.client.put("/shares/1", json=update_share)
    assert response.status_code == 200
    assert response.json()["data"]["comment"] == "test update"
    assert response.json()["data"]["from_internal_account"] == 0
    assert response.json()["data"]["initial_value"] == 3000
    assert response.json()["data"]["current_value"] == 2000


def test_get_share(fixture: Fixture):
    response = fixture.client.get("/shares/1")
    assert response.status_code == 200
    assert response.json()["data"]["comment"] == "test update"
    assert response.json()["data"]["from_internal_account"] == 0
    assert response.json()["data"]["initial_value"] == 3000
    assert response.json()["data"]["current_value"] == 2000
