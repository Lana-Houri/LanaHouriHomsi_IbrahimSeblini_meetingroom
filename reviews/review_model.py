"""
Review Model
Handles all database operations for room and service reviews.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional
import html


def connect_to_db():
    """Establish connection to PostgreSQL database."""
    return psycopg2.connect(
        host="db",
        database="meetingroom",
        user="admin",
        password="password"
    )


def sanitize_input(text: Optional[str]) -> Optional[str]:
    """
    Sanitize user input to prevent XSS and SQL injection.
    
    Args:
        text: Input text to sanitize.
        
    Returns:
        Sanitized text or None.
    """
    if not text:
        return None
    # Escape HTML characters
    sanitized = html.escape(text)
    # Remove potential SQL injection patterns
    sanitized = sanitized.replace("'", "''")  # Escape single quotes for SQL
    return sanitized.strip()


def get_all_reviews() -> List[Dict]:
    """
    Retrieve all reviews with user and room details.
    
    Returns:
        List of review dictionaries.
    """
    reviews = []
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                r.review_id,
                r.user_id,
                r.room_id,
                r.rating,
                r.comment,
                r.is_flagged,
                r.flag_reason,
                r.is_moderated,
                r.moderated_by,
                r.created_at,
                r.updated_at,
                u.username,
                u.user_name,
                rm.room_name,
                rm.room_location
            FROM Reviews r
            JOIN Users u ON r.user_id = u.user_id
            JOIN Rooms rm ON r.room_id = rm.room_id
            ORDER BY r.created_at DESC
        """)
        rows = cur.fetchall()
        reviews = [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        reviews = []
    finally:
        if 'conn' in locals():
            conn.close()
    return reviews


def get_review_by_id(review_id: int) -> Dict:
    """
    Retrieve a specific review by ID.
    
    Args:
        review_id: The ID of the review to retrieve.
        
    Returns:
        Review dictionary or empty dict if not found.
    """
    review = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                r.review_id,
                r.user_id,
                r.room_id,
                r.rating,
                r.comment,
                r.is_flagged,
                r.flag_reason,
                r.is_moderated,
                r.moderated_by,
                r.created_at,
                r.updated_at,
                u.username,
                u.user_name,
                rm.room_name,
                rm.room_location
            FROM Reviews r
            JOIN Users u ON r.user_id = u.user_id
            JOIN Rooms rm ON r.room_id = rm.room_id
            WHERE r.review_id = %s
        """, (review_id,))
        row = cur.fetchone()
        if row:
            review = dict(row)
    except Exception as e:
        print(f"Error fetching review: {e}")
        review = {}
    finally:
        if 'conn' in locals():
            conn.close()
    return review


def get_reviews_by_room(room_id: int, include_flagged: bool = False) -> List[Dict]:
    """
    Retrieve all reviews for a specific room.
    
    Args:
        room_id: The ID of the room.
        include_flagged: Whether to include flagged reviews (moderators/admins only).
        
    Returns:
        List of review dictionaries for the room.
    """
    reviews = []
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if include_flagged:
            cur.execute("""
                SELECT 
                    r.review_id,
                    r.user_id,
                    r.room_id,
                    r.rating,
                    r.comment,
                    r.is_flagged,
                    r.flag_reason,
                    r.is_moderated,
                    r.moderated_by,
                    r.created_at,
                    r.updated_at,
                    u.username,
                    u.user_name,
                    rm.room_name,
                    rm.room_location
                FROM Reviews r
                JOIN Users u ON r.user_id = u.user_id
                JOIN Rooms rm ON r.room_id = rm.room_id
                WHERE r.room_id = %s
                ORDER BY r.created_at DESC
            """, (room_id,))
        else:
            cur.execute("""
                SELECT 
                    r.review_id,
                    r.user_id,
                    r.room_id,
                    r.rating,
                    r.comment,
                    r.is_flagged,
                    r.flag_reason,
                    r.is_moderated,
                    r.moderated_by,
                    r.created_at,
                    r.updated_at,
                    u.username,
                    u.user_name,
                    rm.room_name,
                    rm.room_location
                FROM Reviews r
                JOIN Users u ON r.user_id = u.user_id
                JOIN Rooms rm ON r.room_id = rm.room_id
                WHERE r.room_id = %s AND (r.is_flagged = FALSE OR r.is_flagged IS NULL)
                ORDER BY r.created_at DESC
            """, (room_id,))
        
        rows = cur.fetchall()
        reviews = [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching room reviews: {e}")
        reviews = []
    finally:
        if 'conn' in locals():
            conn.close()
    return reviews


def get_user_reviews(user_id: int) -> List[Dict]:
    """
    Retrieve all reviews by a specific user.
    
    Args:
        user_id: The ID of the user.
        
    Returns:
        List of review dictionaries by the user.
    """
    reviews = []
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                r.review_id,
                r.user_id,
                r.room_id,
                r.rating,
                r.comment,
                r.is_flagged,
                r.flag_reason,
                r.is_moderated,
                r.moderated_by,
                r.created_at,
                r.updated_at,
                u.username,
                u.user_name,
                rm.room_name,
                rm.room_location
            FROM Reviews r
            JOIN Users u ON r.user_id = u.user_id
            JOIN Rooms rm ON r.room_id = rm.room_id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
        """, (user_id,))
        rows = cur.fetchall()
        reviews = [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching user reviews: {e}")
        reviews = []
    finally:
        if 'conn' in locals():
            conn.close()
    return reviews


def get_flagged_reviews() -> List[Dict]:
    """
    Retrieve all flagged reviews for moderation.
    
    Returns:
        List of flagged review dictionaries.
    """
    reviews = []
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                r.review_id,
                r.user_id,
                r.room_id,
                r.rating,
                r.comment,
                r.is_flagged,
                r.flag_reason,
                r.is_moderated,
                r.moderated_by,
                r.created_at,
                r.updated_at,
                u.username,
                u.user_name,
                rm.room_name,
                rm.room_location
            FROM Reviews r
            JOIN Users u ON r.user_id = u.user_id
            JOIN Rooms rm ON r.room_id = rm.room_id
            WHERE r.is_flagged = TRUE
            ORDER BY r.created_at DESC
        """)
        rows = cur.fetchall()
        reviews = [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching flagged reviews: {e}")
        reviews = []
    finally:
        if 'conn' in locals():
            conn.close()
    return reviews


def check_user_exists(user_id: int) -> bool:
    """Check if a user exists."""
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM Users WHERE user_id = %s", (user_id,))
        return cur.fetchone() is not None
    except Exception as e:
        print(f"Error checking user: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


def check_room_exists(room_id: int) -> bool:
    """Check if a room exists."""
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT room_id FROM Rooms WHERE room_id = %s", (room_id,))
        return cur.fetchone() is not None
    except Exception as e:
        print(f"Error checking room: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


def create_review(review_data: Dict) -> Dict:
    """
    Create a new review.
    
    Args:
        review_data: Dictionary containing review details (user_id, room_id, rating, comment).
        
    Returns:
        Created review dictionary or error message.
    """
    result = {}
    conn = None
    try:
        # Validate required fields
        required_fields = ['user_id', 'room_id', 'rating']
        if not all(field in review_data for field in required_fields):
            return {"error": "Missing required fields: user_id, room_id, rating", "status": "error"}
        
        user_id = review_data['user_id']
        room_id = review_data['room_id']
        rating = review_data['rating']
        comment = review_data.get('comment')
        
        # Validate rating
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return {"error": "Rating must be between 1 and 5", "status": "error"}
        except (ValueError, TypeError):
            return {"error": "Invalid rating value", "status": "error"}
        
        # Validate user and room exist
        if not check_user_exists(user_id):
            return {"error": "User does not exist", "status": "error"}
        
        if not check_room_exists(room_id):
            return {"error": "Room does not exist", "status": "error"}
        
        # Sanitize comment
        sanitized_comment = sanitize_input(comment) if comment else None
        
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO Reviews (user_id, room_id, rating, comment)
            VALUES (%s, %s, %s, %s)
            RETURNING review_id, user_id, room_id, rating, comment, is_flagged, is_moderated, created_at, updated_at
        """, (user_id, room_id, rating, sanitized_comment))
        
        row = cur.fetchone()
        conn.commit()
        
        if row:
            result = dict(row)
            # Fetch additional details
            cur.execute("""
                SELECT 
                    r.review_id,
                    r.user_id,
                    r.room_id,
                    r.rating,
                    r.comment,
                    r.is_flagged,
                    r.flag_reason,
                    r.is_moderated,
                    r.moderated_by,
                    r.created_at,
                    r.updated_at,
                    u.username,
                    u.user_name,
                    rm.room_name,
                    rm.room_location
                FROM Reviews r
                JOIN Users u ON r.user_id = u.user_id
                JOIN Rooms rm ON r.room_id = rm.room_id
                WHERE r.review_id = %s
            """, (result['review_id'],))
            full_row = cur.fetchone()
            if full_row:
                result = dict(full_row)
        
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to create review: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result


