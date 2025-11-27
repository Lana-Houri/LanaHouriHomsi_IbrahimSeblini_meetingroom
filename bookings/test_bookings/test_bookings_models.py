"""
Test suite for booking_model.py

This module contains unit tests for all booking model functions,
testing database operations, validation logic, and error handling.
"""
import os
import sys

import pytest
from unittest.mock import patch, MagicMock

SYS_PATH_ROOT = os.path.dirname(os.path.dirname(__file__))
if SYS_PATH_ROOT not in sys.path:
    sys.path.insert(0, SYS_PATH_ROOT)

import booking_model

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


@patch("booking_model.connect_to_db")
def test_get_all_bookings(mock_db):
    """
    Test retrieving all bookings from the database.
    
    Functionality:
        Tests the get_all_bookings() function to ensure it correctly
        retrieves all bookings with user and room details.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is a list with at least one booking
        - Booking contains expected booking_id
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchall.return_value = [
        {"booking_id": 1, "user_id": 1, "room_id": 1, "booking_date": "2024-01-01", "start_time": "10:00:00", "end_time": "11:00:00", "status": "Confirmed", "username": "user1", "room_name": "Room1"}
    ]
    
    result = booking_model.get_all_bookings()
    assert len(result) == 1
    assert result[0]["booking_id"] == 1


@patch("booking_model.connect_to_db")
def test_get_booking_by_id(mock_db):
    """
    Test retrieving a booking by its ID when booking exists.
    
    Functionality:
        Tests the get_booking_by_id() function to ensure it correctly
        retrieves a booking when a valid booking_id is provided.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains the expected booking_id
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = {"booking_id": 1, "user_id": 1, "room_id": 1}
    
    result = booking_model.get_booking_by_id(1)
    assert result["booking_id"] == 1


@patch("booking_model.connect_to_db")
def test_get_booking_by_id_not_found(mock_db):
    """
    Test retrieving a booking by ID when booking does not exist.
    
    Functionality:
        Tests the get_booking_by_id() function to ensure it returns
        an empty dictionary when booking_id is not found.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is an empty dictionary when booking not found
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = booking_model.get_booking_by_id(999)
    assert result == {}


@patch("booking_model.connect_to_db")
def test_get_user_bookings(mock_db):
    """
    Test retrieving all bookings for a specific user.
    
    Functionality:
        Tests the get_user_bookings() function to ensure it correctly
        retrieves all bookings associated with a given user_id.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is a list with at least one booking
        - Booking belongs to the specified user_id
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchall.return_value = [
        {"booking_id": 1, "user_id": 1, "room_id": 1}
    ]
    
    result = booking_model.get_user_bookings(1)
    assert len(result) == 1
    assert result[0]["user_id"] == 1


@patch("booking_model.connect_to_db")
def test_get_room_bookings(mock_db):
    """
    Test retrieving all bookings for a specific room without date filter.
    
    Functionality:
        Tests the get_room_bookings() function to ensure it correctly
        retrieves all bookings for a given room_id when no date is specified.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is a list with at least one booking
        - Booking belongs to the specified room_id
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchall.return_value = [
        {"booking_id": 1, "room_id": 1, "booking_date": "2024-01-01"}
    ]
    
    result = booking_model.get_room_bookings(1)
    assert len(result) == 1
    assert result[0]["room_id"] == 1


@patch("booking_model.connect_to_db")
def test_get_room_bookings_with_date(mock_db):
    """
    Test retrieving bookings for a room filtered by date.
    
    Functionality:
        Tests the get_room_bookings() function to ensure it correctly
        filters bookings by date when a date parameter is provided.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is a list with bookings matching the date filter
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchall.return_value = [
        {"booking_id": 1, "room_id": 1, "booking_date": "2024-01-01"}
    ]
    
    result = booking_model.get_room_bookings(1, "2024-01-01")
    assert len(result) == 1


@patch("booking_model.connect_to_db")
def test_check_room_availability_available(mock_db):
    """
    Test checking room availability when room is available.
    
    Functionality:
        Tests the check_room_availability() function to ensure it correctly
        returns True when no conflicting bookings exist for the time slot.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is True when room is available
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = [0]
    
    result = booking_model.check_room_availability(1, "2024-01-01", "10:00:00", "11:00:00")
    assert result is True


@patch("booking_model.connect_to_db")
def test_check_room_availability_not_available(mock_db):
    """
    Test checking room availability when room is not available.
    
    Functionality:
        Tests the check_room_availability() function to ensure it correctly
        returns False when conflicting bookings exist for the time slot.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is False when room is not available
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = [1]
    
    result = booking_model.check_room_availability(1, "2024-01-01", "10:00:00", "11:00:00")
    assert result is False


