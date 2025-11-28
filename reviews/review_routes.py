"""
Review Routes
API endpoints for managing room and service reviews.
"""
import sys
import os

# Add parent directory to path for shared_utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from flask import Blueprint, request, jsonify
from review_model import (
    get_all_reviews,
    get_review_by_id,
    get_reviews_by_room,
    get_user_reviews,
    get_flagged_reviews,
    create_review,
    update_review,
    delete_review,
    flag_review,
    unflag_review,
    remove_review,
    restore_review,
    hide_review,
    show_review,
    get_review_reports
)

import jwt
from functools import wraps

SECRET_KEY = "4a0f2b0f392b236fe7ff4081c27260fc5520c88962bc45403ce18c179754ef5b"

review_bp = Blueprint('review_bp', __name__)


def token_required(f):
    """
    Decorator that validates JWT tokens from the Authorization header.
    
    Functionality:
        Validates JWT tokens from the Authorization header in the format
        "Bearer <token>". Extracts user information (username, role) from the
        token and stores it in request.user for use in route handlers.
        Returns 401 Unauthorized if token is missing, invalid, or expired.
    
    Parameters:
        f (function): The route handler function to be decorated.
    
    Returns:
        function: Decorated function that validates JWT tokens before execution.
        If validation fails, returns JSON response with error message and 401 status.
    
    Token Format:
        Authorization: Bearer <token>
    
    Raises:
        Returns 401 if:
            - Token is missing
            - Token format is invalid
            - Token is expired
            - Token is invalid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Extract token from Authorization header
        if "Authorization" in request.headers:
            try:
                auth_header = request.headers["Authorization"]
                # Expected format: "Bearer <token>"
                parts = auth_header.split(" ")
                if len(parts) == 2 and parts[0] == "Bearer":
                    token = parts[1]
                else:
                    return jsonify({"error": "Token format must be: Bearer <token>"}), 401
            except Exception as e:
                return jsonify({"error": "Token format must be: Bearer <token>"}), 401

        if not token:
            return jsonify({"error": "Token missing. Please provide a valid token in Authorization header"}), 401

        # Validate and decode the token
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # Store user information in request for use in route handlers
            request.user = data
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired. Please login again"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401
        except Exception as e:
            return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401

        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """
    Decorator that ensures the user has one of the required roles.
    
    Functionality:
        Checks if the authenticated user's role (from JWT token) matches
        one of the allowed roles. Must be used after @token_required decorator.
        Returns 403 Forbidden if user's role is not in the allowed roles list.
    
    Parameters:
        *roles (str): Variable number of allowed role names.
            Examples: "Admin", "moderator", "Auditor", "Facility Manager", "regular user"
    
    Returns:
        function: Decorator function that checks user role before execution.
        If role check fails, returns JSON response with error message and 403 status.
    
    Raises:
        Returns 401 if user information is not found in token.
        Returns 403 if user's role is not in the allowed roles list.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Ensure request.user exists (should be set by token_required)
            if not hasattr(request, 'user') or 'role' not in request.user:
                return jsonify({"error": "User information not found in token"}), 401
            
            # Check if user's role is in the allowed roles
            if request.user["role"] not in roles:
                return jsonify({
                    "error": "Forbidden: Your role cannot access this resource",
                    "required_roles": list(roles),
                    "your_role": request.user["role"]
                }), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


def get_user_id_from_token():
    """
    Get user_id from JWT token by looking up username in database.
    
    Functionality:
        Extracts username from the JWT token stored in request.user and
        performs a database lookup to retrieve the corresponding user_id.
        This is necessary because JWT tokens contain username, not user_id.
    
    Parameters:
        None (uses request.user from token_required decorator)
    
    Returns:
        int or None: The user_id if found in database, None otherwise.
    
    Note:
        For better performance, consider including user_id directly in the
        JWT token payload to avoid database lookups.
    """
    if not hasattr(request, 'user') or 'username' not in request.user:
        return None
    
    try:
        # Try to get user_id from database using username
        conn = None
        try:
            from review_model import connect_to_db
            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM Users WHERE username = %s", (request.user["username"],))
            row = cur.fetchone()
            if row:
                return row[0]
        except Exception:
            pass
        finally:
            if conn:
                conn.close()
    except Exception:
        pass
    
    return None


def get_user_from_request():
    """
    Extract user information from JWT token.
    
    Functionality:
        Retrieves user_id (via database lookup) and role (from JWT token)
        for the authenticated user making the request.
    
    Parameters:
        None (uses request.user from token_required decorator)
    
    Returns:
        tuple: (user_id, user_role) where:
            - user_id (int or None): User ID from database lookup
            - user_role (str): User role from JWT token, defaults to "regular user"
        
        Returns (None, None) if request.user is not set.
    """
    if not hasattr(request, 'user'):
        return None, None
    
    user_id = get_user_id_from_token()
    user_role = request.user.get("role", "regular user")
    
    return user_id, user_role


