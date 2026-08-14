"""
Test suite for Mergington High School Activities API.

All tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the functionality being tested
- Assert: Verify the results match expectations
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Arrange: No setup needed - activities are already loaded
        Act: Make GET request to /activities
        Assert: Response contains all 9 activities with correct structure
        """
        # Arrange is implicit - activities are loaded in the app
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """
        Arrange: Ready to fetch activities
        Act: Make GET request and retrieve activity data
        Assert: Each activity has all required fields
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert - verify structure of first activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_contains_participants(self, client, reset_activities):
        """
        Arrange: Activities with participants exist
        Act: Fetch activities
        Assert: Participants are correctly listed
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        chess_club_participants = data["Chess Club"]["participants"]
        assert "michael@mergington.edu" in chess_club_participants
        assert "daniel@mergington.edu" in chess_club_participants


class TestRootRedirect:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Client is ready
        Act: Make GET request to root path with follow_redirects=False
        Assert: Returns 307 redirect to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_success(self, client, reset_activities):
        """
        Arrange: Prepare new student email and activity name
        Act: POST signup request for new student
        Assert: Student added to participants and success message returned
        """
        # Arrange
        new_email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {new_email} for {activity}"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert new_email in activities_data[activity]["participants"]
    
    def test_signup_duplicate_student_rejected(self, client, reset_activities):
        """
        Arrange: Use existing participant email from Chess Club
        Act: POST signup request for already-registered student
        Assert: Returns 400 error, participant not added twice
        """
        # Arrange
        existing_email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
        
        # Verify participant count unchanged
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participant_count = activities_data[activity]["participants"].count(existing_email)
        assert participant_count == 1  # Should still be just 1
    
    def test_signup_invalid_activity_rejected(self, client, reset_activities):
        """
        Arrange: Use non-existent activity name
        Act: POST signup request for invalid activity
        Assert: Returns 404 error
        """
        # Arrange
        email = "student@mergington.edu"
        invalid_activity = "Nonexistent Club"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_student_success(self, client, reset_activities):
        """
        Arrange: Use existing participant from Chess Club
        Act: DELETE unregister request for that student
        Assert: Student removed from participants and success message returned
        """
        # Arrange
        email_to_remove = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Pre-verify participant exists
        activities_response = client.get("/activities")
        assert email_to_remove in activities_response.json()[activity]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email_to_remove} from {activity}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email_to_remove not in activities_data[activity]["participants"]
    
    def test_unregister_nonexistent_participant_rejected(self, client, reset_activities):
        """
        Arrange: Use email not registered for the activity
        Act: DELETE unregister request for non-registered student
        Assert: Returns 400 error
        """
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_invalid_activity_rejected(self, client, reset_activities):
        """
        Arrange: Use non-existent activity name
        Act: DELETE unregister request for invalid activity
        Assert: Returns 404 error
        """
        # Arrange
        email = "student@mergington.edu"
        invalid_activity = "Nonexistent Club"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
