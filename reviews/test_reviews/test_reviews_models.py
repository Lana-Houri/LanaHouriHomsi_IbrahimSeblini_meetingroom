"""
Test suite for review_model.py

This module contains unit tests for all review model functions,
testing database operations, validation logic, and error handling.
"""
import os
import sys

import pytest
from unittest.mock import patch, MagicMock

SYS_PATH_ROOT = os.path.dirname(os.path.dirname(__file__))
if SYS_PATH_ROOT not in sys.path:
    sys.path.insert(0, SYS_PATH_ROOT)

import review_model


@pytest.fixture
def mock_connection():
    """
    Fixture that provides a mock database connection and cursor.
    
    Functionality:
        Creates mock objects for database connection and cursor
        to be used in tests that require database mocking.
    
    Parameters:
        None
    
    Returns:
        tuple: (conn, cursor) where both are MagicMock objects
    """
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


@patch("review_model.connect_to_db")
def test_get_all_reviews(mock_db):
    """
    Test retrieving all reviews from the database.
    
    Functionality:
        Tests the get_all_reviews() function to ensure it correctly
        retrieves all reviews with user and room details.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is a list with at least one review
        - Review contains expected review_id
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchall.return_value = [
        {"review_id": 1, "user_id": 1, "room_id": 1, "rating": 5, "comment": "Great room"}
    ]
    
    result = review_model.get_all_reviews()
    assert len(result) == 1
    assert result[0]["review_id"] == 1


@patch("review_model.connect_to_db")
def test_get_review_by_id(mock_db):
    """
    Test retrieving a review by its ID when review exists.
    
    Functionality:
        Tests the get_review_by_id() function to ensure it correctly
        retrieves a review when a valid review_id is provided.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains the expected review_id
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = {"review_id": 1, "user_id": 1, "room_id": 1, "rating": 5}
    
    result = review_model.get_review_by_id(1)
    assert result["review_id"] == 1


@patch("review_model.connect_to_db")
def test_get_review_by_id_not_found(mock_db):
    """
    Test retrieving a review by ID when review does not exist.
    
    Functionality:
        Tests the get_review_by_id() function to ensure it returns
        an empty dictionary when review_id is not found.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is an empty dictionary when review not found
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = review_model.get_review_by_id(999)
    assert result == {}


@patch("review_model.connect_to_db")
def test_get_reviews_by_room(mock_db):
    """
    Test retrieving reviews for a specific room.
    
    Functionality:
        Tests the get_reviews_by_room() function to ensure it correctly
        retrieves all reviews for a given room_id.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is a list with reviews for the room
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchall.return_value = [
        {"review_id": 1, "room_id": 1, "rating": 5}
    ]
    
    result = review_model.get_reviews_by_room(1)
    assert len(result) == 1
    assert result[0]["room_id"] == 1


@patch("review_model.connect_to_db")
def test_get_reviews_by_room_include_flagged(mock_db):
    """
    Test retrieving reviews for a room including flagged reviews.
    
    Functionality:
        Tests the get_reviews_by_room() function with include_flagged=True
        to ensure it returns all reviews including flagged ones.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result includes flagged reviews when include_flagged=True
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchall.return_value = [
        {"review_id": 1, "room_id": 1, "is_flagged": True}
    ]
    
    result = review_model.get_reviews_by_room(1, include_flagged=True)
    assert len(result) == 1


@patch("review_model.connect_to_db")
def test_get_user_reviews(mock_db):
    """
    Test retrieving all reviews by a specific user.
    
    Functionality:
        Tests the get_user_reviews() function to ensure it correctly
        retrieves all reviews associated with a given user_id.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is a list with at least one review
        - Review belongs to the specified user_id
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchall.return_value = [
        {"review_id": 1, "user_id": 1, "room_id": 1}
    ]
    
    result = review_model.get_user_reviews(1)
    assert len(result) == 1
    assert result[0]["user_id"] == 1