def update_review(review_id: int, review_data: Dict, user_id: Optional[int] = None, is_admin: bool = False, is_moderator: bool = False) -> Dict:
    """
    Update an existing review.
    
    Args:
        review_id: The ID of the review to update.
        review_data: Dictionary containing fields to update.
        user_id: ID of the user making the request (for authorization).
        is_admin: Whether the user is an admin.
        is_moderator: Whether the user is a moderator (lowercase 'moderator' role).
        
    Returns:
        Updated review dictionary or error message.
    """
    result = {}
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if review exists and user has permission
        cur.execute("SELECT user_id FROM Reviews WHERE review_id = %s", (review_id,))
        existing = cur.fetchone()
        
        if not existing:
            return {"error": "Review not found", "status": "error"}
        
        existing_user_id = existing['user_id']
        
        # Authorization check: users can update their own reviews, admins/moderators can update any
        if user_id and not is_admin and not is_moderator:
            if existing_user_id != user_id:
                return {"error": "Unauthorized: You can only update your own reviews", "status": "error"}
        
        # Get updated values
        rating = review_data.get('rating')
        comment = review_data.get('comment')
        
        # Validate rating if provided
        if rating is not None:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    return {"error": "Rating must be between 1 and 5", "status": "error"}
            except (ValueError, TypeError):
                return {"error": "Invalid rating value", "status": "error"}
        
        # Sanitize comment if provided
        sanitized_comment = sanitize_input(comment) if comment is not None else None
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if rating is not None:
            update_fields.append("rating = %s")
            params.append(rating)
        
        if comment is not None:
            update_fields.append("comment = %s")
            params.append(sanitized_comment)
        
        if not update_fields:
            return {"error": "No fields to update", "status": "error"}
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(review_id)
        
        cur.execute(f"""
            UPDATE Reviews 
            SET {', '.join(update_fields)}
            WHERE review_id = %s
            RETURNING review_id, user_id, room_id, rating, comment, is_flagged, flag_reason, is_moderated, moderated_by, created_at, updated_at
        """, tuple(params))
        
        row = cur.fetchone()
        conn.commit()
        
        if row:
            result = dict(row)
            # Fetch additional details
            cur.execute("""
                SELECT 
                    r.review_id,
                    r.user_id,
                    r.room_id,
                    r.rating,
                    r.comment,
                    r.is_flagged,
                    r.flag_reason,
                    r.is_moderated,
                    r.moderated_by,
                    r.created_at,
                    r.updated_at,
                    u.username,
                    u.user_name,
                    rm.room_name,
                    rm.room_location
                FROM Reviews r
                JOIN Users u ON r.user_id = u.user_id
                JOIN Rooms rm ON r.room_id = rm.room_id
                WHERE r.review_id = %s
            """, (review_id,))
            full_row = cur.fetchone()
            if full_row:
                result = dict(full_row)
        
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to update review: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result


