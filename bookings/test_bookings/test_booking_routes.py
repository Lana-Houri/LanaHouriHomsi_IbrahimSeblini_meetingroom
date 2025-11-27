import os
import sys

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask

SYS_PATH_ROOT = os.path.dirname(os.path.dirname(__file__))
if SYS_PATH_ROOT not in sys.path:
    sys.path.insert(0, SYS_PATH_ROOT)

from booking_routes import booking_bp


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(booking_bp)
    return app.test_client()


@pytest.fixture(autouse=True)
def mock_auth_jwt_decode(monkeypatch):
    """Mock jwt.decode to return user info based on token."""
    def mock_decode(token, key, algorithms):
        # Default mock user for admin routes
        if "admin_token" in token:
            return {"username": "admin", "role": "Admin"}
        # Default mock user for facility manager routes
        if "facility_manager_token" in token:
            return {"username": "facility_manager", "role": "Facility Manager"}
        # Default mock user for auditor routes
        if "auditor_token" in token:
            return {"username": "auditor", "role": "Auditor"}
        # Default mock user for regular user routes
        if "regular_user_token" in token:
            return {"username": "regular_user", "role": "regular user"}
        # Default mock user for user_id=1
        if "user1_token" in token:
            return {"username": "user1", "role": "regular user"}
        # Default mock user for user_id=2
        if "user2_token" in token:
            return {"username": "user2", "role": "regular user"}
        # Fallback
        return {"username": "test_user", "role": "regular user"}
    monkeypatch.setattr("booking_routes.jwt.decode", mock_decode)


@pytest.fixture(autouse=True)
def mock_get_user_id_from_token(monkeypatch):
    """Mock get_user_id_from_token to return user_id based on username."""
    def mock_get_user_id():
        from flask import request
        if not hasattr(request, 'user') or 'username' not in request.user:
            return None
        username = request.user["username"]
        # Map usernames to user_ids
        user_id_map = {
            "admin": 1,
            "facility_manager": 1,
            "auditor": 1,
            "regular_user": 1,
            "user1": 1,
            "user2": 2,
            "test_user": 1
        }
        return user_id_map.get(username, 1)
    monkeypatch.setattr("booking_routes.get_user_id_from_token", mock_get_user_id)


