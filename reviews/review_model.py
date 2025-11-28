"""
Review Model
Handles all database operations for room and service reviews.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional
import html


def connect_to_db():
    """
    Establish connection to PostgreSQL database.
    
    Functionality:
        Creates and returns a connection to the PostgreSQL database used for
        storing review data. Uses hardcoded connection parameters.
    
    Parameters:
        None
    
    Returns:
        psycopg2.connection: Database connection object.
        
        Raises psycopg2.OperationalError if connection fails.
    """
    return psycopg2.connect(
        host="db",
        database="meetingroom",
        user="admin",
        password="password"
    )


def sanitize_input(text: Optional[str]) -> Optional[str]:
    """
    Sanitize user input to prevent XSS and SQL injection.
    
    Functionality:
        Escapes HTML characters to prevent XSS attacks and escapes single quotes
        to prevent SQL injection. Strips whitespace from the input.
    
    Parameters:
        text (Optional[str]): Input text to sanitize. Can be None.
    
    Returns:
        Optional[str]: Sanitized text with HTML characters escaped and SQL-injection
        patterns removed, or None if input is None or empty.
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
    
    Functionality:
        Fetches all reviews from the database, including associated user and room
        information. Returns reviews ordered by creation date (newest first).
        Includes all review fields: rating, comment, flags, moderation status, etc.
    
    Parameters:
        None
    
    Returns:
        List[Dict]: List of review dictionaries, each containing:
            - review_id (int): Unique review identifier
            - user_id (int): ID of the user who wrote the review
            - room_id (int): ID of the room being reviewed
            - rating (int): Rating from 1 to 5
            - comment (str): Review comment text
            - is_flagged (bool): Whether the review has been flagged
            - flag_reason (str): Reason for flagging (if flagged)
            - is_moderated (bool): Whether the review has been moderated
            - is_hidden (bool): Whether the review is hidden from regular users
            - moderated_by (int): ID of moderator who moderated the review
            - created_at (datetime): Review creation timestamp
            - updated_at (datetime): Last update timestamp
            - username (str): Username of the reviewer
            - user_name (str): Full name of the reviewer
            - room_name (str): Name of the reviewed room
            - room_location (str): Location of the reviewed room
        
        Returns empty list [] if an error occurs or no reviews exist.
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
                r.is_hidden,
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
    
    Functionality:
        Fetches a single review by its unique identifier, including associated
        user and room information. Returns all review details.
    
    Parameters:
        review_id (int): The unique identifier of the review to retrieve.
    
    Returns:
        Dict: Review dictionary containing the same fields as get_all_reviews(),
        or empty dictionary {} if review is not found or an error occurs.
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
                r.is_hidden,
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
    
    Functionality:
        Fetches all reviews for a given room. By default, excludes flagged and
        hidden reviews (for regular users). When include_flagged=True, returns all
        reviews including flagged ones (for moderators/admins). Reviews are ordered
        by creation date (newest first).
    
    Parameters:
        room_id (int): The unique identifier of the room whose reviews to retrieve.
        include_flagged (bool, optional): Whether to include flagged reviews.
            Defaults to False. Set to True for moderator/admin views.
    
    Returns:
        List[Dict]: List of review dictionaries for the specified room, containing
        the same fields as get_all_reviews(). Returns empty list [] if no reviews
        exist for the room, if room doesn't exist, or if an error occurs.
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
                    r.is_hidden,
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
                    r.is_hidden,
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
                AND (r.is_flagged = FALSE OR r.is_flagged IS NULL)
                AND (r.is_hidden = FALSE OR r.is_hidden IS NULL)
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
    
    Functionality:
        Fetches all reviews written by a given user, including associated room
        information. Returns reviews ordered by creation date (newest first).
        Includes all review details.
    
    Parameters:
        user_id (int): The unique identifier of the user whose reviews to retrieve.
    
    Returns:
        List[Dict]: List of review dictionaries written by the specified user,
        containing the same fields as get_all_reviews(). Returns empty list []
        if user has no reviews, if user doesn't exist, or if an error occurs.
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
                r.is_hidden,
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
    
    Functionality:
        Fetches all reviews that have been flagged as inappropriate and require
        moderation. Used by moderators and admins to review and take action on
        flagged content. Reviews are ordered by creation date (newest first).
    
    Parameters:
        None
    
    Returns:
        List[Dict]: List of flagged review dictionaries, each containing the same
        fields as get_all_reviews(). Only includes reviews where is_flagged=True.
        Returns empty list [] if no flagged reviews exist or if an error occurs.
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
                r.is_hidden,
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
    """
    Check if a user exists in the system.
    
    Functionality:
        Verifies whether a user with the given ID exists. First attempts to call
        the users microservice via circuit breaker pattern. If the service is
        unavailable or circuit breaker is open, falls back to a direct database
        query. This provides resilience in a microservices architecture.
    
    Parameters:
        user_id (int): The unique identifier of the user to check.
    
    Returns:
        bool: True if user exists, False otherwise (including if user doesn't
        exist, service is unavailable, or an error occurs).
    """
    # Try to call users service with circuit breaker
    try:
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from shared_utils.circuit_breaker import call_service_with_circuit_breaker, CircuitBreakerOpenError
        
        # Get service URL from environment or use default
        users_service_url = os.getenv('USERS_SERVICE_URL', 'http://users-service:5001')
        
        try:
            response = call_service_with_circuit_breaker(
                service_name='users',
                method='GET',
                url=f'{users_service_url}/admin/users/{user_id}',
                timeout=3
            )
            if response.status_code == 200:
                return True
            return False
        except CircuitBreakerOpenError:
            # Circuit is open, fall back to direct DB query
            print(f"Circuit breaker OPEN for users service, falling back to DB query")
            pass
        except Exception as e:
            # Service call failed, fall back to DB
            print(f"Users service call failed: {e}, falling back to DB query")
            pass
    except ImportError:
        # Circuit breaker not available, use DB directly
        pass
    
    # Fallback: Direct database query
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
    """
    Check if a room exists in the system.
    
    Functionality:
        Verifies whether a room with the given ID exists. First attempts to call
        the rooms microservice via circuit breaker pattern. If the service is
        unavailable or circuit breaker is open, falls back to a direct database
        query. This provides resilience in a microservices architecture.
    
    Parameters:
        room_id (int): The unique identifier of the room to check.
    
    Returns:
        bool: True if room exists, False otherwise (including if room doesn't
        exist, service is unavailable, or an error occurs).
    """
    # Try to call rooms service with circuit breaker
    try:
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from shared_utils.circuit_breaker import call_service_with_circuit_breaker, CircuitBreakerOpenError
        
        # Get service URL from environment or use default
        rooms_service_url = os.getenv('ROOMS_SERVICE_URL', 'http://rooms-service:5000')
        
        try:
            # First get room name from DB (we need it for the API call)
            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute("SELECT room_name FROM Rooms WHERE room_id = %s", (room_id,))
            row = cur.fetchone()
            conn.close()
            
            if not row:
                return False
            
            room_name = row[0]
            
            # Call rooms service to verify
            response = call_service_with_circuit_breaker(
                service_name='rooms',
                method='GET',
                url=f'{rooms_service_url}/api/rooms/{room_name}',
                timeout=3
            )
            if response.status_code == 200:
                return True
            return False
        except CircuitBreakerOpenError:
            # Circuit is open, use DB result we already have
            print(f"Circuit breaker OPEN for rooms service, using DB result")
            return row is not None
        except Exception as e:
            # Service call failed, use DB result
            print(f"Rooms service call failed: {e}, using DB result")
            return row is not None
    except ImportError:
        # Circuit breaker not available, use DB directly
        pass
    except Exception:
        # Any other error, fall through to DB query
        pass
    
    # Fallback: Direct database query
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
    Create a new review for a meeting room.
    
    Functionality:
        Creates a new review in the database after validating all required fields,
        checking that the user and room exist, validating the rating (1-5), and
        sanitizing the comment to prevent XSS and SQL injection attacks.
    
    Parameters:
        review_data (Dict): Dictionary containing review details with keys:
            - user_id (int, required): ID of the user submitting the review
            - room_id (int, required): ID of the room being reviewed
            - rating (int, required): Rating from 1 to 5
            - comment (str, optional): Review comment text
    
    Returns:
        Dict: On success, returns dictionary containing:
            - review_id (int): Unique identifier of the created review
            - user_id (int): ID of the reviewer
            - room_id (int): ID of the reviewed room
            - rating (int): Rating value
            - comment (str): Sanitized comment text
            - is_flagged (bool): Flag status (defaults to False)
            - is_moderated (bool): Moderation status (defaults to False)
            - is_hidden (bool): Hidden status (defaults to False)
            - created_at (datetime): Creation timestamp
            - updated_at (datetime): Update timestamp
            - username (str): Reviewer's username
            - user_name (str): Reviewer's full name
            - room_name (str): Room name
            - room_location (str): Room location
        
        On error, returns dictionary with:
            - error (str): Error message describing what went wrong
            - status (str): "error"
        
        Possible errors:
            - "Missing required fields: user_id, room_id, rating"
            - "Rating must be between 1 and 5"
            - "Invalid rating value"
            - "User does not exist"
            - "Room does not exist"
            - "Failed to create review: <error details>"
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
        
        # Try to encrypt sensitive data if encryption is available
        try:
            import sys
            import os
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            from shared_utils.encryption import get_encryption
            encryption = get_encryption()
            # Encrypt comment if it contains sensitive info (simplified - in production, encrypt all comments)
            # For now, we'll just store sanitized comment
        except ImportError:
            # Encryption not available, continue without it
            pass
        
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO Reviews (user_id, room_id, rating, comment)
            VALUES (%s, %s, %s, %s)
            RETURNING review_id, user_id, room_id, rating, comment, is_flagged, is_moderated, is_hidden, created_at, updated_at
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
                    r.is_hidden,
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
    
    Functionality:
        Updates one or more fields of an existing review. Validates authorization
        (users can only update their own reviews unless they are admin/moderator),
        validates rating if provided, and sanitizes comment text. Updates the
        updated_at timestamp automatically.
    
    Parameters:
        review_id (int): The unique identifier of the review to update.
        review_data (Dict): Dictionary containing fields to update with keys:
            - rating (int, optional): New rating value (1-5)
            - comment (str, optional): New comment text
        At least one field must be provided.
        user_id (Optional[int]): ID of the user making the request (for authorization).
            Required for non-admin/moderator users.
        is_admin (bool): Whether the user is an admin. Defaults to False.
        is_moderator (bool): Whether the user is a moderator. Defaults to False.
    
    Returns:
        Dict: On success, returns dictionary containing the updated review with
        all fields (same structure as get_review_by_id()).
        
        On error, returns dictionary with:
            - error (str): Error message describing what went wrong
            - status (str): "error"
        
        Possible errors:
            - "Review not found"
            - "Unauthorized: You can only update your own reviews"
            - "Rating must be between 1 and 5"
            - "Invalid rating value"
            - "No fields to update"
            - "Failed to update review: <error details>"
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
            RETURNING review_id, user_id, room_id, rating, comment, is_flagged, flag_reason, is_moderated, is_hidden, moderated_by, created_at, updated_at
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
    Delete a review from the database.
    
    Functionality:
        Permanently deletes a review from the database. Validates authorization
        (users can only delete their own reviews unless they are admin/moderator).
        This is a hard delete - the review is completely removed from the database.
    
    Parameters:
        review_id (int): The unique identifier of the review to delete.
        user_id (Optional[int]): ID of the user making the request (for authorization).
            Required for non-admin/moderator users.
        is_admin (bool): Whether the user is an admin. Defaults to False.
        is_moderator (bool): Whether the user is a moderator. Defaults to False.
    
    Returns:
        Dict: On success, returns dictionary with:
            - message (str): "Review deleted successfully"
            - review_id (int): ID of the deleted review
            - status (str): "success"
        
        On error, returns dictionary with:
            - error (str): Error message describing what went wrong
            - status (str): "error"
        
        Possible errors:
            - "Review not found"
            - "Unauthorized: You can only delete your own reviews"
            - "Failed to delete review"
            - "Failed to delete review: <error details>"
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
    Flag a review as inappropriate for moderation.
    
    Functionality:
        Marks a review as flagged, indicating it may contain inappropriate content
        and requires moderation. The flag reason is sanitized to prevent XSS attacks.
        Once flagged, the review is hidden from regular users but visible to moderators
        and admins. A review cannot be flagged if it is already flagged.
    
    Parameters:
        review_id (int): The unique identifier of the review to flag.
        flag_reason (Optional[str]): Reason for flagging the review. Defaults to
            "Flagged by user" if not provided. Will be sanitized before storage.
        user_id (Optional[int]): ID of the user flagging the review. Currently
            stored but not used in the flagging logic.
    
    Returns:
        Dict: On success, returns dictionary with:
            - message (str): "Review flagged successfully"
            - review_id (int): ID of the flagged review
            - status (str): "success"
        
        On error, returns dictionary with:
            - error (str): Error message describing what went wrong
            - status (str): "error"
        
        Possible errors:
            - "Review not found"
            - "Review is already flagged"
            - "Failed to flag review"
            - "Failed to flag review: <error details>"
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
    
    Functionality:
        Removes the flag from a review, indicating it has been reviewed and approved
        by a moderator or admin. Marks the review as moderated and records the
        moderator who performed the action. Once unflagged, the review becomes
        visible to regular users again. A review cannot be unflagged if it is not
        currently flagged.
    
    Parameters:
        review_id (int): The unique identifier of the review to unflag.
        moderator_id (Optional[int]): ID of the moderator or admin performing the
            unflag action. Stored in moderated_by field.
    
    Returns:
        Dict: On success, returns dictionary with:
            - message (str): "Review unflagged successfully"
            - review_id (int): ID of the unflagged review
            - status (str): "success"
        
        On error, returns dictionary with:
            - error (str): Error message describing what went wrong
            - status (str): "error"
        
        Possible errors:
            - "Review not found"
            - "Review is not flagged"
            - "Failed to unflag review"
            - "Failed to unflag review: <error details>"
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
    Remove a review (moderator/admin only - soft delete).
    
    Functionality:
        Soft deletes a review by marking it as moderated, flagged, and setting
        the flag reason to "Removed by moderator". This hides the review from
        regular users while keeping it in the database for audit purposes.
        Records the moderator who performed the removal action.
    
    Parameters:
        review_id (int): The unique identifier of the review to remove.
        moderator_id (Optional[int]): ID of the moderator or admin performing the
            removal action. Stored in moderated_by field.
    
    Returns:
        Dict: On success, returns dictionary with:
            - message (str): "Review removed by moderator"
            - review_id (int): ID of the removed review
            - status (str): "success"
        
        On error, returns dictionary with:
            - error (str): Error message describing what went wrong
            - status (str): "error"
        
        Possible errors:
            - "Review not found"
            - "Failed to remove review"
            - "Failed to remove review: <error details>"
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