@review_bp.route('/api/reviews', methods=['GET'])
@token_required
@role_required("Admin", "moderator", "Auditor", "Facility Manager")
def api_get_all_reviews():
    """
    Get all reviews.
    
    Functionality:
        Retrieves all reviews in the system.
        Only accessible to Admin, Moderator, Auditor, and Facility Manager roles.
    
    Parameters:
        None (uses JWT token from Authorization header)
    
    Returns:
        JSON response with status code 200 containing:
            {
                "reviews": [list of review dictionaries],
                "count": number of reviews
            }
        
        Returns 401 if token is missing or invalid.
        Returns 403 if user role is not authorized.
    
    Authorization:
        Required roles: Admin, moderator, Auditor, Facility Manager
    """
    reviews = get_all_reviews()
    return jsonify({"reviews": reviews, "count": len(reviews)}), 200


@review_bp.route('/api/reviews/<int:review_id>', methods=['GET'])
@token_required
def api_get_review(review_id):
    """
    Get a specific review by ID.
    
    Functionality:
        Retrieves a single review by its ID. Regular users cannot see flagged reviews,
        while Admin, Moderator, Auditor, and Facility Manager can see all reviews.
    
    Parameters:
        review_id (int): The ID of the review to retrieve.
    
    Returns:
        JSON response with status code 200 containing review details.
        
        Returns 401 if token is missing or invalid.
        Returns 404 if review is not found or is flagged (for regular users).
    
    Authorization:
        - Regular users: Cannot see flagged reviews
        - Admin, Moderator, Auditor, Facility Manager: Can see all reviews
    """
    review = get_review_by_id(review_id)
    
    if not review:
        return jsonify({"error": "Review not found"}), 404
    
    # Don't show flagged reviews to regular users
    user_id, user_role = get_user_from_request()
    if user_role not in ['Admin', 'moderator', 'Auditor', 'Facility Manager']:
        if review.get('is_flagged'):
            return jsonify({"error": "Review not found"}), 404
    
    return jsonify(review), 200


@review_bp.route('/api/reviews/room/<int:room_id>', methods=['GET'])
@token_required
def api_get_room_reviews(room_id):
    """
    Get reviews for a specific room.
    
    Functionality:
        Retrieves all reviews for a given room. Regular users see only non-flagged
        reviews, while Admin, Moderator, Auditor, and Facility Manager see all reviews.
    
    Parameters:
        room_id (int): The ID of the room whose reviews to retrieve.
    
    Returns:
        JSON response with status code 200 containing:
            {
                "reviews": [list of review dictionaries],
                "count": number of reviews,
                "room_id": room_id
            }
        
        Returns 401 if token is missing or invalid.
    
    Authorization:
        - Regular users: See only non-flagged reviews
        - Admin, Moderator, Auditor, Facility Manager: See all reviews
    """
    user_id, user_role = get_user_from_request()
    
    include_flagged = user_role in ['Admin', 'moderator', 'Auditor', 'Facility Manager']
    reviews = get_reviews_by_room(room_id, include_flagged=include_flagged)
    
    return jsonify({"reviews": reviews, "count": len(reviews), "room_id": room_id}), 200


@review_bp.route('/api/reviews/user/<int:user_id>', methods=['GET'])
@token_required
def api_get_user_reviews(user_id):
    """
    Get reviews by a specific user.
    
    Functionality:
        Retrieves all reviews by a given user. Regular users can only view their own
        reviews, while Admin, Moderator, Auditor, and Facility Manager can view any
        user's reviews.
    
    Parameters:
        user_id (int): The ID of the user whose reviews to retrieve.
    
    Returns:
        JSON response with status code 200 containing:
            {
                "reviews": [list of review dictionaries],
                "count": number of reviews,
                "user_id": user_id
            }
        
        Returns 401 if token is missing or invalid.
        Returns 403 if user tries to view another user's reviews (regular users only).
    
    Authorization:
        - Regular users: Can only view their own reviews
        - Admin, Moderator, Auditor, Facility Manager: Can view any user's reviews
    """
    requesting_user_id, user_role = get_user_from_request()
    
    # Authorization check
    if requesting_user_id and user_role not in ['Admin', 'moderator', 'Auditor', 'Facility Manager']:
        if requesting_user_id != user_id:
            return jsonify({"error": "Unauthorized: You can only view your own reviews"}), 403
    
    reviews = get_user_reviews(user_id)
    return jsonify({"reviews": reviews, "count": len(reviews), "user_id": user_id}), 200