@patch("booking_routes.get_all_bookings", return_value=[{"booking_id": 1, "user_id": 1}])
def test_get_all_bookings_admin(mock_func, client):
    res = client.get("/api/bookings", headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200
    assert "bookings" in res.json
    assert res.json["count"] == 1


@patch("booking_routes.get_all_bookings", return_value=[{"booking_id": 1}])
def test_get_all_bookings_facility_manager(mock_func, client):
    res = client.get("/api/bookings", headers={"Authorization": "Bearer facility_manager_token"})
    assert res.status_code == 200
    assert "bookings" in res.json


@patch("booking_routes.get_all_bookings", return_value=[{"booking_id": 1}])
def test_get_all_bookings_auditor(mock_func, client):
    res = client.get("/api/bookings", headers={"Authorization": "Bearer auditor_token"})
    assert res.status_code == 200
    assert "bookings" in res.json


def test_get_all_bookings_unauthorized(client):
    res = client.get("/api/bookings", headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 403
    assert "error" in res.json


def test_get_all_bookings_no_token(client):
    res = client.get("/api/bookings")
    assert res.status_code == 401
    assert "error" in res.json


@patch("booking_routes.get_booking_by_id", return_value={"booking_id": 1, "user_id": 1})
def test_get_booking_own_booking(mock_func, client):
    res = client.get("/api/bookings/1", headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 200
    assert res.json["booking_id"] == 1


@patch("booking_routes.get_booking_by_id", return_value={"booking_id": 1, "user_id": 2})
def test_get_booking_other_user_booking_unauthorized(mock_func, client):
    res = client.get("/api/bookings/1", headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 403
    assert "error" in res.json


@patch("booking_routes.get_booking_by_id", return_value={"booking_id": 1, "user_id": 2})
def test_get_booking_admin_can_view_any(mock_func, client):
    res = client.get("/api/bookings/1", headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200
    assert res.json["booking_id"] == 1


@patch("booking_routes.get_booking_by_id", return_value={})
def test_get_booking_not_found(mock_func, client):
    res = client.get("/api/bookings/999", headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 404
    assert "error" in res.json


@patch("booking_routes.get_user_bookings", return_value=[{"booking_id": 1, "user_id": 1}])
def test_get_user_bookings_own_history(mock_func, client):
    res = client.get("/api/bookings/user/1", headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 200
    assert "bookings" in res.json
    assert res.json["user_id"] == 1


@patch("booking_routes.get_user_bookings", return_value=[{"booking_id": 1}])
def test_get_user_bookings_admin_can_view_any(mock_func, client):
    res = client.get("/api/bookings/user/2", headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200
    assert res.json["user_id"] == 2


def test_get_user_bookings_unauthorized(client):
    res = client.get("/api/bookings/user/2", headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 403
    assert "error" in res.json


@patch("booking_routes.get_room_bookings", return_value=[{"booking_id": 1, "room_id": 1}])
def test_get_room_bookings(mock_func, client):
    res = client.get("/api/bookings/room/1")
    assert res.status_code == 200
    assert "bookings" in res.json
    assert res.json["room_id"] == 1


@patch("booking_routes.get_room_bookings", return_value=[{"booking_id": 1}])
def test_get_room_bookings_with_date(mock_func, client):
    res = client.get("/api/bookings/room/1?date=2024-01-01")
    assert res.status_code == 200
    assert res.json["date"] == "2024-01-01"


@patch("booking_routes.check_room_availability", return_value=True)
def test_check_availability_available(mock_func, client):
    res = client.get("/api/bookings/availability?room_id=1&date=2024-01-01&start_time=10:00:00&end_time=11:00:00")
    assert res.status_code == 200
    assert res.json["available"] is True


@patch("booking_routes.check_room_availability", return_value=False)
def test_check_availability_not_available(mock_func, client):
    res = client.get("/api/bookings/availability?room_id=1&date=2024-01-01&start_time=10:00:00&end_time=11:00:00")
    assert res.status_code == 200
    assert res.json["available"] is False


def test_check_availability_missing_params(client):
    res = client.get("/api/bookings/availability?room_id=1")
    assert res.status_code == 400
    assert "error" in res.json


@patch("booking_routes.create_booking", return_value={"booking_id": 1, "user_id": 1, "room_id": 1, "status": "Confirmed"})
def test_create_booking_success(mock_func, client):
    payload = {
        "user_id": 1,
        "room_id": 1,
        "booking_date": "2024-01-01",
        "start_time": "10:00:00",
        "end_time": "11:00:00"
    }
    res = client.post("/api/bookings", json=payload, headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 201
    assert res.json["booking_id"] == 1


@patch("booking_routes.create_booking", return_value={"error": "Room is not available", "status": "error"})
def test_create_booking_not_available(mock_func, client):
    payload = {
        "user_id": 1,
        "room_id": 1,
        "booking_date": "2024-01-01",
        "start_time": "10:00:00",
        "end_time": "11:00:00"
    }
    res = client.post("/api/bookings", json=payload, headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 400
    assert "error" in res.json


def test_create_booking_missing_data(client):
    res = client.post("/api/bookings", json={}, headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 400
    assert "error" in res.json


def test_create_booking_unauthorized_other_user(client):
    payload = {
        "user_id": 2,
        "room_id": 1,
        "booking_date": "2024-01-01",
        "start_time": "10:00:00",
        "end_time": "11:00:00"
    }
    res = client.post("/api/bookings", json=payload, headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 403
    assert "error" in res.json


@patch("booking_routes.create_booking", return_value={"booking_id": 1})
def test_create_booking_admin_can_create_for_anyone(mock_func, client):
    payload = {
        "user_id": 2,
        "room_id": 1,
        "booking_date": "2024-01-01",
        "start_time": "10:00:00",
        "end_time": "11:00:00"
    }
    res = client.post("/api/bookings", json=payload, headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 201


@patch("booking_routes.update_booking", return_value={"booking_id": 1, "status": "Confirmed"})
def test_update_booking_success(mock_func, client):
    payload = {
        "start_time": "11:00:00",
        "end_time": "12:00:00"
    }
    res = client.put("/api/bookings/1", json=payload, headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 200
    assert res.json["booking_id"] == 1


@patch("booking_routes.update_booking", return_value={"error": "Unauthorized", "status": "error"})
def test_update_booking_unauthorized(mock_func, client):
    payload = {"start_time": "11:00:00"}
    res = client.put("/api/bookings/1", json=payload, headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 403


def test_update_booking_missing_data(client):
    res = client.put("/api/bookings/1", json={}, headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 400
    assert "error" in res.json


@patch("booking_routes.cancel_booking", return_value={"message": "Booking cancelled successfully", "status": "success"})
def test_cancel_booking_success(mock_func, client):
    res = client.put("/api/bookings/1/cancel", headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 200
    assert "message" in res.json


@patch("booking_routes.cancel_booking", return_value={"error": "Unauthorized", "status": "error"})
def test_cancel_booking_unauthorized(mock_func, client):
    res = client.put("/api/bookings/1/cancel", headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 403


@patch("booking_routes.cancel_booking", return_value={"message": "Booking cancelled successfully", "status": "success"})
def test_force_cancel_booking_admin(mock_func, client):
    res = client.put("/api/admin/bookings/1/force-cancel", headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200
    assert "message" in res.json


def test_force_cancel_booking_unauthorized(client):
    res = client.put("/api/admin/bookings/1/force-cancel", headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 403
    assert "error" in res.json


@patch("booking_routes.update_booking", return_value={"booking_id": 1, "status": "Confirmed"})
def test_admin_update_booking(mock_func, client):
    payload = {"start_time": "11:00:00", "end_time": "12:00:00"}
    res = client.put("/api/admin/bookings/1", json=payload, headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200
    assert res.json["booking_id"] == 1


def test_admin_update_booking_unauthorized(client):
    res = client.put("/api/admin/bookings/1", json={}, headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 403
    assert "error" in res.json


@patch("booking_routes.get_conflicting_bookings", return_value=[{"booking_id": 1}])
def test_get_conflicts_admin(mock_func, client):
    res = client.get("/api/admin/bookings/conflicts?room_id=1&date=2024-01-01&start_time=10:00:00&end_time=11:00:00", 
                     headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200
    assert "conflicts" in res.json


def test_get_conflicts_unauthorized(client):
    res = client.get("/api/admin/bookings/conflicts?room_id=1&date=2024-01-01&start_time=10:00:00&end_time=11:00:00",
                     headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 403


def test_get_conflicts_missing_params(client):
    res = client.get("/api/admin/bookings/conflicts?room_id=1",
                     headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 400
    assert "error" in res.json


@patch("booking_routes.resolve_booking_conflict", return_value={"message": "Booking cancelled to resolve conflict", "status": "success"})
def test_resolve_conflict_admin(mock_func, client):
    payload = {"action": "cancel"}
    res = client.put("/api/admin/bookings/1/resolve", json=payload, headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200
    assert "message" in res.json


def test_resolve_conflict_unauthorized(client):
    res = client.put("/api/admin/bookings/1/resolve", json={"action": "cancel"},
                     headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 403


def test_resolve_conflict_missing_data(client):
    res = client.put("/api/admin/bookings/1/resolve", json={},
                     headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 400
    assert "error" in res.json


@patch("booking_routes.get_stuck_bookings", return_value=[{"booking_id": 1, "status": "Confirmed"}])
def test_get_stuck_bookings_admin(mock_func, client):
    res = client.get("/api/admin/bookings/stuck", headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200
    assert "stuck_bookings" in res.json


def test_get_stuck_bookings_unauthorized(client):
    res = client.get("/api/admin/bookings/stuck", headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 403
    assert "error" in res.json


@patch("booking_routes.unblock_stuck_booking", return_value={"message": "Booking marked as completed", "status": "success"})
def test_unblock_booking_admin(mock_func, client):
    payload = {"action": "complete"}
    res = client.put("/api/admin/bookings/1/unblock", json=payload, headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200
    assert "message" in res.json


def test_unblock_booking_unauthorized(client):
    res = client.put("/api/admin/bookings/1/unblock", json={"action": "complete"},
                     headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 403
    assert "error" in res.json

