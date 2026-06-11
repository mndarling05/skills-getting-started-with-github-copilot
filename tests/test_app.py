"""Test suite for Mergington High School API endpoints."""

import pytest
from src.app import activities


class TestRootEndpoint:
    """Tests for the root endpoint."""

    @pytest.mark.asyncio
    async def test_root_redirect(self, async_client):
        """Root endpoint should redirect to static index.html"""
        response = await async_client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities listing endpoint."""

    @pytest.mark.asyncio
    async def test_get_activities(self, async_client):
        """GET /activities should return all activities with correct schema."""
        response = await async_client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        
        # Verify all expected activities are present
        expected_activities = {
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Yoga Club", "Art Workshop", "Photography Club", "Debate Team", "Science Club"
        }
        assert set(data.keys()) == expected_activities
        
        # Verify activity schema
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)

    @pytest.mark.asyncio
    async def test_get_activities_chess_club_initial_state(self, async_client):
        """Verify Chess Club has expected initial participants."""
        response = await async_client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for the signup endpoint."""

    @pytest.mark.asyncio
    async def test_signup_success(self, async_client):
        """POST /activities/{name}/signup should add student and return 200."""
        # Clear participants to start fresh for this test
        activities["Chess Club"]["participants"] = ["michael@mergington.edu"]
        
        response = await async_client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, async_client):
        """POST signup with already-enrolled student should return 400."""
        response = await async_client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]

    @pytest.mark.asyncio
    async def test_signup_invalid_activity(self, async_client):
        """POST signup to non-existent activity should return 404."""
        response = await async_client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestDeleteParticipantEndpoint:
    """Tests for the delete participant endpoint."""

    @pytest.mark.asyncio
    async def test_delete_participant_success(self, async_client):
        """DELETE /activities/{name}/participants/{email} should remove participant."""
        # Ensure participant exists
        activities["Yoga Club"]["participants"] = ["alex@mergington.edu", "test@mergington.edu"]
        
        response = await async_client.delete(
            "/activities/Yoga Club/participants/test@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "Removed" in data["message"]
        assert "test@mergington.edu" in data["message"]
        
        # Verify participant was removed
        assert "test@mergington.edu" not in activities["Yoga Club"]["participants"]
        assert "alex@mergington.edu" in activities["Yoga Club"]["participants"]

    @pytest.mark.asyncio
    async def test_delete_participant_invalid_activity(self, async_client):
        """DELETE from non-existent activity should return 404."""
        response = await async_client.delete(
            "/activities/Nonexistent Activity/participants/student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_participant_not_found(self, async_client):
        """DELETE non-existent participant should return 404."""
        response = await async_client.delete(
            "/activities/Chess Club/participants/nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Participant not found" in data["detail"]