def restore_review(review_id: int, admin_id: Optional[int] = None) -> Dict:
    """
    Restore a removed/hidden review (Admin only).
    
    Functionality:
        Restores a previously removed or hidden review by clearing all moderation
        flags (is_moderated, is_hidden, is_flagged) and resetting related fields
        (flag_reason, moderated_by). This makes the review visible to all users
        again and removes all moderation markers.
    
    Parameters:
        review_id (int): The unique identifier of the review to restore.
        admin_id (Optional[int]): ID of the admin performing the restore action.
            Currently not stored but may be used for audit logging.
    
    Returns:
        Dict: On success, returns dictionary with:
            - message (str): "Review restored successfully"
            - review_id (int): ID of the restored review
            - status (str): "success"
        
        On error, returns dictionary with:
            - error (str): Error message describing what went wrong
            - status (str): "error"
        
        Possible errors:
            - "Review not found"
            - "Failed to restore review"
            - "Failed to restore review: <error details>"
    """
    result = {}
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if review exists
        cur.execute("SELECT is_moderated, is_hidden FROM Reviews WHERE review_id = %s", (review_id,))
        existing = cur.fetchone()
        
        if not existing:
            return {"error": "Review not found", "status": "error"}
        
        existing = dict(existing)
        
        # Restore review
        cur.execute("""
            UPDATE Reviews 
            SET is_moderated = FALSE,
                is_hidden = FALSE,
                is_flagged = FALSE,
                flag_reason = NULL,
                moderated_by = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE review_id = %s
            RETURNING review_id, is_moderated, is_hidden, is_flagged
        """, (review_id,))
        
        row = cur.fetchone()
        conn.commit()
        
        if row:
            result = {"message": "Review restored successfully", "review_id": review_id, "status": "success"}
        else:
            result = {"error": "Failed to restore review", "status": "error"}
        
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to restore review: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result