@review_bp.route('/api/reviews/flagged', methods=['GET'])
@token_required
@role_required("Admin", "moderator")
def api_get_flagged_reviews():
    """
    Get all flagged reviews for moderation.
    
    Functionality:
        Retrieves all flagged reviews that need moderation.
        Only accessible to Admin and Moderator roles.
    
    Parameters:
        None (uses JWT token from Authorization header)
    
    Returns:
        JSON response with status code 200 containing:
            {
                "reviews": [list of flagged review dictionaries],
                "count": number of flagged reviews
            }
        
        Returns 401 if token is missing or invalid.
        Returns 403 if user role is not Admin or Moderator.
    
    Authorization:
        Required roles: Admin, moderator
    """
    reviews = get_flagged_reviews()
    return jsonify({"reviews": reviews, "count": len(reviews)}), 200


@review_bp.route('/api/reviews', methods=['POST'])
@token_required
def api_create_review():
    """
    Submit a new review for a meeting room.
    
    Functionality:
        Creates a new review for a meeting room. Regular users can only create
        reviews for themselves, while Admin and Facility Manager can create
        reviews for any user.
    
    Parameters:
        Request Body (JSON, required):
            user_id (int): ID of the user submitting the review.
            room_id (int): ID of the room being reviewed.
            rating (int): Rating from 1 to 5.
            comment (str, optional): Review comment.
    
    Returns:
        JSON response with status code 201 containing created review details.
        
        Returns 400 if:
            - No review data provided
            - Invalid rating
            - User or room does not exist
        Returns 401 if token is missing or invalid.
        Returns 403 if user tries to create review for another user (regular users only).
        Returns 500 for other errors.
    
    Authorization:
        - Regular users: Can only create reviews for themselves
        - Admin, Facility Manager: Can create reviews for any user
    """
    user_id, user_role = get_user_from_request()
    review_data = request.get_json()
    
    if not review_data:
        return jsonify({"error": "No review data provided"}), 400
    
    # Authorization: users can create reviews for themselves
    requesting_user_id = review_data.get('user_id')
    if user_id and user_role not in ['Admin', 'Facility Manager']:
        if requesting_user_id and int(requesting_user_id) != user_id:
            return jsonify({"error": "Unauthorized: You can only create reviews for yourself"}), 403
    
    result = create_review(review_data)
    
    if result.get('error'):
        status_code = 400 if 'exist' in result.get('error', '') or 'Rating' in result.get('error', '') else 500
        return jsonify(result), status_code
    
    return jsonify(result), 201


@review_bp.route('/api/reviews/<int:review_id>', methods=['PUT'])
@token_required
def api_update_review(review_id):
    """
    Update an existing review.
    
    Functionality:
        Updates an existing review. Regular users can only update their own reviews,
        while Admin and Moderator can update any review.
    
    Parameters:
        review_id (int): The ID of the review to update.
        
        Request Body (JSON, required):
            rating (int, optional): New rating (1-5).
            comment (str, optional): New comment.
    
    Returns:
        JSON response with status code 200 containing updated review details.
        
        Returns 400 if:
            - No review data provided
            - Invalid rating
        Returns 401 if token is missing or invalid.
        Returns 403 if user tries to update another user's review (regular users only).
    
    Authorization:
        - Regular users: Can only update their own reviews
        - Admin, Moderator: Can update any review
    """
    user_id, user_role = get_user_from_request()
    
    review_data = request.get_json()
    if not review_data:
        return jsonify({"error": "No review data provided"}), 400
    
    is_admin = user_role == 'Admin'
    is_moderator = user_role == 'moderator'
    
    result = update_review(review_id, review_data, user_id, is_admin, is_moderator)
    
    if result.get('error'):
        status_code = 403 if 'Unauthorized' in result.get('error', '') else 400
        return jsonify(result), status_code
    
    return jsonify(result), 200


@review_bp.route('/api/reviews/<int:review_id>', methods=['DELETE'])
@token_required
def api_delete_review(review_id):
    """
    Delete a review.
    
    Functionality:
        Deletes an existing review. Regular users can only delete their own reviews,
        while Admin and Moderator can delete any review.
    
    Parameters:
        review_id (int): The ID of the review to delete.
    
    Returns:
        JSON response with status code 200 containing deletion confirmation.
        
        Returns 400 if review cannot be deleted or other errors occur.
        Returns 401 if token is missing or invalid.
        Returns 403 if user tries to delete another user's review (regular users only).
    
    Authorization:
        - Regular users: Can only delete their own reviews
        - Admin, Moderator: Can delete any review
    """
    user_id, user_role = get_user_from_request()
    
    is_admin = user_role == 'Admin'
    is_moderator = user_role == 'moderator'
    
    result = delete_review(review_id, user_id, is_admin, is_moderator)
    
    if result.get('error'):
        status_code = 403 if 'Unauthorized' in result.get('error', '') else 400
        return jsonify(result), status_code
    
    return jsonify(result), 200