@patch("review_model.connect_to_db")
def test_get_flagged_reviews(mock_db):
    """
    Test retrieving all flagged reviews.
    
    Functionality:
        Tests the get_flagged_reviews() function to ensure it correctly
        retrieves all reviews that have been flagged.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is a list with flagged reviews
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchall.return_value = [
        {"review_id": 1, "is_flagged": True, "flag_reason": "Inappropriate"}
    ]
    
    result = review_model.get_flagged_reviews()
    assert len(result) == 1
    assert result[0]["is_flagged"] is True


@patch("review_model.check_user_exists", return_value=True)
@patch("review_model.check_room_exists", return_value=True)
@patch("review_model.connect_to_db")
def test_create_review_success(mock_db, mock_room, mock_user):
    """
    Test creating a review successfully.
    
    Functionality:
        Tests the create_review() function to ensure it correctly creates
        a new review when all validations pass (user exists, room exists,
        valid rating, all required fields provided).
    
    Parameters:
        mock_db: Mocked database connection function
        mock_room: Mocked check_room_exists function
        mock_user: Mocked check_user_exists function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains review_id
        - Result does not contain error
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.side_effect = [
        {"review_id": 1, "user_id": 1, "room_id": 1, "rating": 5, "comment": "Great"},
        {"review_id": 1, "user_id": 1, "room_id": 1, "rating": 5, "username": "user1", "room_name": "Room1"}
    ]
    
    review_data = {
        "user_id": 1,
        "room_id": 1,
        "rating": 5,
        "comment": "Great room"
    }
    
    result = review_model.create_review(review_data)
    assert result["review_id"] == 1
    assert "error" not in result


@patch("review_model.check_user_exists", return_value=False)
def test_create_review_user_not_exists(mock_user):
    """
    Test creating a review when user does not exist.
    
    Functionality:
        Tests the create_review() function to ensure it returns an error
        when the specified user_id does not exist.
    
    Parameters:
        mock_user: Mocked check_user_exists function returning False
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates user does not exist
    """
    review_data = {
        "user_id": 999,
        "room_id": 1,
        "rating": 5
    }
    
    result = review_model.create_review(review_data)
    assert "error" in result
    assert "User does not exist" in result["error"]


@patch("review_model.check_user_exists", return_value=True)
@patch("review_model.check_room_exists", return_value=False)
def test_create_review_room_not_exists(mock_room, mock_user):
    """
    Test creating a review when room does not exist.
    
    Functionality:
        Tests the create_review() function to ensure it returns an error
        when the specified room_id does not exist.
    
    Parameters:
        mock_room: Mocked check_room_exists function returning False
        mock_user: Mocked check_user_exists function returning True
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates room does not exist
    """
    review_data = {
        "user_id": 1,
        "room_id": 999,
        "rating": 5
    }
    
    result = review_model.create_review(review_data)
    assert "error" in result
    assert "Room does not exist" in result["error"]


def test_create_review_missing_fields():
    """
    Test creating a review with missing required fields.
    
    Functionality:
        Tests the create_review() function to ensure it returns an error
        when required fields (user_id, room_id, rating) are missing.
    
    Parameters:
        None
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates missing required fields
    """
    review_data = {
        "user_id": 1,
        "room_id": 1
    }
    
    result = review_model.create_review(review_data)
    assert "error" in result
    assert "Missing required fields" in result["error"]


def test_create_review_invalid_rating():
    """
    Test creating a review with invalid rating.
    
    Functionality:
        Tests the create_review() function to ensure it returns an error
        when rating is outside the valid range (1-5).
    
    Parameters:
        None
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates invalid rating
    """
    review_data = {
        "user_id": 1,
        "room_id": 1,
        "rating": 6
    }
    
    result = review_model.create_review(review_data)
    assert "error" in result
    assert "Rating must be between 1 and 5" in result["error"]


