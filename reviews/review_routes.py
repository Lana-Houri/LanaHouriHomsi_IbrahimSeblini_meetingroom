"""
Review Routes
API endpoints for managing room and service reviews.
"""
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


review_bp = Blueprint('review_bp', __name__)


def get_user_from_request():
    """
    Extract user information from request headers.
    In a real implementation, this would verify JWT tokens or session.
    """
    user_id = request.headers.get('X-User-ID')
    user_role = request.headers.get('X-User-Role', 'regular user')
    
    if user_id:
        try:
            return int(user_id), user_role
        except ValueError:
            return None, None
    return None, None


@review_bp.route('/api/reviews', methods=['GET'])
def api_get_all_reviews():
    """
    Get all reviews.
    Admin, Moderator, and Auditor can view all reviews.
    """
    user_id, user_role = get_user_from_request()
    
    # Check authorization
    if user_role not in ['Admin', 'moderator', 'Auditor', 'Facility Manager']:
        return jsonify({"error": "Unauthorized: Only admins, moderators, auditors, and facility managers can view all reviews"}), 403
    
    reviews = get_all_reviews()
    return jsonify({"reviews": reviews, "count": len(reviews)}), 200


@review_bp.route('/api/reviews/<int:review_id>', methods=['GET'])
def api_get_review(review_id):
    """
    Get a specific review by ID.
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
def api_get_room_reviews(room_id):
    """
    Get reviews for a specific room.
    Regular users see non-flagged reviews, moderators/admins see all.
    """
    user_id, user_role = get_user_from_request()
    
    include_flagged = user_role in ['Admin', 'moderator', 'Auditor', 'Facility Manager']
    reviews = get_reviews_by_room(room_id, include_flagged=include_flagged)
    
    return jsonify({"reviews": reviews, "count": len(reviews), "room_id": room_id}), 200


@review_bp.route('/api/reviews/user/<int:user_id>', methods=['GET'])
def api_get_user_reviews(user_id):
    """
    Get reviews by a specific user.
    Users can view their own reviews, admins/moderators can view any user's reviews.
    """
    requesting_user_id, user_role = get_user_from_request()
    
    # Authorization check
    if requesting_user_id and user_role not in ['Admin', 'moderator', 'Auditor', 'Facility Manager']:
        if requesting_user_id != user_id:
            return jsonify({"error": "Unauthorized: You can only view your own reviews"}), 403
    
    reviews = get_user_reviews(user_id)
    return jsonify({"reviews": reviews, "count": len(reviews), "user_id": user_id}), 200


@review_bp.route('/api/reviews/flagged', methods=['GET'])
def api_get_flagged_reviews():
    """
    Get all flagged reviews for moderation.
    Moderators and Admins only.
    """
    user_id, user_role = get_user_from_request()
    
    if user_role not in ['Admin', 'moderator']:
        return jsonify({"error": "Unauthorized: Only admins and moderators can view flagged reviews"}), 403
    
    reviews = get_flagged_reviews()
    return jsonify({"reviews": reviews, "count": len(reviews)}), 200


@review_bp.route('/api/reviews', methods=['POST'])
def api_create_review():
    """
    Submit a new review for a meeting room.
    Required fields: user_id, room_id, rating (1-5), optional comment
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
    
    # Require authentication
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
    
    result = create_review(review_data)
    
    if result.get('error'):
        status_code = 400 if 'exist' in result.get('error', '') or 'Rating' in result.get('error', '') else 500
        return jsonify(result), status_code
    
    return jsonify(result), 201


@review_bp.route('/api/reviews/<int:review_id>', methods=['PUT'])
def api_update_review(review_id):
    """
    Update an existing review.
    Users can update their own reviews.
    """
    user_id, user_role = get_user_from_request()
    
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
    
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
def api_delete_review(review_id):
    """
    Delete a review.
    Users can delete their own reviews, moderators/admins can delete any.
    """
    user_id, user_role = get_user_from_request()
    
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
    
    is_admin = user_role == 'Admin'
    is_moderator = user_role == 'moderator'
    
    result = delete_review(review_id, user_id, is_admin, is_moderator)
    
    if result.get('error'):
        status_code = 403 if 'Unauthorized' in result.get('error', '') else 400
        return jsonify(result), status_code
    
    return jsonify(result), 200


@review_bp.route('/api/reviews/<int:review_id>/flag', methods=['POST'])
def api_flag_review(review_id):
    """
    Flag a review as inappropriate.
    Any authenticated user can flag reviews.
    """
    user_id, user_role = get_user_from_request()
    
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
    
    review_data = request.get_json() or {}
    flag_reason = review_data.get('flag_reason', 'Flagged by user')
    
    result = flag_review(review_id, flag_reason, user_id)
    
    if result.get('error'):
        return jsonify(result), 400
    
    return jsonify(result), 200


@review_bp.route('/api/moderator/reviews/<int:review_id>/unflag', methods=['PUT'])
def api_unflag_review(review_id):
    """
    Unflag a review (moderator/admin only).
    """
    user_id, user_role = get_user_from_request()
    
    if user_role not in ['Admin', 'moderator']:
        return jsonify({"error": "Unauthorized: Only admins and moderators can unflag reviews"}), 403
    
    result = unflag_review(review_id, user_id)
    
    if result.get('error'):
        return jsonify(result), 400
    
    return jsonify(result), 200


@review_bp.route('/api/moderator/reviews/<int:review_id>/remove', methods=['DELETE'])
def api_remove_review(review_id):
    """
    Remove a review (moderator/admin only).
    """
    user_id, user_role = get_user_from_request()
    
    if user_role not in ['Admin', 'moderator']:
        return jsonify({"error": "Unauthorized: Only admins and moderators can remove reviews"}), 403
    
    result = remove_review(review_id, user_id)
    
    if result.get('error'):
        return jsonify(result), 400
    
    return jsonify(result), 200


@review_bp.route('/api/admin/reviews/<int:review_id>', methods=['PUT'])
def api_admin_update_review(review_id):
    """
    Admin update review endpoint.
    Allows admins to override and update any review.
    """
    user_id, user_role = get_user_from_request()
    
    if user_role != 'Admin':
        return jsonify({"error": "Unauthorized: Only admins can override reviews"}), 403
    
    review_data = request.get_json()
    if not review_data:
        return jsonify({"error": "No review data provided"}), 400
    
    result = update_review(review_id, review_data, user_id, is_admin=True, is_moderator=True)
    
    if result.get('error'):
        return jsonify(result), 400
    
    return jsonify(result), 200


@review_bp.route('/api/auditor/reviews', methods=['GET'])
def api_auditor_get_reviews():
    """
    Get all reviews for auditing purposes (read-only).
    """
    user_id, user_role = get_user_from_request()
    
    if user_role != 'Auditor':
        return jsonify({"error": "Unauthorized: Only auditors can access this endpoint"}), 403
    
    reviews = get_all_reviews()
    return jsonify({"reviews": reviews, "count": len(reviews)}), 200