def hide_review(review_id: int, moderator_id: Optional[int] = None) -> Dict:
    """
    Hide a review from regular users (Moderator/Admin only).
    
    Functionality:
        Hides a review from regular users while keeping it visible to moderators
        and admins. Marks the review as moderated and records the moderator who
        performed the action. Hidden reviews are excluded from public listings
        but remain in the database. A review cannot be hidden if it is already hidden.
    
    Parameters:
        review_id (int): The unique identifier of the review to hide.
        moderator_id (Optional[int]): ID of the moderator or admin performing the
            hide action. Stored in moderated_by field.
    
    Returns:
        Dict: On success, returns dictionary with:
            - message (str): "Review hidden successfully"
            - review_id (int): ID of the hidden review
            - status (str): "success"
        
        On error, returns dictionary with:
            - error (str): Error message describing what went wrong
            - status (str): "error"
        
        Possible errors:
            - "Review not found"
            - "Review is already hidden"
            - "Failed to hide review"
            - "Failed to hide review: <error details>"
    """
    result = {}
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if review exists
        cur.execute("SELECT is_hidden FROM Reviews WHERE review_id = %s", (review_id,))
        existing = cur.fetchone()
        
        if not existing:
            return {"error": "Review not found", "status": "error"}
        
        if existing['is_hidden']:
            return {"error": "Review is already hidden", "status": "error"}
        
        # Hide review
        cur.execute("""
            UPDATE Reviews 
            SET is_hidden = TRUE,
                is_moderated = TRUE,
                moderated_by = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE review_id = %s
            RETURNING review_id, is_hidden
        """, (moderator_id, review_id))
        
        row = cur.fetchone()
        conn.commit()
        
        if row:
            result = {"message": "Review hidden successfully", "review_id": review_id, "status": "success"}
        else:
            result = {"error": "Failed to hide review", "status": "error"}
        
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to hide review: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result