@patch("booking_model.connect_to_db")
def test_check_room_availability_with_exclude(mock_db):
    """
    Test checking room availability with excluded booking ID.
    
    Functionality:
        Tests the check_room_availability() function with exclude_booking_id
        parameter, used when updating an existing booking to exclude it from
        conflict checks.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is True when room is available after excluding specified booking
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = [0]
    
    result = booking_model.check_room_availability(1, "2024-01-01", "10:00:00", "11:00:00", exclude_booking_id=5)
    assert result is True


@patch("booking_model.check_user_exists", return_value=True)
@patch("booking_model.check_room_exists", return_value=True)
@patch("booking_model.check_room_availability", return_value=True)
@patch("booking_model.connect_to_db")
def test_create_booking_success(mock_db, mock_avail, mock_room, mock_user):
    """
    Test creating a booking successfully.
    
    Functionality:
        Tests the create_booking() function to ensure it correctly creates
        a new booking when all validations pass (user exists, room exists,
        room is available, all required fields provided).
    
    Parameters:
        mock_db: Mocked database connection function
        mock_avail: Mocked check_room_availability function
        mock_room: Mocked check_room_exists function
        mock_user: Mocked check_user_exists function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains booking_id
        - Result does not contain error
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.side_effect = [
        {"booking_id": 1, "user_id": 1, "room_id": 1, "booking_date": "2024-01-01", "start_time": "10:00:00", "end_time": "11:00:00", "status": "Confirmed"},
        {"booking_id": 1, "user_id": 1, "room_id": 1, "username": "user1", "room_name": "Room1"}
    ]
    
    booking_data = {
        "user_id": 1,
        "room_id": 1,
        "booking_date": "2024-01-01",
        "start_time": "10:00:00",
        "end_time": "11:00:00"
    }
    
    result = booking_model.create_booking(booking_data)
    assert result["booking_id"] == 1
    assert "error" not in result


@patch("booking_model.check_user_exists", return_value=False)
def test_create_booking_user_not_exists(mock_user):
    """
    Test creating a booking when user does not exist.
    
    Functionality:
        Tests the create_booking() function to ensure it returns an error
        when the specified user_id does not exist in the database.
    
    Parameters:
        mock_user: Mocked check_user_exists function returning False
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates user does not exist
    """
    booking_data = {
        "user_id": 999,
        "room_id": 1,
        "booking_date": "2024-01-01",
        "start_time": "10:00:00",
        "end_time": "11:00:00"
    }
    
    result = booking_model.create_booking(booking_data)
    assert "error" in result
    assert "User does not exist" in result["error"]


@patch("booking_model.check_user_exists", return_value=True)
@patch("booking_model.check_room_exists", return_value=False)
def test_create_booking_room_not_exists(mock_room, mock_user):
    """
    Test creating a booking when room does not exist.
    
    Functionality:
        Tests the create_booking() function to ensure it returns an error
        when the specified room_id does not exist or is not available.
    
    Parameters:
        mock_room: Mocked check_room_exists function returning False
        mock_user: Mocked check_user_exists function returning True
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates room does not exist
    """
    booking_data = {
        "user_id": 1,
        "room_id": 999,
        "booking_date": "2024-01-01",
        "start_time": "10:00:00",
        "end_time": "11:00:00"
    }
    
    result = booking_model.create_booking(booking_data)
    assert "error" in result
    assert "Room does not exist" in result["error"]


@patch("booking_model.check_user_exists", return_value=True)
@patch("booking_model.check_room_exists", return_value=True)
@patch("booking_model.check_room_availability", return_value=False)
def test_create_booking_not_available(mock_avail, mock_room, mock_user):
    """
    Test creating a booking when room is not available.
    
    Functionality:
        Tests the create_booking() function to ensure it returns an error
        when the room is already booked for the requested time slot.
    
    Parameters:
        mock_avail: Mocked check_room_availability function returning False
        mock_room: Mocked check_room_exists function returning True
        mock_user: Mocked check_user_exists function returning True
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates room is not available
    """
    booking_data = {
        "user_id": 1,
        "room_id": 1,
        "booking_date": "2024-01-01",
        "start_time": "10:00:00",
        "end_time": "11:00:00"
    }
    
    result = booking_model.create_booking(booking_data)
    assert "error" in result
    assert "not available" in result["error"]