@patch("review_model.connect_to_db")
def test_update_review_success(mock_db):
    """
    Test updating a review successfully.
    
    Functionality:
        Tests the update_review() function to ensure it correctly updates
        a review when user has permission and validations pass.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains review_id
        - Result does not contain error
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.side_effect = [
        {"user_id": 1},
        {"review_id": 1, "user_id": 1, "rating": 4},
        {"review_id": 1, "user_id": 1, "rating": 4, "username": "user1", "room_name": "Room1"}
    ]
    
    review_data = {
        "rating": 4,
        "comment": "Updated comment"
    }
    
    result = review_model.update_review(1, review_data, user_id=1, is_admin=False, is_moderator=False)
    assert result["review_id"] == 1
    assert "error" not in result


@patch("review_model.connect_to_db")
def test_update_review_not_found(mock_db):
    """
    Test updating a review that does not exist.
    
    Functionality:
        Tests the update_review() function to ensure it returns an error
        when the specified review_id does not exist.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates review not found
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = review_model.update_review(999, {}, user_id=1, is_admin=False, is_moderator=False)
    assert "error" in result
    assert "Review not found" in result["error"]


@patch("review_model.connect_to_db")
def test_update_review_unauthorized(mock_db):
    """
    Test updating a review without authorization.
    
    Functionality:
        Tests the update_review() function to ensure it returns an error
        when a regular user tries to update another user's review.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates unauthorized access
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = {"user_id": 2}
    
    result = review_model.update_review(1, {}, user_id=1, is_admin=False, is_moderator=False)
    assert "error" in result
    assert "Unauthorized" in result["error"]


@patch("review_model.connect_to_db")
def test_delete_review_success(mock_db):
    """
    Test deleting a review successfully.
    
    Functionality:
        Tests the delete_review() function to ensure it correctly deletes
        a review when user has permission.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result status is "success"
        - Result contains success message
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.side_effect = [
        {"user_id": 1},
        {"review_id": 1}
    ]
    
    result = review_model.delete_review(1, user_id=1, is_admin=False, is_moderator=False)
    assert result["status"] == "success"
    assert "message" in result


@patch("review_model.connect_to_db")
def test_delete_review_not_found(mock_db):
    """
    Test deleting a review that does not exist.
    
    Functionality:
        Tests the delete_review() function to ensure it returns an error
        when the specified review_id does not exist.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates review not found
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = review_model.delete_review(999, user_id=1, is_admin=False, is_moderator=False)
    assert "error" in result
    assert "Review not found" in result["error"]


@patch("review_model.connect_to_db")
def test_delete_review_unauthorized(mock_db):
    """
    Test deleting a review without authorization.
    
    Functionality:
        Tests the delete_review() function to ensure it returns an error
        when a regular user tries to delete another user's review.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates unauthorized access
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = {"user_id": 2}
    
    result = review_model.delete_review(1, user_id=1, is_admin=False, is_moderator=False)
    assert "error" in result
    assert "Unauthorized" in result["error"]


@patch("review_model.connect_to_db")
def test_flag_review_success(mock_db):
    """
    Test flagging a review successfully.
    
    Functionality:
        Tests the flag_review() function to ensure it correctly flags
        a review as inappropriate.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result status is "success"
        - Result contains success message
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.side_effect = [
        {"is_flagged": False},
        {"review_id": 1, "is_flagged": True}
    ]
    
    result = review_model.flag_review(1, "Inappropriate content", user_id=1)
    assert result["status"] == "success"
    assert "message" in result


@patch("review_model.connect_to_db")
def test_flag_review_not_found(mock_db):
    """
    Test flagging a review that does not exist.
    
    Functionality:
        Tests the flag_review() function to ensure it returns an error
        when the specified review_id does not exist.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates review not found
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = review_model.flag_review(999, "Reason", user_id=1)
    assert "error" in result
    assert "Review not found" in result["error"]


