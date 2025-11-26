import json
import os
import sys

import pytest
from unittest.mock import patch
from flask import Flask

SYS_PATH_ROOT = os.path.dirname(os.path.dirname(__file__))
if SYS_PATH_ROOT not in sys.path:
    sys.path.insert(0, SYS_PATH_ROOT)

from user_routes import user_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(user_bp)
    return app.test_client()


@patch("user_routes.get_users", return_value=[{"username": "lana"}])
def test_admin_get_users(mock_func, client):
    res = client.get("/admin/users")
    assert res.status_code == 200
    assert res.json == [{"username": "lana"}]


@patch("user_routes.get_user_by_username", return_value={"username": "lana"})
def test_admin_get_user(mock_func, client):
    res = client.get("/admin/users/lana")
    assert res.status_code == 200
    assert res.json["username"] == "lana"


@patch("user_routes.insert_user", return_value={"username": "lana"})
def test_admin_add_user_success(mock_insert, client):
    payload = {
        "user_name": "Lana",
        "username": "lana",
        "email": "lana@test.com",
        "password": "12345",
        "user_role": "admin"
    }
    res = client.post("/admin/users/add", json=payload)
    assert res.status_code == 201
    assert res.json["username"] == "lana"


def test_admin_add_user_missing_data(client):
    res = client.post("/admin/users/add", json={})
    assert res.status_code == 400
    assert "error" in res.json


@patch("user_routes.update_user", return_value={"username": "lana"})
def test_admin_update_user(mock_func, client):
    res = client.put("/admin/user/update", json={"username": "lana"})
    assert res.status_code == 200
    assert res.json["username"] == "lana"


@patch("user_routes.delete_user", return_value={"message": "User deleted"})
def test_admin_delete_user(mock_func, client):
    res = client.delete("/admin/users/delete/lana")
    assert res.status_code == 200
    assert res.json["message"] == "User deleted"


@patch("user_routes.update_role", return_value={"username": "lana", "user_role": "manager"})
def test_admin_update_role(mock_func, client):
    payload = {"username": "lana", "user_role": "manager"}
    res = client.put("/admin/update/user_role", json=payload)
    assert res.status_code == 200
    assert res.json["user_role"] == "manager"


@patch("user_routes.get_booking_history", return_value=[{"booking_id": 1}])
def test_admin_booking_history_success(mock_func, client):
    res = client.get("/admin/users/lana/booking_history")
    assert res.status_code == 200
    assert res.json["count"] == 1
    assert len(res.json["bookings"]) == 1


@patch("user_routes.get_booking_history", return_value=None)
def test_admin_booking_history_user_not_found(mock_func, client):
    res = client.get("/admin/users/unknown/booking_history")
    assert res.status_code == 404
    assert "error" in res.json


@patch("user_routes.reset_password", return_value={"username": "lana"})
def test_admin_reset_password(mock_func, client):
    payload = {"username": "lana", "new_password": "newpass"}
    res = client.put("/api/admin/reset_password", json=payload)
    assert res.status_code == 200
    assert res.json["username"] == "lana"


@patch("user_routes.get_user_by_username", return_value={"username": "lana"})
def test_regular_user_get(mock_func, client):
    res = client.get("/regular_user/lana")
    assert res.status_code == 200
    assert res.json["username"] == "lana"


@patch("user_routes.update_own_profile", return_value={"username": "lana"})
def test_regular_user_update(mock_func, client):
    res = client.put("/regular_user/update", json={"username": "lana"})
    assert res.status_code == 200
    assert res.json["username"] == "lana"


@patch("user_routes.get_booking_history", return_value=[{"booking_id": 1}])
def test_regular_user_booking_history_ok(mock_func, client):
    res = client.get("/regular_user/lana/booking_history")
    assert res.status_code == 200
    assert res.json["count"] == 1


@patch("user_routes.get_booking_history", return_value=None)
def test_regular_user_booking_history_not_found(mock_func, client):
    res = client.get("/regular_user/unknown/booking_history")
    assert res.status_code == 404
    assert "error" in res.json


@patch("user_routes.get_user_by_username", return_value={"username": "manager"})
def test_facility_manager_get(mock_func, client):
    res = client.get("/facility_manager/manager")
    assert res.status_code == 200
    assert res.json["username"] == "manager"


@patch("user_routes.update_own_profile", return_value={"username": "manager"})
def test_facility_manager_update(mock_func, client):
    res = client.put("/facility_manager/update", json={"username": "manager"})
    assert res.status_code == 200
    assert res.json["username"] == "manager"


@patch("user_routes.get_users", return_value=[{"username": "lana"}])
def test_auditor_users(mock_func, client):
    res = client.get("/auditor/users")
    assert res.status_code == 200
    assert res.json == [{"username": "lana"}]

@patch("user_routes.login_user", return_value={"username": "lana"})
def test_login_success(mock_func, client):
    payload = {"username": "lana", "password": "123"}
    res = client.post("/login", json=payload)
    assert res.status_code == 200
    assert res.json["message"] == "Login successful"


@patch("user_routes.login_user", return_value=None)
def test_login_user_not_found(mock_func, client):
    payload = {"username": "unknown", "password": "123"}
    res = client.post("/login", json=payload)
    assert res.status_code == 404
    assert "error" in res.json


@patch("user_routes.login_user", return_value=False)
def test_login_wrong_password(mock_func, client):
    payload = {"username": "lana", "password": "wrong"}
    res = client.post("/login", json=payload)
    assert res.status_code == 401
    assert "error" in res.json


def test_login_missing_fields(client):
    res = client.post("/login", json={"username": ""})
    assert res.status_code == 400
    assert "error" in res.json