def show_review(review_id: int, moderator_id: Optional[int] = None) -> Dict:
    """
    Show a hidden review (Moderator/Admin only).
    
    Functionality:
        Makes a previously hidden review visible to regular users again by clearing
        the is_hidden flag. Records the moderator who performed the action.
        A review cannot be shown if it is not currently hidden.
    
    Parameters:
        review_id (int): The unique identifier of the review to show.
        moderator_id (Optional[int]): ID of the moderator or admin performing the
            show action. Stored in moderated_by field.
    
    Returns:
        Dict: On success, returns dictionary with:
            - message (str): "Review shown successfully"
            - review_id (int): ID of the shown review
            - status (str): "success"
        
        On error, returns dictionary with:
            - error (str): Error message describing what went wrong
            - status (str): "error"
        
        Possible errors:
            - "Review not found"
            - "Review is not hidden"
            - "Failed to show review"
            - "Failed to show review: <error details>"
    """
    result = {}
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if review exists
        cur.execute("SELECT is_hidden FROM Reviews WHERE review_id = %s", (review_id,))
        existing = cur.fetchone()
        
        if not existing:
            return {"error": "Review not found", "status": "error"}
        
        if not existing['is_hidden']:
            return {"error": "Review is not hidden", "status": "error"}
        
        # Show review
        cur.execute("""
            UPDATE Reviews 
            SET is_hidden = FALSE,
                moderated_by = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE review_id = %s
            RETURNING review_id, is_hidden
        """, (moderator_id, review_id))
        
        row = cur.fetchone()
        conn.commit()
        
        if row:
            result = {"message": "Review shown successfully", "review_id": review_id, "status": "success"}
        else:
            result = {"error": "Failed to show review", "status": "error"}
        
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to show review: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result