def delete_review(review_id: int, user_id: Optional[int] = None, is_admin: bool = False, is_moderator: bool = False) -> Dict:
    """
    Delete a review.
    
    Args:
        review_id: The ID of the review to delete.
        user_id: ID of the user making the request (for authorization).
        is_admin: Whether the user is an admin.
        is_moderator: Whether the user is a moderator (lowercase 'moderator' role).
        
    Returns:
        Success message or error.
    """
    result = {}
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if review exists and user has permission
        cur.execute("SELECT user_id FROM Reviews WHERE review_id = %s", (review_id,))
        existing = cur.fetchone()
        
        if not existing:
            return {"error": "Review not found", "status": "error"}
        
        existing_user_id = existing['user_id']
        
        # Authorization check: users can delete their own reviews, admins/moderators can delete any
        if user_id and not is_admin and not is_moderator:
            if existing_user_id != user_id:
                return {"error": "Unauthorized: You can only delete your own reviews", "status": "error"}
        
        # Delete review
        cur.execute("DELETE FROM Reviews WHERE review_id = %s RETURNING review_id", (review_id,))
        deleted = cur.fetchone()
        conn.commit()
        
        if deleted:
            result = {"message": "Review deleted successfully", "review_id": review_id, "status": "success"}
        else:
            result = {"error": "Failed to delete review", "status": "error"}
        
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to delete review: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result