def test_create_booking_missing_fields():
    """
    Test creating a booking with missing required fields.
    
    Functionality:
        Tests the create_booking() function to ensure it returns an error
        when required fields (user_id, room_id, booking_date, start_time, end_time)
        are missing from the booking data.
    
    Parameters:
        None
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates missing required fields
    """
    booking_data = {
        "user_id": 1,
        "room_id": 1
    }
    
    result = booking_model.create_booking(booking_data)
    assert "error" in result
    assert "Missing required fields" in result["error"]


@patch("booking_model.check_room_exists", return_value=True)
@patch("booking_model.check_room_availability", return_value=True)
@patch("booking_model.connect_to_db")
def test_update_booking_success(mock_db, mock_avail, mock_room):
    """
    Test updating a booking successfully.
    
    Functionality:
        Tests the update_booking() function to ensure it correctly updates
        a booking when user has permission and validations pass.
    
    Parameters:
        mock_db: Mocked database connection function
        mock_avail: Mocked check_room_availability function
        mock_room: Mocked check_room_exists function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains booking_id
        - Result does not contain error
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.side_effect = [
        {"user_id": 1, "room_id": 1, "booking_date": "2024-01-01", "start_time": "10:00:00", "end_time": "11:00:00", "status": "Confirmed"},
        {"booking_id": 1, "user_id": 1, "room_id": 1, "booking_date": "2024-01-01", "start_time": "10:00:00", "end_time": "11:00:00", "status": "Confirmed"},
        {"booking_id": 1, "user_id": 1, "room_id": 1, "username": "user1", "room_name": "Room1"}
    ]
    
    booking_data = {
        "room_id": 1,
        "booking_date": "2024-01-01",
        "start_time": "10:00:00",
        "end_time": "12:00:00"
    }
    
    result = booking_model.update_booking(1, booking_data, user_id=1, is_admin=False)
    assert result["booking_id"] == 1
    assert "error" not in result


@patch("booking_model.connect_to_db")
def test_update_booking_not_found(mock_db):
    """
    Test updating a booking that does not exist.
    
    Functionality:
        Tests the update_booking() function to ensure it returns an error
        when the specified booking_id does not exist.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates booking not found
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = booking_model.update_booking(999, {}, user_id=1, is_admin=False)
    assert "error" in result
    assert "Booking not found" in result["error"]


@patch("booking_model.connect_to_db")
def test_update_booking_unauthorized(mock_db):
    """
    Test updating a booking without authorization.
    
    Functionality:
        Tests the update_booking() function to ensure it returns an error
        when a regular user tries to update another user's booking.
    
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
    
    cursor.fetchone.return_value = {"user_id": 2, "room_id": 1, "booking_date": "2024-01-01", "start_time": "10:00:00", "end_time": "11:00:00"}
    
    result = booking_model.update_booking(1, {}, user_id=1, is_admin=False)
    assert "error" in result
    assert "Unauthorized" in result["error"]


@patch("booking_model.connect_to_db")
def test_cancel_booking_success(mock_db):
    """
    Test cancelling a booking successfully.
    
    Functionality:
        Tests the cancel_booking() function to ensure it correctly cancels
        a booking when user has permission.
    
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
        {"user_id": 1, "status": "Confirmed"},
        {"booking_id": 1, "status": "Cancelled"}
    ]
    
    result = booking_model.cancel_booking(1, user_id=1, is_admin=False)
    assert result["status"] == "success"
    assert "message" in result


@patch("booking_model.connect_to_db")
def test_cancel_booking_not_found(mock_db):
    """
    Test cancelling a booking that does not exist.
    
    Functionality:
        Tests the cancel_booking() function to ensure it returns an error
        when the specified booking_id does not exist.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates booking not found
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = booking_model.cancel_booking(999, user_id=1, is_admin=False)
    assert "error" in result
    assert "Booking not found" in result["error"]


@patch("booking_model.connect_to_db")
def test_cancel_booking_unauthorized(mock_db):
    """
    Test cancelling a booking without authorization.
    
    Functionality:
        Tests the cancel_booking() function to ensure it returns an error
        when a regular user tries to cancel another user's booking.
    
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
    
    cursor.fetchone.return_value = {"user_id": 2, "status": "Confirmed"}
    
    result = booking_model.cancel_booking(1, user_id=1, is_admin=False)
    assert "error" in result
    assert "Unauthorized" in result["error"]


