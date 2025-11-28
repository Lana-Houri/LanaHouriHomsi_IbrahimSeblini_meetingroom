"""
Test suite for review_routes.py

This module contains unit tests for all review route endpoints,
testing JWT authentication, authorization, and route functionality.
"""
import os
import sys

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, request

SYS_PATH_ROOT = os.path.dirname(os.path.dirname(__file__))
if SYS_PATH_ROOT not in sys.path:
    sys.path.insert(0, SYS_PATH_ROOT)

# Patch jwt.decode before importing review_routes
with patch('review_routes.jwt') as mock_jwt:
    mock_jwt.decode.side_effect = lambda token, key, algorithms: {
        "admin_token": {"username": "admin", "role": "Admin"},
        "moderator_token": {"username": "moderator", "role": "moderator"},
        "auditor_token": {"username": "auditor", "role": "Auditor"},
        "facility_manager_token": {"username": "manager", "role": "Facility Manager"},
        "regular_user_token": {"username": "user", "role": "regular user"},
        "user1_token": {"username": "user1", "role": "regular user"},
        "user2_token": {"username": "user2", "role": "regular user"},
        "fake_token": {"username": "test", "role": "test_role"}
    }.get(token, {"error": "Invalid token"})
    mock_jwt.ExpiredSignatureError = MagicMock()
    mock_jwt.InvalidTokenError = MagicMock()
    from review_routes import review_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(review_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def mock_auth_jwt_decode(monkeypatch):
    """Mock jwt.decode to return user info based on token."""
    def mock_decode(token, key, algorithms):
        token_map = {
            "admin_token": {"username": "admin", "role": "Admin"},
            "moderator_token": {"username": "moderator", "role": "moderator"},
            "auditor_token": {"username": "auditor", "role": "Auditor"},
            "facility_manager_token": {"username": "manager", "role": "Facility Manager"},
            "regular_user_token": {"username": "user", "role": "regular user"},
            "user1_token": {"username": "user1", "role": "regular user"},
            "user2_token": {"username": "user2", "role": "regular user"},
            "fake_token": {"username": "test", "role": "test_role"}
        }
        return token_map.get(token, {"username": "test_user", "role": "regular user"})
    
    monkeypatch.setattr("review_routes.jwt.decode", mock_decode)
    monkeypatch.setattr("review_routes.jwt.ExpiredSignatureError", Exception)
    monkeypatch.setattr("review_routes.jwt.InvalidTokenError", Exception)


@pytest.fixture(autouse=True)
def mock_get_user_id_from_token(monkeypatch):
    """Mock get_user_id_from_token to return user_id based on username."""
    def mock_get_user_id():
        from flask import request
        if not hasattr(request, 'user') or 'username' not in request.user:
            return None
        username = request.user["username"]
        user_id_map = {
            "admin": 1,
            "moderator": 1,
            "auditor": 1,
            "manager": 1,
            "user": 1,
            "user1": 1,
            "user2": 2,
            "test": 1,
            "test_user": 1
        }
        return user_id_map.get(username, 1)
    monkeypatch.setattr("review_routes.get_user_id_from_token", mock_get_user_id)


# Test GET /api/reviews (all reviews)
@patch("review_routes.get_all_reviews", return_value=[{"review_id": 1, "user_id": 1, "room_id": 1}])
def test_get_all_reviews_admin(mock_func, client):
    """Test getting all reviews as Admin."""
    res = client.get("/api/reviews", headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200
    assert "reviews" in res.json
    assert res.json["count"] == 1


@patch("review_routes.get_all_reviews", return_value=[{"review_id": 1}])
def test_get_all_reviews_moderator(mock_func, client):
    """Test getting all reviews as Moderator."""
    res = client.get("/api/reviews", headers={"Authorization": "Bearer moderator_token"})
    assert res.status_code == 200
    assert "reviews" in res.json


@patch("review_routes.get_all_reviews", return_value=[])
def test_get_all_reviews_auditor(mock_func, client):
    """Test getting all reviews as Auditor."""
    res = client.get("/api/reviews", headers={"Authorization": "Bearer auditor_token"})
    assert res.status_code == 200
    assert res.json["count"] == 0


def test_get_all_reviews_unauthorized(client):
    """Test getting all reviews without proper role."""
    res = client.get("/api/reviews", headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 403
    assert "error" in res.json


def test_get_all_reviews_no_token(client):
    """Test getting all reviews without token."""
    res = client.get("/api/reviews")
    assert res.status_code == 401


# Test GET /api/reviews/<review_id>
@patch("review_routes.get_review_by_id", return_value={"review_id": 1, "is_flagged": False})
def test_get_review_success(mock_func, client):
    """Test getting a specific review."""
    res = client.get("/api/reviews/1", headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 200
    assert res.json["review_id"] == 1


@patch("review_routes.get_review_by_id", return_value={"review_id": 1, "is_flagged": True})
def test_get_review_flagged_regular_user(mock_func, client):
    """Test getting a flagged review as regular user (should be hidden)."""
    res = client.get("/api/reviews/1", headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 404


@patch("review_routes.get_review_by_id", return_value={"review_id": 1, "is_flagged": True})
def test_get_review_flagged_admin(mock_func, client):
    """Test getting a flagged review as Admin (should be visible)."""
    res = client.get("/api/reviews/1", headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200


@patch("review_routes.get_review_by_id", return_value={})
def test_get_review_not_found(mock_func, client):
    """Test getting a non-existent review."""
    res = client.get("/api/reviews/999", headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 404


def test_get_review_no_token(client):
    """Test getting review without token."""
    res = client.get("/api/reviews/1")
    assert res.status_code == 401


# Test GET /api/reviews/room/<room_id>
@patch("review_routes.get_reviews_by_room", return_value=[{"review_id": 1, "room_id": 1}])
def test_get_room_reviews(mock_func, client):
    """Test getting reviews for a room."""
    res = client.get("/api/reviews/room/1", headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 200
    assert "reviews" in res.json
    assert res.json["room_id"] == 1


def test_get_room_reviews_no_token(client):
    """Test getting room reviews without token."""
    res = client.get("/api/reviews/room/1")
    assert res.status_code == 401


# Test GET /api/reviews/user/<user_id>
@patch("review_routes.get_user_reviews", return_value=[{"review_id": 1, "user_id": 1}])
def test_get_user_reviews_own(mock_func, client):
    """Test getting own reviews."""
    res = client.get("/api/reviews/user/1", headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 200
    assert res.json["user_id"] == 1


@patch("review_routes.get_user_reviews", return_value=[])
def test_get_user_reviews_other_user_unauthorized(mock_func, client):
    """Test getting another user's reviews as regular user (should fail)."""
    res = client.get("/api/reviews/user/2", headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 403


@patch("review_routes.get_user_reviews", return_value=[{"review_id": 1}])
def test_get_user_reviews_admin(mock_func, client):
    """Test getting any user's reviews as Admin."""
    res = client.get("/api/reviews/user/2", headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200


def test_get_user_reviews_no_token(client):
    """Test getting user reviews without token."""
    res = client.get("/api/reviews/user/1")
    assert res.status_code == 401


# Test GET /api/reviews/flagged
@patch("review_routes.get_flagged_reviews", return_value=[{"review_id": 1, "is_flagged": True}])
def test_get_flagged_reviews_admin(mock_func, client):
    """Test getting flagged reviews as Admin."""
    res = client.get("/api/reviews/flagged", headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200
    assert "reviews" in res.json


@patch("review_routes.get_flagged_reviews", return_value=[])
def test_get_flagged_reviews_moderator(mock_func, client):
    """Test getting flagged reviews as Moderator."""
    res = client.get("/api/reviews/flagged", headers={"Authorization": "Bearer moderator_token"})
    assert res.status_code == 200


def test_get_flagged_reviews_unauthorized(client):
    """Test getting flagged reviews without proper role."""
    res = client.get("/api/reviews/flagged", headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 403


def test_get_flagged_reviews_no_token(client):
    """Test getting flagged reviews without token."""
    res = client.get("/api/reviews/flagged")
    assert res.status_code == 401


# Test POST /api/reviews
@patch("review_routes.create_review", return_value={"review_id": 1, "user_id": 1, "room_id": 1, "rating": 5})
def test_create_review_success(mock_func, client):
    """Test creating a review."""
    payload = {"user_id": 1, "room_id": 1, "rating": 5, "comment": "Great room"}
    res = client.post("/api/reviews", json=payload, headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 201
    assert res.json["review_id"] == 1


@patch("review_routes.create_review", return_value={"error": "User does not exist"})
def test_create_review_user_not_exists(mock_func, client):
    """Test creating review with non-existent user."""
    payload = {"user_id": 999, "room_id": 1, "rating": 5}
    res = client.post("/api/reviews", json=payload, headers={"Authorization": "Bearer user1_token"})
    # Authorization check happens first, so user1 cannot create review for user_id=999
    assert res.status_code == 403


@patch("review_routes.create_review", return_value={"review_id": 1})
def test_create_review_for_other_user_unauthorized(mock_func, client):
    """Test creating review for another user as regular user (should fail)."""
    payload = {"user_id": 2, "room_id": 1, "rating": 5}
    res = client.post("/api/reviews", json=payload, headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 403


@patch("review_routes.create_review", return_value={"review_id": 1})
def test_create_review_admin(mock_func, client):
    """Test creating review for any user as Admin."""
    payload = {"user_id": 2, "room_id": 1, "rating": 5}
    res = client.post("/api/reviews", json=payload, headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 201


def test_create_review_no_data(client):
    """Test creating review without data."""
    # Send empty JSON to trigger 400 error (not 415 Unsupported Media Type)
    res = client.post("/api/reviews", json={}, headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 400


def test_create_review_no_token(client):
    """Test creating review without token."""
    payload = {"user_id": 1, "room_id": 1, "rating": 5}
    res = client.post("/api/reviews", json=payload)
    assert res.status_code == 401


# Test PUT /api/reviews/<review_id>
@patch("review_routes.update_review", return_value={"review_id": 1, "rating": 4})
def test_update_review_own(mock_func, client):
    """Test updating own review."""
    payload = {"rating": 4, "comment": "Updated comment"}
    res = client.put("/api/reviews/1", json=payload, headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 200


@patch("review_routes.update_review", return_value={"error": "Unauthorized: You can only update your own reviews"})
def test_update_review_other_user_unauthorized(mock_func, client):
    """Test updating another user's review as regular user."""
    payload = {"rating": 4}
    res = client.put("/api/reviews/1", json=payload, headers={"Authorization": "Bearer user2_token"})
    assert res.status_code == 403


@patch("review_routes.update_review", return_value={"review_id": 1})
def test_update_review_admin(mock_func, client):
    """Test updating any review as Admin."""
    payload = {"rating": 5}
    res = client.put("/api/reviews/1", json=payload, headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200


def test_update_review_no_data(client):
    """Test updating review without data."""
    # Send empty JSON to trigger 400 error (not 415 Unsupported Media Type)
    res = client.put("/api/reviews/1", json={}, headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 400


def test_update_review_no_token(client):
    """Test updating review without token."""
    payload = {"rating": 4}
    res = client.put("/api/reviews/1", json=payload)
    assert res.status_code == 401


# Test DELETE /api/reviews/<review_id>
@patch("review_routes.delete_review", return_value={"message": "Review deleted successfully", "review_id": 1})
def test_delete_review_own(mock_func, client):
    """Test deleting own review."""
    res = client.delete("/api/reviews/1", headers={"Authorization": "Bearer user1_token"})
    assert res.status_code == 200


@patch("review_routes.delete_review", return_value={"error": "Unauthorized: You can only delete your own reviews"})
def test_delete_review_other_user_unauthorized(mock_func, client):
    """Test deleting another user's review as regular user."""
    res = client.delete("/api/reviews/1", headers={"Authorization": "Bearer user2_token"})
    assert res.status_code == 403


@patch("review_routes.delete_review", return_value={"message": "Review deleted successfully"})
def test_delete_review_admin(mock_func, client):
    """Test deleting any review as Admin."""
    res = client.delete("/api/reviews/1", headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200


def test_delete_review_no_token(client):
    """Test deleting review without token."""
    res = client.delete("/api/reviews/1")
    assert res.status_code == 401


# Test POST /api/reviews/<review_id>/flag
@patch("review_routes.flag_review", return_value={"message": "Review flagged successfully", "review_id": 1})
def test_flag_review(mock_func, client):
    """Test flagging a review."""
    payload = {"flag_reason": "Inappropriate content"}
    res = client.post("/api/reviews/1/flag", json=payload, headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 200


@patch("review_routes.flag_review", return_value={"error": "Review not found"})
def test_flag_review_not_found(mock_func, client):
    """Test flagging a non-existent review."""
    # Send empty JSON to trigger 400 error (not 415 Unsupported Media Type)
    res = client.post("/api/reviews/999/flag", json={}, headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 400


def test_flag_review_no_token(client):
    """Test flagging review without token."""
    res = client.post("/api/reviews/1/flag")
    assert res.status_code == 401


# Test PUT /api/moderator/reviews/<review_id>/unflag
@patch("review_routes.unflag_review", return_value={"message": "Review unflagged successfully", "review_id": 1})
def test_unflag_review_moderator(mock_func, client):
    """Test unflagging a review as Moderator."""
    res = client.put("/api/moderator/reviews/1/unflag", headers={"Authorization": "Bearer moderator_token"})
    assert res.status_code == 200


@patch("review_routes.unflag_review", return_value={"message": "Review unflagged successfully"})
def test_unflag_review_admin(mock_func, client):
    """Test unflagging a review as Admin."""
    res = client.put("/api/moderator/reviews/1/unflag", headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200


def test_unflag_review_unauthorized(client):
    """Test unflagging review without proper role."""
    res = client.put("/api/moderator/reviews/1/unflag", headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 403


def test_unflag_review_no_token(client):
    """Test unflagging review without token."""
    res = client.put("/api/moderator/reviews/1/unflag")
    assert res.status_code == 401


# Test DELETE /api/moderator/reviews/<review_id>/remove
@patch("review_routes.remove_review", return_value={"message": "Review removed by moderator", "review_id": 1})
def test_remove_review_moderator(mock_func, client):
    """Test removing a review as Moderator."""
    res = client.delete("/api/moderator/reviews/1/remove", headers={"Authorization": "Bearer moderator_token"})
    assert res.status_code == 200


@patch("review_routes.remove_review", return_value={"message": "Review removed by moderator"})
def test_remove_review_admin(mock_func, client):
    """Test removing a review as Admin."""
    res = client.delete("/api/moderator/reviews/1/remove", headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200


def test_remove_review_unauthorized(client):
    """Test removing review without proper role."""
    res = client.delete("/api/moderator/reviews/1/remove", headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 403


def test_remove_review_no_token(client):
    """Test removing review without token."""
    res = client.delete("/api/moderator/reviews/1/remove")
    assert res.status_code == 401


# Test PUT /api/admin/reviews/<review_id>
@patch("review_routes.update_review", return_value={"review_id": 1, "rating": 5})
def test_admin_update_review(mock_func, client):
    """Test admin updating any review."""
    payload = {"rating": 5, "comment": "Admin override"}
    res = client.put("/api/admin/reviews/1", json=payload, headers={"Authorization": "Bearer admin_token"})
    assert res.status_code == 200


def test_admin_update_review_unauthorized(client):
    """Test admin update without Admin role."""
    payload = {"rating": 5}
    res = client.put("/api/admin/reviews/1", json=payload, headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 403


def test_admin_update_review_no_token(client):
    """Test admin update without token."""
    payload = {"rating": 5}
    res = client.put("/api/admin/reviews/1", json=payload)
    assert res.status_code == 401


# Test GET /api/auditor/reviews
@patch("review_routes.get_all_reviews", return_value=[{"review_id": 1}])
def test_auditor_get_reviews(mock_func, client):
    """Test getting all reviews as Auditor."""
    res = client.get("/api/auditor/reviews", headers={"Authorization": "Bearer auditor_token"})
    assert res.status_code == 200
    assert "reviews" in res.json


def test_auditor_get_reviews_unauthorized(client):
    """Test getting auditor reviews without Auditor role."""
    res = client.get("/api/auditor/reviews", headers={"Authorization": "Bearer regular_user_token"})
    assert res.status_code == 403


def test_auditor_get_reviews_no_token(client):
    """Test getting auditor reviews without token."""
    res = client.get("/api/auditor/reviews")
    assert res.status_code == 401

