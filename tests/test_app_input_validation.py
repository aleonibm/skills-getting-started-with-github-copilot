import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities_state():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_signup_requires_email_query_param(client):
    # Arrange

    # Act
    response = client.post("/activities/Chess%20Club/signup")
    payload = response.json()

    # Assert
    assert response.status_code == 422
    assert payload["detail"][0]["loc"] == ["query", "email"]


def test_unregister_requires_email_query_param(client):
    # Arrange

    # Act
    response = client.delete("/activities/Chess%20Club/participants")
    payload = response.json()

    # Assert
    assert response.status_code == 422
    assert payload["detail"][0]["loc"] == ["query", "email"]


def test_signup_allows_empty_string_email_with_current_behavior(client):
    # Arrange
    activity_name = "Chess Club"
    before_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": ""})

    # Assert
    assert response.status_code == 200
    assert len(activities[activity_name]["participants"]) == before_count + 1
    assert "" in activities[activity_name]["participants"]


def test_signup_allows_non_email_format_with_current_behavior(client):
    # Arrange
    activity_name = "Gym Class"
    unusual_value = "not-an-email"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": unusual_value}
    )

    # Assert
    assert response.status_code == 200
    assert unusual_value in activities[activity_name]["participants"]


def test_signup_treats_whitespace_variant_as_different_participant(client):
    # Arrange
    activity_name = "Programming Class"
    existing_email = activities[activity_name]["participants"][0]
    whitespace_variant = f"  {existing_email}  "

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": whitespace_variant}
    )

    # Assert
    assert response.status_code == 200
    assert whitespace_variant in activities[activity_name]["participants"]


def test_unregister_unknown_activity_still_returns_404(client):
    # Arrange

    # Act
    response = client.delete(
        "/activities/Nonexistent%20Activity/participants",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
