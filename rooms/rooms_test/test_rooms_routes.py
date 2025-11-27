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


@patch("rooms_routes.jwt.decode")
@patch("rooms_routes.insert_room", return_value={"room_name": "NewRoom"})
def test_add_room(mock_insert, mock_jwt_decode, client):
    mock_jwt_decode.return_value = {"username": "admin", "role": "Admin"}
    payload = {"room_name": "NewRoom", "Capacity": 10}
    res = client.post("/rooms/add", json=payload, headers={"Authorization": "Bearer fake_token"})
    assert res.status_code == 201
    assert res.json["room_name"] == "NewRoom"


@patch("rooms_routes.jwt.decode")
def test_add_room_unauthorized(mock_jwt_decode, client):
    mock_jwt_decode.return_value = {"username": "user", "role": "regular user"}
    res = client.post("/rooms/add", json={}, headers={"Authorization": "Bearer fake_token"})
    assert res.status_code == 403


@patch("rooms_routes.jwt.decode")
@patch("rooms_routes.update_room", return_value={"room_name": "UpdatedRoom"})
def test_update_room(mock_update, mock_jwt_decode, client):
    mock_jwt_decode.return_value = {"username": "admin", "role": "Admin"}
    payload = {"room_name": "UpdatedRoom", "Capacity": 10, "room_location": "F1", "room_status": "Available"}
    res = client.put("/api/rooms/update", json=payload, headers={"Authorization": "Bearer fake_token"})
    assert res.status_code == 200


@patch("rooms_routes.jwt.decode")
def test_update_room_unauthorized(mock_jwt_decode, client):
    mock_jwt_decode.return_value = {"username": "user", "role": "regular user"}
    res = client.put("/api/rooms/update", json={}, headers={"Authorization": "Bearer fake_token"})
    assert res.status_code == 403


@patch("rooms_routes.jwt.decode")
@patch("rooms_routes.delete_room", return_value={"message": "Room deleted"})
def test_delete_room(mock_delete, mock_jwt_decode, client):
    mock_jwt_decode.return_value = {"username": "admin", "role": "Admin"}
    res = client.delete("/api/rooms/delete/RX", headers={"Authorization": "Bearer fake_token"})
    assert res.status_code == 200


@patch("rooms_routes.jwt.decode")
@patch("rooms_routes.delete_room", return_value=None)
def test_delete_room_not_found(mock_delete, mock_jwt_decode, client):
    mock_jwt_decode.return_value = {"username": "admin", "role": "Admin"}
    res = client.delete("/api/rooms/delete/Unknown", headers={"Authorization": "Bearer fake_token"})
    assert res.status_code == 404


@patch("rooms_routes.jwt.decode")
@patch("rooms_routes.update_room", return_value={"room_name": "RT", "room_status": "Booked"})
@patch("rooms_routes.get_room_by_name", return_value={"room_name": "RT", "room_status": "Available", "Capacity": 10, "room_location": "L1"})
def test_toggle_status(mock_get, mock_update, mock_jwt_decode, client):
    mock_jwt_decode.return_value = {"username": "admin", "role": "Admin"}
    res = client.put("/api/rooms/toggle_status/RT", json={}, headers={"Authorization": "Bearer fake_token"})
    assert res.status_code == 200


@patch("rooms_routes.jwt.decode")
@patch("rooms_routes.update_room", return_value={"room_name": "R5", "room_status": "Out-of-Service"})
@patch("rooms_routes.get_room_by_name", return_value={"room_name": "R5", "Capacity": 10, "room_location": "L1"})
def test_mark_out_of_service(mock_get, mock_update, mock_jwt_decode, client):
    mock_jwt_decode.return_value = {"username": "manager", "role": "Facility Manager"}
    res = client.put("/facility_manager/rooms/out_of_service/R5", headers={"Authorization": "Bearer fake_token"})
    assert res.status_code == 200


@patch("rooms_routes.jwt.decode")
@patch("rooms_routes.get_rooms", return_value=[{"room_name": "Aud1"}])
def test_auditor_get_rooms(mock_get, mock_jwt_decode, client):
    mock_jwt_decode.return_value = {"username": "auditor", "role": "Auditor"}
    res = client.get("/auditor/rooms", headers={"Authorization": "Bearer fake_token"})
    assert res.status_code == 200


@patch("rooms_routes.jwt.decode")
def test_auditor_get_rooms_unauthorized(mock_jwt_decode, client):
    mock_jwt_decode.return_value = {"username": "user", "role": "regular user"}
    res = client.get("/auditor/rooms", headers={"Authorization": "Bearer fake_token"})
    assert res.status_code == 403


@patch("rooms_routes.jwt.decode")
@patch("rooms_routes.get_room_by_name", return_value={"room_name": "AudR"})
def test_auditor_get_room(mock_get, mock_jwt_decode, client):
    mock_jwt_decode.return_value = {"username": "auditor", "role": "Auditor"}
    res = client.get("/auditor/rooms/AudR", headers={"Authorization": "Bearer fake_token"})
    assert res.status_code == 200


@patch("rooms_routes.jwt.decode")
@patch("rooms_routes.get_room_by_name", return_value=None)
def test_auditor_get_room_not_found(mock_get, mock_jwt_decode, client):
    mock_jwt_decode.return_value = {"username": "auditor", "role": "Auditor"}
    res = client.get("/auditor/rooms/Unknown", headers={"Authorization": "Bearer fake_token"})
    assert res.status_code == 404