@review_bp.route('/api/reviews/<int:review_id>/flag', methods=['POST'])
@token_required
def api_flag_review(review_id):
    """
    Flag a review as inappropriate.
    
    Functionality:
        Flags a review as inappropriate. Any authenticated user can flag reviews.
        The review will be marked for moderation.
    
    Parameters:
        review_id (int): The ID of the review to flag.
        
        Request Body (JSON, optional):
            flag_reason (str): Reason for flagging (default: "Flagged by user").
    
    Returns:
        JSON response with status code 200 containing flagging confirmation.
        
        Returns 400 if review cannot be flagged or other errors occur.
        Returns 401 if token is missing or invalid.
    
    Authorization:
        Any authenticated user
    """
    user_id, user_role = get_user_from_request()
    
    review_data = request.get_json() or {}
    flag_reason = review_data.get('flag_reason', 'Flagged by user')
    
    result = flag_review(review_id, flag_reason, user_id)
    
    if result.get('error'):
        return jsonify(result), 400
    
    return jsonify(result), 200


@review_bp.route('/api/moderator/reviews/<int:review_id>/unflag', methods=['PUT'])
@token_required
@role_required("Admin", "moderator")
def api_unflag_review(review_id):
    """
    Unflag a review (Moderator/Admin only).
    
    Functionality:
        Removes the flag from a review. Only accessible to Admin and Moderator roles.
    
    Parameters:
        review_id (int): The ID of the review to unflag.
    
    Returns:
        JSON response with status code 200 containing unflag confirmation.
        
        Returns 400 if review cannot be unflagged or other errors occur.
        Returns 401 if token is missing or invalid.
        Returns 403 if user role is not Admin or Moderator.
    
    Authorization:
        Required roles: Admin, moderator
    """
    user_id, user_role = get_user_from_request()
    
    result = unflag_review(review_id, user_id)
    
    if result.get('error'):
        return jsonify(result), 400
    
    return jsonify(result), 200


@review_bp.route('/api/moderator/reviews/<int:review_id>/remove', methods=['DELETE'])
@token_required
@role_required("Admin", "moderator")
def api_remove_review(review_id):
    """
    Remove a review (Moderator/Admin only).
    
    Functionality:
        Permanently removes a review from the system. Only accessible to Admin
        and Moderator roles.
    
    Parameters:
        review_id (int): The ID of the review to remove.
    
    Returns:
        JSON response with status code 200 containing removal confirmation.
        
        Returns 400 if review cannot be removed or other errors occur.
        Returns 401 if token is missing or invalid.
        Returns 403 if user role is not Admin or Moderator.
    
    Authorization:
        Required roles: Admin, moderator
    """
    user_id, user_role = get_user_from_request()
    
    result = remove_review(review_id, user_id)
    
    if result.get('error'):
        return jsonify(result), 400
    
    return jsonify(result), 200


@review_bp.route('/api/admin/reviews/<int:review_id>', methods=['PUT'])
@token_required
@role_required("Admin")
def api_admin_update_review(review_id):
    """
    Admin update review endpoint.
    
    Functionality:
        Allows admins to override and update any review, bypassing normal
        authorization checks. This is used for administrative corrections.
    
    Parameters:
        review_id (int): The ID of the review to update.
        
        Request Body (JSON, required):
            rating (int, optional): New rating (1-5).
            comment (str, optional): New comment.
    
    Returns:
        JSON response with status code 200 containing updated review details.
        
        Returns 400 if:
            - No review data provided
            - Invalid rating
            - Other validation errors
        Returns 401 if token is missing or invalid.
        Returns 403 if user is not an Admin.
    
    Authorization:
        Required role: Admin
    """
    user_id, user_role = get_user_from_request()
    
    review_data = request.get_json()
    if not review_data:
        return jsonify({"error": "No review data provided"}), 400
    
    result = update_review(review_id, review_data, user_id, is_admin=True, is_moderator=True)
    
    if result.get('error'):
        return jsonify(result), 400
    
    return jsonify(result), 200


@review_bp.route('/api/auditor/reviews', methods=['GET'])
@token_required
@role_required("Auditor")
def api_auditor_get_reviews():
    """
    Get all reviews for auditing purposes (read-only).
    
    Functionality:
        Retrieves all reviews in the system for auditing purposes.
        Only accessible to Auditor role. This is a read-only endpoint.
    
    Parameters:
        None (uses JWT token from Authorization header)
    
    Returns:
        JSON response with status code 200 containing:
            {
                "reviews": [list of review dictionaries],
                "count": number of reviews
            }
        
        Returns 401 if token is missing or invalid.
        Returns 403 if user role is not Auditor.
    
    Authorization:
        Required role: Auditor
    """
    reviews = get_all_reviews()
    return jsonify({"reviews": reviews, "count": len(reviews)}), 200

