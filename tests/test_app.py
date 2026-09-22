from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

INITIAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities_returns_activity_catalog():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_email():
    activity_name = "Soccer Club"
    email = "student@example.com"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_for_unknown_activity_returns_404():
    response = client.post("/activities/Unknown Activity/signup?email=student@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_email():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_for_unregistered_student_returns_404():
    activity_name = "Soccer Club"
    email = "student@example.com"

    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