def get_review_reports() -> Dict:
    """
    Get review moderation reports and statistics for moderators.
    
    Functionality:
        Generates comprehensive statistics and reports about reviews in the system,
        including totals, flagged reviews, hidden reviews, moderated reviews, average
        ratings, rating distribution, and recent flagged reviews. Used by moderators
        and admins to monitor review activity and moderation workload.
    
    Parameters:
        None
    
    Returns:
        Dict: Dictionary containing review statistics with keys:
            - total_reviews (int): Total number of reviews in the system
            - flagged_reviews (int): Number of reviews that are currently flagged
            - hidden_reviews (int): Number of reviews that are currently hidden
            - moderated_reviews (int): Number of reviews that have been moderated
            - average_rating (float): Average rating across all non-hidden reviews
            - rating_distribution (List[Dict]): List of dictionaries with rating
                and count, showing distribution of ratings (1-5)
            - recent_flagged (List[Dict]): List of the 10 most recently flagged
                reviews with their details
        
        On error, returns dictionary with:
            - error (str): Error message describing what went wrong
    """
    reports = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get total reviews
        cur.execute("SELECT COUNT(*) as total FROM Reviews")
        total = cur.fetchone()['total']
        
        # Get flagged reviews count
        cur.execute("SELECT COUNT(*) as flagged FROM Reviews WHERE is_flagged = TRUE")
        flagged = cur.fetchone()['flagged']
        
        # Get hidden reviews count
        cur.execute("SELECT COUNT(*) as hidden FROM Reviews WHERE is_hidden = TRUE")
        hidden = cur.fetchone()['hidden']
        
        # Get moderated reviews count
        cur.execute("SELECT COUNT(*) as moderated FROM Reviews WHERE is_moderated = TRUE")
        moderated = cur.fetchone()['moderated']
        
        # Get average rating
        cur.execute("SELECT AVG(rating) as avg_rating FROM Reviews WHERE is_hidden = FALSE")
        avg_rating = cur.fetchone()['avg_rating']
        
        # Get reviews by rating
        cur.execute("""
            SELECT rating, COUNT(*) as count 
            FROM Reviews 
            WHERE is_hidden = FALSE
            GROUP BY rating 
            ORDER BY rating DESC
        """)
        rating_distribution = [dict(row) for row in cur.fetchall()]
        
        # Get recent flagged reviews (last 10)
        cur.execute("""
            SELECT review_id, user_id, room_id, rating, is_flagged, flag_reason, created_at
            FROM Reviews
            WHERE is_flagged = TRUE
            ORDER BY created_at DESC
            LIMIT 10
        """)
        recent_flagged = [dict(row) for row in cur.fetchall()]
        
        reports = {
            "total_reviews": total,
            "flagged_reviews": flagged,
            "hidden_reviews": hidden,
            "moderated_reviews": moderated,
            "average_rating": float(avg_rating) if avg_rating else 0,
            "rating_distribution": rating_distribution,
            "recent_flagged": recent_flagged
        }
        
    except Exception as e:
        print(f"Error generating reports: {e}")
        reports = {"error": f"Failed to generate reports: {str(e)}"}
    finally:
        if 'conn' in locals():
            conn.close()
    
    return reports

