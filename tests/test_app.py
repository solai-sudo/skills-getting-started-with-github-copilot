import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities

# Original activities data for resetting
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team for practice and matches",
        "schedule": "Mondays, Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Swim laps, learn techniques, and improve endurance",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Drama Club": {
        "description": "Perform in school plays and explore acting, stagecraft, and storytelling",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["lily@mergington.edu", "chloe@mergington.edu"]
    },
    "Art Workshop": {
        "description": "Create art projects in drawing, painting, and mixed media",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["jack@mergington.edu", "ella@mergington.edu"]
    },
    "Robotics Club": {
        "description": "Design, build, and program robots for competitions",
        "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["ethan@mergington.edu", "noah.r@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills in competitive debates",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    }
}


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before and after each test."""
    original = copy.deepcopy(ORIGINAL_ACTIVITIES)
    activities.clear()
    activities.update(original)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    """Create a TestClient instance for the FastAPI app."""
    return TestClient(app)


def test_get_activities(client):
    """Test GET /activities returns all activities."""
    # Arrange
    # (Client fixture provides the TestClient)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert len(data["Chess Club"]["participants"]) == 2
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in data["message"]

    # Verify participant was added
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert email in activities_data[activity]["participants"]


def test_signup_duplicate(client):
    """Test signup fails when student is already signed up."""
    # Arrange
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_activity_full(client):
    """Test signup fails when activity is at max capacity."""
    # Arrange
    activity = "Chess Club"  # Max 12, starts with 2
    # Fill to max
    for i in range(10):
        email = f"test{i}@mergington.edu"
        client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act - Try to add one more
    email = "last@mergington.edu"
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "full" in data["detail"]


def test_signup_invalid_activity(client):
    """Test signup fails for non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    activity = "Nonexistent Activity"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]


def test_unregister_success(client):
    """Test successful unregister from an activity."""
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    assert email in data["message"]

    # Verify participant was removed
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert email not in activities_data[activity]["participants"]


def test_unregister_not_signed_up(client):
    """Test unregister fails when student is not signed up."""
    # Arrange
    email = "notsigned@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_unregister_invalid_activity(client):
    """Test unregister fails for non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    activity = "Nonexistent Activity"

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]