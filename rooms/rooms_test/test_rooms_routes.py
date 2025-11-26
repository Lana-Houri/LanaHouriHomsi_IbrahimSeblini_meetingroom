import os
import sys

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask

SYS_PATH_ROOT = os.path.dirname(os.path.dirname(__file__))
if SYS_PATH_ROOT not in sys.path:
    sys.path.insert(0, SYS_PATH_ROOT)

from rooms_routes import room_bp


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(room_bp)
    return app.test_client()

@patch("rooms_routes.get_rooms", return_value=[{"room_name": "R1"}])
def test_get_rooms(mock_func, client):
    res = client.get("/api/rooms")
    assert res.status_code == 200
    assert res.json[0]["room_name"] == "R1"


@patch("rooms_routes.get_room_by_name", return_value={"room_name": "R2"})
def test_get_room(mock_func, client):
    res = client.get("/api/rooms/R2")
    assert res.status_code == 200
    assert res.json["room_name"] == "R2"


@patch("rooms_routes.get_room_by_name", return_value=None)
def test_get_room_not_found(mock_func, client):
    res = client.get("/api/rooms/Unknown")
    assert res.status_code == 404


@patch("rooms_routes.search_rooms", return_value=[{"room_name": "S1"}])
def test_search_rooms(mock_func, client):
    res = client.get("/api/rooms/search?capacity=10")
    assert res.status_code == 200
    assert res.json[0]["room_name"] == "S1"


@patch("rooms_routes.get_rooms", return_value=[
    {"room_name": "A1", "room_status": "Available"},
    {"room_name": "A2", "room_status": "Booked"},
])
def test_available_rooms(mock_func, client):
    res = client.get("/api/rooms/available")
    assert res.status_code == 200
    assert len(res.json) == 1


@patch("rooms_routes.insert_room", return_value={"room_name": "NewRoom"})
@patch("rooms_routes.get_user_role", return_value="Admin")
def test_add_room(mock_role, mock_insert, client):
    payload = {"room_name": "NewRoom", "Capacity": 10}
    res = client.post("/rooms/add", json=payload)
    assert res.status_code == 201
    assert res.json["room_name"] == "NewRoom"


@patch("rooms_routes.get_user_role", return_value="regular user")
def test_add_room_unauthorized(mock_role, client):
    res = client.post("/rooms/add", json={})
    assert res.status_code == 403


@patch("rooms_routes.update_room", return_value={"room_name": "UpdatedRoom"})
@patch("rooms_routes.get_user_role", return_value="Admin")
def test_update_room(mock_role, mock_update, client):
    payload = {"room_name": "UpdatedRoom", "Capacity": 10, "room_location": "F1", "room_status": "Available"}
    res = client.put("/api/rooms/update", json=payload)
    assert res.status_code == 200


@patch("rooms_routes.get_user_role", return_value="regular user")
def test_update_room_unauthorized(mock_role, client):
    res = client.put("/api/rooms/update", json={})
    assert res.status_code == 403


@patch("rooms_routes.delete_room", return_value={"message": "Room deleted"})
@patch("rooms_routes.get_user_role", return_value="Admin")
def test_delete_room(mock_role, mock_delete, client):
    res = client.delete("/api/rooms/delete/RX")
    assert res.status_code == 200


@patch("rooms_routes.delete_room", return_value=None)
@patch("rooms_routes.get_user_role", return_value="Admin")
def test_delete_room_not_found(mock_role, mock_delete, client):
    res = client.delete("/api/rooms/delete/Unknown")
    assert res.status_code == 404


@patch("rooms_routes.update_room", return_value={"room_name": "RT", "room_status": "Booked"})
@patch("rooms_routes.get_room_by_name", return_value={"room_name": "RT", "room_status": "Available", "Capacity": 10, "room_location": "L1"})
@patch("rooms_routes.get_user_role", return_value="Admin")
def test_toggle_status(mock_role, mock_get, mock_update, client):
    res = client.put("/api/rooms/toggle_status/RT", json={})
    assert res.status_code == 200


@patch("rooms_routes.update_room", return_value={"room_name": "R5", "room_status": "Out-of-Service"})
@patch("rooms_routes.get_room_by_name", return_value={"room_name": "R5", "Capacity": 10, "room_location": "L1"})
@patch("rooms_routes.get_user_role", return_value="Facility Manager")
def test_mark_out_of_service(mock_role, mock_get, mock_update, client):
    res = client.put("/facility_manager/rooms/out_of_service/R5")
    assert res.status_code == 200


@patch("rooms_routes.get_rooms", return_value=[{"room_name": "Aud1"}])
@patch("rooms_routes.get_user_role", return_value="Auditor")
def test_auditor_get_rooms(mock_role, mock_get, client):
    res = client.get("/auditor/rooms")
    assert res.status_code == 200


@patch("rooms_routes.get_user_role", return_value="regular user")
def test_auditor_get_rooms_unauthorized(mock_role, client):
    res = client.get("/auditor/rooms")
    assert res.status_code == 403


@patch("rooms_routes.get_room_by_name", return_value={"room_name": "AudR"})
@patch("rooms_routes.get_user_role", return_value="Auditor")
def test_auditor_get_room(mock_role, mock_get, client):
    res = client.get("/auditor/rooms/AudR")
    assert res.status_code == 200


@patch("rooms_routes.get_room_by_name", return_value=None)
@patch("rooms_routes.get_user_role", return_value="Auditor")
def test_auditor_get_room_not_found(mock_role, mock_get, client):
    res = client.get("/auditor/rooms/Unknown")
    assert res.status_code == 404
