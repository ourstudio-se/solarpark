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
def update_member():
    return {
        "bank": "string",
        "birth_date": "2023-11-08T09:57:48.506Z",
        "email": "test@test.com",
        "firstname": "Test",
        "lastname": "Tester",
        "street_address": "Test street 2",
        "swish": "string",
        "telephone": "123456",
        "year": "2023-01-01T00:00:00.000Z",
        "zip_code": "12345",
    }


def test_create_member(fixture: Fixture, create_member):
    response = fixture.client.post("/members", json=create_member)
    assert response.status_code == 200
    assert response.json()["data"]["firstname"] == "Test"
    assert response.json()["data"]["lastname"] == "Tester"
    assert response.json()["data"]["created_at"] is not None


def test_update_member(fixture: Fixture, update_member):
    response = fixture.client.put("/members/1", json=update_member)
    assert response.status_code == 200
    assert response.json()["data"]["firstname"] == "Test"
    assert response.json()["data"]["lastname"] == "Tester"
    assert response.json()["data"]["street_address"] == "Test street 2"
    assert response.json()["data"]["created_at"] is not None
    assert response.json()["data"]["updated_at"] is not None


def test_get_member(fixture: Fixture):
    response = fixture.client.get("/members/1")
    assert response.status_code == 200


def test_get_member_does_not_exist(fixture: Fixture):
    response = fixture.client.get("/members/3")
    assert response.status_code == 404


def test_delete_member(fixture: Fixture):
    response = fixture.client.delete("/members/1")
    assert response.status_code == 200