@patch("booking_model.connect_to_db")
def test_get_conflicting_bookings(mock_db):
    """
    Test retrieving conflicting bookings for a time slot.
    
    Functionality:
        Tests the get_conflicting_bookings() function to ensure it correctly
        retrieves all bookings that conflict with a given time slot.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is a list with conflicting bookings
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchall.return_value = [
        {"booking_id": 1, "room_id": 1, "start_time": "10:00:00", "end_time": "11:00:00"}
    ]
    
    result = booking_model.get_conflicting_bookings(1, "2024-01-01", "10:00:00", "11:00:00")
    assert len(result) == 1


@patch("booking_model.connect_to_db")
def test_resolve_booking_conflict_cancel(mock_db):
    """
    Test resolving a booking conflict by cancelling.
    
    Functionality:
        Tests the resolve_booking_conflict() function to ensure it correctly
        cancels a booking when "cancel" action is specified.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result status is "success"
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.side_effect = [
        {"booking_id": 1},
        {"booking_id": 1, "status": "Cancelled"}
    ]
    
    result = booking_model.resolve_booking_conflict(1, "cancel", admin_id=1)
    assert result["status"] == "success"


@patch("booking_model.connect_to_db")
def test_resolve_booking_conflict_not_found(mock_db):
    """
    Test resolving a booking conflict when booking does not exist.
    
    Functionality:
        Tests the resolve_booking_conflict() function to ensure it returns
        an error when the specified booking_id does not exist.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates booking not found
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = booking_model.resolve_booking_conflict(999, "cancel", admin_id=1)
    assert "error" in result
    assert "Booking not found" in result["error"]


@patch("booking_model.connect_to_db")
def test_get_stuck_bookings(mock_db):
    """
    Test retrieving stuck bookings.
    
    Functionality:
        Tests the get_stuck_bookings() function to ensure it correctly
        retrieves bookings that are in stuck states (e.g., confirmed bookings
        with past dates that haven't been completed or cancelled).
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result is a list with stuck bookings
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchall.return_value = [
        {"booking_id": 1, "status": "Confirmed", "booking_date": "2023-01-01"}
    ]
    
    result = booking_model.get_stuck_bookings()
    assert len(result) == 1


@patch("booking_model.connect_to_db")
def test_unblock_stuck_booking_complete(mock_db):
    """
    Test unblocking a stuck booking by marking as completed.
    
    Functionality:
        Tests the unblock_stuck_booking() function to ensure it correctly
        marks a stuck booking as completed when "complete" action is specified.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result status is "success"
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.side_effect = [
        {"status": "Confirmed"},
        {"booking_id": 1, "status": "Completed"}
    ]
    
    result = booking_model.unblock_stuck_booking(1, "complete")
    assert result["status"] == "success"


@patch("booking_model.connect_to_db")
def test_unblock_stuck_booking_cancel(mock_db):
    """
    Test unblocking a stuck booking by cancelling.
    
    Functionality:
        Tests the unblock_stuck_booking() function to ensure it correctly
        cancels a stuck booking when "cancel" action is specified.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result status is "success"
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.side_effect = [
        {"status": "Confirmed"},
        {"booking_id": 1, "status": "Cancelled"}
    ]
    
    result = booking_model.unblock_stuck_booking(1, "cancel")
    assert result["status"] == "success"


@patch("booking_model.connect_to_db")
def test_unblock_stuck_booking_not_found(mock_db):
    """
    Test unblocking a stuck booking that does not exist.
    
    Functionality:
        Tests the unblock_stuck_booking() function to ensure it returns
        an error when the specified booking_id does not exist.
    
    Parameters:
        mock_db: Mocked database connection function
    
    Returns:
        None (assertions verify the result)
    
    Asserts:
        - Result contains error
        - Error message indicates booking not found
    """
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = booking_model.unblock_stuck_booking(999, "complete")
    assert "error" in result
    assert "Booking not found" in result["error"]

