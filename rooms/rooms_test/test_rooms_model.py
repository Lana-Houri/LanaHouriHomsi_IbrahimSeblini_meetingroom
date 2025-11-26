import os
import sys

import pytest
from unittest.mock import patch, MagicMock

SYS_PATH_ROOT = os.path.dirname(os.path.dirname(__file__))
if SYS_PATH_ROOT not in sys.path:
    sys.path.insert(0, SYS_PATH_ROOT)

import rooms_model


@pytest.fixture
def mock_conn_cursor():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


@patch("rooms_model.connect_to_db")
def test_get_rooms(mock_db):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        {"room_name": "Room101", "Capacity": 10}
    ]

    result = rooms_model.get_rooms()
    assert len(result) == 1
    assert result[0]["room_name"] == "Room101"


@patch("rooms_model.connect_to_db")
def test_get_room_by_name(mock_db):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = {"room_name": "RoomA"}

    result = rooms_model.get_room_by_name("RoomA")
    assert result["room_name"] == "RoomA"


@patch("rooms_model.connect_to_db")
def test_insert_room(mock_db):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "room_name": "RoomX",
        "Capacity": 20,
        "room_status": "Available"
    }

    payload = {
        "room_name": "RoomX",
        "Capacity": 20,
        "room_location": "Floor 1",
        "equipment": "TV",
        "room_status": "Available"
    }

    result = rooms_model.insert_room(payload)
    assert result["room_name"] == "RoomX"


@patch("rooms_model.connect_to_db")
def test_update_room(mock_db):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = {"room_name": "RoomB", "Capacity": 15}

    payload = {
        "room_name": "RoomB",
        "Capacity": 15,
        "room_location": "Floor 3",
        "equipment": "Projector",
        "room_status": "Available"
    }

    result = rooms_model.update_room(payload)
    assert result["room_name"] == "RoomB"


def test_update_room_missing_fields():
    payload = {"room_name": None}
    result = rooms_model.update_room(payload)
    assert "error" in result


@patch("rooms_model.connect_to_db")
def test_delete_room(mock_db):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = {"room_name": "RoomC"}

    result = rooms_model.delete_room("RoomC")
    assert result["room_name"] == "RoomC"
    assert result["message"] == "Room deleted"


@patch("rooms_model.connect_to_db")
def test_search_rooms(mock_db):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        {"room_name": "RoomBig", "Capacity": 30}
    ]

    result = rooms_model.search_rooms(capacity=20)
    assert len(result) == 1
    assert result[0]["room_name"] == "RoomBig"
