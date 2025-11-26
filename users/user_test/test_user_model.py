import os
import sys

import pytest
from unittest.mock import patch, MagicMock

SYS_PATH_ROOT = os.path.dirname(os.path.dirname(__file__))
if SYS_PATH_ROOT not in sys.path:
    sys.path.insert(0, SYS_PATH_ROOT)

import user_model

@pytest.fixture
def mock_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


@patch("user_model.connect_to_db")
def test_get_users(mock_db):
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor

    cursor.fetchall.return_value = [{"username": "lana19"}]

    result = user_model.get_users()
    assert result == [{"username": "lana19"}]

@patch("user_model.connect_to_db")
def test_get_user_by_username(mock_db):
    conn, cursor = MagicMock(), MagicMock()
    mock_db.return_value = conn
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = {"username": "lana19"}

    result = user_model.get_user_by_username("lana19")
    assert result["username"] == "lana19"

@patch("user_model.generate_password_hash", return_value="fakehashed")
@patch("user_model.connect_to_db")
def test_insert_user(mock_db, mock_hash):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = {"username": "lana19"}

    payload = {
        "user_name": "Lana",
        "username": "lana19",
        "email": "lana@test.com",
        "password": "pass123",
        "user_role": "admin"
    }

    result = user_model.insert_user(payload)
    assert result["username"] == "lana19"
    mock_hash.assert_called_once()

@patch("user_model.connect_to_db")
def test_update_user(mock_db):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = {"username": "lana19"}

    data = {
        "user_name": "New Lana",
        "username": "lana19",
        "email": "lana@test.com",
        "user_role": "admin",
        "username_old": "oldlana"
    }

    result = user_model.update_user(data)
    assert result["username"] == "lana19"

@patch("user_model.connect_to_db")
def test_update_role(mock_db):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = {"username": "lana19", "user_role": "manager"}

    result = user_model.update_role("lana19", "manager")
    assert result["user_role"] == "manager"

@patch("user_model.connect_to_db")
def test_delete_user(mock_db):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = {"username": "lana19"}

    result = user_model.delete_user("lana19")
    assert result["username"] == "lana19"
    assert result["message"] == "User deleted"

@patch("user_model.generate_password_hash", return_value="newhash")
@patch("user_model.connect_to_db")
def test_reset_password(mock_db, mock_hash):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = {"username": "lana19"}

    result = user_model.reset_password("lana19", "newpass")
    assert result["username"] == "lana19"
    mock_hash.assert_called_once()

@patch("user_model.generate_password_hash", return_value="hashed")
@patch("user_model.connect_to_db")
def test_update_own_profile(mock_db, mock_hash):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "username": "lana19",
        "email": "new@test.com"
    }

    payload = {
        "username": "lana19",
        "user_name": "Updated Name",
        "email": "new@test.com",
        "password": "newpass"
    }

    result = user_model.update_own_profile(payload)
    assert result["username"] == "lana19"

@patch("user_model.check_password_hash", return_value=True)
@patch("user_model.connect_to_db")
def test_login_user_success(mock_db, mock_check):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "user_id": 1,
        "user_name": "Lana",
        "username": "lana19",
        "email": "lana@test.com",
        "password_hash": "hashed",
        "user_role": "regular user"
    }

    result = user_model.login_user("lana19", "correctpass")
    assert result["username"] == "lana19"

@patch("user_model.check_password_hash", return_value=False)
@patch("user_model.connect_to_db")
def test_login_user_wrong_password(mock_db, mock_check):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "username": "lana19",
        "password_hash": "hashed"
    }

    result = user_model.login_user("lana19", "wrongpass")
    assert result is False

@patch("user_model.connect_to_db")
def test_get_booking_history(mock_db):
    conn, cursor = mock_db.return_value, MagicMock()
    conn.cursor.return_value = cursor

    cursor.fetchone.side_effect = [
        {"user_id": 10},
    ]

    cursor.fetchall.return_value = [
        {"booking_id": 1, "room": "A1"}
    ]

    result = user_model.get_booking_history("lana19")
    assert len(result) == 1
    assert result[0]["booking_id"] == 1