def flag_review(review_id: int, flag_reason: Optional[str] = None, user_id: Optional[int] = None) -> Dict:
    """
    Flag a review as inappropriate.
    
    Args:
        review_id: The ID of the review to flag.
        flag_reason: Reason for flagging the review.
        user_id: ID of the user flagging the review.
        
    Returns:
        Success message or error.
    """
    result = {}
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if review exists
        cur.execute("SELECT is_flagged FROM Reviews WHERE review_id = %s", (review_id,))
        existing = cur.fetchone()
        
        if not existing:
            return {"error": "Review not found", "status": "error"}
        
        if existing['is_flagged']:
            return {"error": "Review is already flagged", "status": "error"}
        
        # Sanitize flag reason
        sanitized_reason = sanitize_input(flag_reason) if flag_reason else "Flagged by user"
        
        # Flag review
        cur.execute("""
            UPDATE Reviews 
            SET is_flagged = TRUE,
                flag_reason = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE review_id = %s
            RETURNING review_id, is_flagged, flag_reason
        """, (sanitized_reason, review_id))
        
        row = cur.fetchone()
        conn.commit()
        
        if row:
            result = {"message": "Review flagged successfully", "review_id": review_id, "status": "success"}
        else:
            result = {"error": "Failed to flag review", "status": "error"}
        
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to flag review: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result


def unflag_review(review_id: int, moderator_id: Optional[int] = None) -> Dict:
    """
    Unflag a review (moderator/admin only).
    
    Args:
        review_id: The ID of the review to unflag.
        moderator_id: ID of the moderator/admin unflagging the review.
        
    Returns:
        Success message or error.
    """
    result = {}
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if review exists
        cur.execute("SELECT is_flagged FROM Reviews WHERE review_id = %s", (review_id,))
        existing = cur.fetchone()
        
        if not existing:
            return {"error": "Review not found", "status": "error"}
        
        if not existing['is_flagged']:
            return {"error": "Review is not flagged", "status": "error"}
        
        # Unflag review
        cur.execute("""
            UPDATE Reviews 
            SET is_flagged = FALSE,
                flag_reason = NULL,
                is_moderated = TRUE,
                moderated_by = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE review_id = %s
            RETURNING review_id, is_flagged, is_moderated
        """, (moderator_id, review_id))
        
        row = cur.fetchone()
        conn.commit()
        
        if row:
            result = {"message": "Review unflagged successfully", "review_id": review_id, "status": "success"}
        else:
            result = {"error": "Failed to unflag review", "status": "error"}
        
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to unflag review: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result


def remove_review(review_id: int, moderator_id: Optional[int] = None) -> Dict:
    """
    Remove a review (moderator/admin only - soft delete by marking as moderated and flagged).
    
    Args:
        review_id: The ID of the review to remove.
        moderator_id: ID of the moderator/admin removing the review.
        
    Returns:
        Success message or error.
    """
    result = {}
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if review exists
        cur.execute("SELECT review_id FROM Reviews WHERE review_id = %s", (review_id,))
        existing = cur.fetchone()
        
        if not existing:
            return {"error": "Review not found", "status": "error"}
        
        # Mark as moderated and keep flagged
        cur.execute("""
            UPDATE Reviews 
            SET is_moderated = TRUE,
                moderated_by = %s,
                is_flagged = TRUE,
                flag_reason = 'Removed by moderator',
                updated_at = CURRENT_TIMESTAMP
            WHERE review_id = %s
            RETURNING review_id, is_moderated
        """, (moderator_id, review_id))
        
        row = cur.fetchone()
        conn.commit()
        
        if row:
            result = {"message": "Review removed by moderator", "review_id": review_id, "status": "success"}
        else:
            result = {"error": "Failed to remove review", "status": "error"}
        
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to remove review: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result

