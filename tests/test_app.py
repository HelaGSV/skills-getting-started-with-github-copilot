"""
Tests for the Mergington High School API

Tests for activities endpoints, signup functionality, and unregister functionality.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original activities
    original_activities = {
        "Soccer Team": {
            "description": "Competitive soccer team practicing skills and participating in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Pickup games, drills, and intramural competitions",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["oliver@mergington.edu", "logan@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu", "isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops, rehearsals, and school productions",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["mia@mergington.edu", "charlotte@mergington.edu"]
        },
        "Math Club": {
            "description": "Problem solving, competitions, and math exploration",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu", "elijah@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Hands-on science challenges and team competitions",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["scarlett@mergington.edu", "grace@mergington.edu"]
        },
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
        }
    }
    
    from app import activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities_data = response.json()
        assert len(activities_data) == 9
        assert "Soccer Team" in activities_data
        assert "Basketball Club" in activities_data
    
    def test_get_activities_contains_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_details in activities_data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
    
    def test_get_activities_initial_participants(self, client, reset_activities):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        activities_data = response.json()
        
        soccer = activities_data["Soccer Team"]
        assert len(soccer["participants"]) == 2
        assert "liam@mergington.edu" in soccer["participants"]
        assert "noah@mergington.edu" in soccer["participants"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Soccer Team/signup",
            params={"email": "john.doe@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert "john.doe@mergington.edu" in response.json()["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        client.post(
            "/activities/Soccer Team/signup",
            params={"email": "jane.smith@mergington.edu"}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        activities_data = response.json()
        assert "jane.smith@mergington.edu" in activities_data["Soccer Team"]["participants"]
    
    def test_signup_duplicate_fails(self, client, reset_activities):
        """Test that signing up twice fails"""
        # First signup
        client.post(
            "/activities/Soccer Team/signup",
            params={"email": "test@mergington.edu"}
        )
        
        # Second signup should fail
        response = client.post(
            "/activities/Soccer Team/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities"""
        email = "multi@mergington.edu"
        
        response1 = client.post(
            "/activities/Soccer Team/signup",
            params={"email": email}
        )
        response2 = client.post(
            "/activities/Basketball Club/signup",
            params={"email": email}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        activities_data = response.json()
        assert email in activities_data["Soccer Team"]["participants"]
        assert email in activities_data["Basketball Club"]["participants"]


class TestRootRedirect:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestActivityDetails:
    """Tests for activity details and constraints"""
    
    def test_activity_has_max_participants(self, client, reset_activities):
        """Test that activities have max_participants constraint"""
        response = client.get("/activities")
        activities_data = response.json()
        
        chess_club = activities_data["Chess Club"]
        assert chess_club["max_participants"] == 12
    
    def test_activity_spot_calculation(self, client, reset_activities):
        """Test that spots available can be calculated correctly"""
        response = client.get("/activities")
        activities_data = response.json()
        
        soccer = activities_data["Soccer Team"]
        spots_left = soccer["max_participants"] - len(soccer["participants"])
        assert spots_left == 16  # 18 max - 2 current


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
