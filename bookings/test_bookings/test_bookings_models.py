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
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


@patch("booking_model.connect_to_db")
def test_get_all_bookings(mock_db):
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
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = {"booking_id": 1, "user_id": 1, "room_id": 1}
    
    result = booking_model.get_booking_by_id(1)
    assert result["booking_id"] == 1


@patch("booking_model.connect_to_db")
def test_get_booking_by_id_not_found(mock_db):
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = booking_model.get_booking_by_id(999)
    assert result == {}


@patch("booking_model.connect_to_db")
def test_get_user_bookings(mock_db):
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
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = [0]
    
    result = booking_model.check_room_availability(1, "2024-01-01", "10:00:00", "11:00:00")
    assert result is True


@patch("booking_model.connect_to_db")
def test_check_room_availability_not_available(mock_db):
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = [1]
    
    result = booking_model.check_room_availability(1, "2024-01-01", "10:00:00", "11:00:00")
    assert result is False


@patch("booking_model.connect_to_db")
def test_check_room_availability_with_exclude(mock_db):
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
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = booking_model.update_booking(999, {}, user_id=1, is_admin=False)
    assert "error" in result
    assert "Booking not found" in result["error"]


@patch("booking_model.connect_to_db")
def test_update_booking_unauthorized(mock_db):
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = {"user_id": 2, "room_id": 1, "booking_date": "2024-01-01", "start_time": "10:00:00", "end_time": "11:00:00"}
    
    result = booking_model.update_booking(1, {}, user_id=1, is_admin=False)
    assert "error" in result
    assert "Unauthorized" in result["error"]


@patch("booking_model.connect_to_db")
def test_cancel_booking_success(mock_db):
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
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = booking_model.cancel_booking(999, user_id=1, is_admin=False)
    assert "error" in result
    assert "Booking not found" in result["error"]


@patch("booking_model.connect_to_db")
def test_cancel_booking_unauthorized(mock_db):
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = {"user_id": 2, "status": "Confirmed"}
    
    result = booking_model.cancel_booking(1, user_id=1, is_admin=False)
    assert "error" in result
    assert "Unauthorized" in result["error"]


@patch("booking_model.connect_to_db")
def test_get_conflicting_bookings(mock_db):
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
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = booking_model.resolve_booking_conflict(999, "cancel", admin_id=1)
    assert "error" in result
    assert "Booking not found" in result["error"]


@patch("booking_model.connect_to_db")
def test_get_stuck_bookings(mock_db):
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
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor
    
    cursor.fetchone.return_value = None
    
    result = booking_model.unblock_stuck_booking(999, "complete")
    assert "error" in result
    assert "Booking not found" in result["error"]

