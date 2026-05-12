import copy
import pytest
from fastapi.testclient import TestClient
import src.app as app_module

client = TestClient(app_module.app)

original_activities = copy.deepcopy(app_module.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))
    yield


def test_root_redirect():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities():
    # Arrange
    expected_activities = ["Chess Club", "Programming Class"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    for activity in expected_activities:
        assert activity in data


def test_signup_for_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "test@example.com"
    params = {"email": email}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=params)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity_name}"


def test_signup_missing_email_parameter():
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["detail"]
    assert any(error["loc"][-1] == "email" for error in data["detail"])


def test_signup_already_signed_up():
    # Arrange
    activity_name = "Programming Class"
    email = "duplicate@example.com"
    params = {"email": email}
    client.post(f"/activities/{activity_name}/signup", params=params)

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=params)

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up"


def test_signup_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test@example.com"
    params = {"email": email}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=params)

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_remove_participant():
    # Arrange
    activity_name = "Gym Class"
    email = "remove@example.com"
    signup_params = {"email": email}
    client.post(f"/activities/{activity_name}/signup", params=signup_params)

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Removed {email} from {activity_name}"


def test_remove_participant_not_found():
    # Arrange
    activity_name = "Gym Class"
    email = "nonexistent@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Participant not found"


def test_remove_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"