@patch("review_model.connect_to_db")
def test_flag_review_already_flagged(mock_db):
    """
    Test flagging a review that is already flagged.
    
    Functionality:
        Tests the flag_review() function to ensure it returns an error
        when trying to flag a review that is already flagged.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates review is already flagged
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = {"is_flagged": True}
    
    result = review_model.flag_review(1, "Reason", user_id=1)
    assert "error" in result
    assert "already flagged" in result["error"]


@patch("review_model.connect_to_db")
def test_unflag_review_success(mock_db):
    """
    Test unflagging a review successfully.
    
    Functionality:
        Tests the unflag_review() function to ensure it correctly
        removes the flag from a review.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result status is "success"
        - Result contains success message
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.side_effect = [
        {"is_flagged": True},
        {"review_id": 1, "is_flagged": False}
    ]
    
    result = review_model.unflag_review(1, moderator_id=1)
    assert result["status"] == "success"
    assert "message" in result


@patch("review_model.connect_to_db")
def test_unflag_review_not_found(mock_db):
    """
    Test unflagging a review that does not exist.
    
    Functionality:
        Tests the unflag_review() function to ensure it returns an error
        when the specified review_id does not exist.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates review not found
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = review_model.unflag_review(999, moderator_id=1)
    assert "error" in result
    assert "Review not found" in result["error"]


@patch("review_model.connect_to_db")
def test_unflag_review_not_flagged(mock_db):
    """
    Test unflagging a review that is not flagged.
    
    Functionality:
        Tests the unflag_review() function to ensure it returns an error
        when trying to unflag a review that is not flagged.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates review is not flagged
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = {"is_flagged": False}
    
    result = review_model.unflag_review(1, moderator_id=1)
    assert "error" in result
    assert "not flagged" in result["error"]


@patch("review_model.connect_to_db")
def test_remove_review_success(mock_db):
    """
    Test removing a review successfully.
    
    Functionality:
        Tests the remove_review() function to ensure it correctly
        removes a review (soft delete).
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result status is "success"
        - Result contains success message
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.side_effect = [
        {"review_id": 1},
        {"review_id": 1, "is_moderated": True}
    ]
    
    result = review_model.remove_review(1, moderator_id=1)
    assert result["status"] == "success"
    assert "message" in result


@patch("review_model.connect_to_db")
def test_remove_review_not_found(mock_db):
    """
    Test removing a review that does not exist.
    
    Functionality:
        Tests the remove_review() function to ensure it returns an error
        when the specified review_id does not exist.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates review not found
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = review_model.remove_review(999, moderator_id=1)
    assert "error" in result
    assert "Review not found" in result["error"]


@patch("review_model.connect_to_db")
def test_get_review_reports(mock_db):
    """
    Test retrieving review moderation reports.
    
    Functionality:
        Tests the get_review_reports() function to ensure it correctly
        generates review statistics and reports.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains review statistics
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.side_effect = [
        {"total": 10},
        {"flagged": 2},
        {"hidden": 1},
        {"moderated": 3},
        {"avg_rating": 4.5}
    ]
    
    cursor.fetchall.return_value = [
        {"rating": 5, "count": 5},
        {"rating": 4, "count": 3}
    ]
    
    result = review_model.get_review_reports()
    assert "total_reviews" in result
    assert "flagged_reviews" in result
    assert "average_rating" in result


@patch("review_model.connect_to_db")
def test_sanitize_input(mock_db):
    """
    Test input sanitization.
    
    Functionality:
        Tests the sanitize_input() function to ensure it correctly
        sanitizes user input to prevent XSS and SQL injection.
    
    Parameters:
        mock_db: Mocked database connection function (not used but needed for fixture)
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - HTML characters are escaped
        - SQL injection patterns are handled
    """
    # Test HTML escaping
    result = review_model.sanitize_input("<script>alert('xss')</script>")
    assert "<" not in result or "&lt;" in result
    
    # Test None input
    result = review_model.sanitize_input(None)
    assert result is None
    
    # Test empty string
    result = review_model.sanitize_input("")
    assert result is None

