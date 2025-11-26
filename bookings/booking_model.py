"""
Booking Model
Handles all database operations for meeting room bookings.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional


def connect_to_db():
    """Establish connection to PostgreSQL database."""
    return psycopg2.connect(
        host="db",
        database="meetingroom",
        user="admin",
        password="password"
    )


def get_all_bookings() -> List[Dict]:
    """
    Retrieve all bookings with user and room details.
    
    Returns:
        List of booking dictionaries with user and room information.
    """
    bookings = []
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                b.booking_id,
                b.user_id,
                b.room_id,
                b.booking_date,
                b.start_time,
                b.end_time,
                b.status,
                b.created_at,
                b.updated_at,
                u.username,
                u.user_name,
                r.room_name,
                r.room_location,
                r.Capacity
            FROM Bookings b
            JOIN Users u ON b.user_id = u.user_id
            JOIN Rooms r ON b.room_id = r.room_id
            ORDER BY b.booking_date DESC, b.start_time DESC
        """)
        rows = cur.fetchall()
        bookings = [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching bookings: {e}")
        bookings = []
    finally:
        if 'conn' in locals():
            conn.close()
    return bookings


def get_booking_by_id(booking_id: int) -> Dict:
    """
    Retrieve a specific booking by ID.
    
    Args:
        booking_id: The ID of the booking to retrieve.
        
    Returns:
        Booking dictionary or empty dict if not found.
    """
    booking = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                b.booking_id,
                b.user_id,
                b.room_id,
                b.booking_date,
                b.start_time,
                b.end_time,
                b.status,
                b.created_at,
                b.updated_at,
                u.username,
                u.user_name,
                r.room_name,
                r.room_location,
                r.Capacity
            FROM Bookings b
            JOIN Users u ON b.user_id = u.user_id
            JOIN Rooms r ON b.room_id = r.room_id
            WHERE b.booking_id = %s
        """, (booking_id,))
        row = cur.fetchone()
        if row:
            booking = dict(row)
    except Exception as e:
        print(f"Error fetching booking: {e}")
        booking = {}
    finally:
        if 'conn' in locals():
            conn.close()
    return booking


def get_user_bookings(user_id: int) -> List[Dict]:
    """
    Retrieve all bookings for a specific user.
    
    Args:
        user_id: The ID of the user.
        
    Returns:
        List of booking dictionaries for the user.
    """
    bookings = []
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                b.booking_id,
                b.user_id,
                b.room_id,
                b.booking_date,
                b.start_time,
                b.end_time,
                b.status,
                b.created_at,
                b.updated_at,
                u.username,
                u.user_name,
                r.room_name,
                r.room_location,
                r.Capacity
            FROM Bookings b
            JOIN Users u ON b.user_id = u.user_id
            JOIN Rooms r ON b.room_id = r.room_id
            WHERE b.user_id = %s
            ORDER BY b.booking_date DESC, b.start_time DESC
        """, (user_id,))
        rows = cur.fetchall()
        bookings = [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching user bookings: {e}")
        bookings = []
    finally:
        if 'conn' in locals():
            conn.close()
    return bookings


def get_room_bookings(room_id: int, booking_date: Optional[str] = None) -> List[Dict]:
    """
    Retrieve bookings for a specific room, optionally filtered by date.
    
    Args:
        room_id: The ID of the room.
        booking_date: Optional date to filter bookings (YYYY-MM-DD format).
        
    Returns:
        List of booking dictionaries for the room.
    """
    bookings = []
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if booking_date:
            cur.execute("""
                SELECT 
                    b.booking_id,
                    b.user_id,
                    b.room_id,
                    b.booking_date,
                    b.start_time,
                    b.end_time,
                    b.status,
                    b.created_at,
                    b.updated_at,
                    u.username,
                    u.user_name,
                    r.room_name,
                    r.room_location,
                    r.Capacity
                FROM Bookings b
                JOIN Users u ON b.user_id = u.user_id
                JOIN Rooms r ON b.room_id = r.room_id
                WHERE b.room_id = %s AND b.booking_date = %s AND b.status != 'Cancelled'
                ORDER BY b.start_time
            """, (room_id, booking_date))
        else:
            cur.execute("""
                SELECT 
                    b.booking_id,
                    b.user_id,
                    b.room_id,
                    b.booking_date,
                    b.start_time,
                    b.end_time,
                    b.status,
                    b.created_at,
                    b.updated_at,
                    u.username,
                    u.user_name,
                    r.room_name,
                    r.room_location,
                    r.Capacity
                FROM Bookings b
                JOIN Users u ON b.user_id = u.user_id
                JOIN Rooms r ON b.room_id = r.room_id
                WHERE b.room_id = %s AND b.status != 'Cancelled'
                ORDER BY b.booking_date, b.start_time
            """, (room_id,))
        
        rows = cur.fetchall()
        bookings = [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching room bookings: {e}")
        bookings = []
    finally:
        if 'conn' in locals():
            conn.close()
    return bookings


def check_room_availability(room_id: int, booking_date: str, start_time: str, end_time: str, exclude_booking_id: Optional[int] = None) -> bool:
    """
    Check if a room is available for a given time slot.
    
    Args:
        room_id: The ID of the room.
        booking_date: Date of the booking (YYYY-MM-DD format).
        start_time: Start time (HH:MM:SS format).
        end_time: End time (HH:MM:SS format).
        exclude_booking_id: Optional booking ID to exclude from check (for updates).
        
    Returns:
        True if room is available, False otherwise.
    """
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        
        # Check for overlapping bookings
        # Two time slots overlap if: existing_start < new_end AND existing_end > new_start
        if exclude_booking_id:
            cur.execute("""
                SELECT COUNT(*) 
                FROM Bookings 
                WHERE room_id = %s 
                AND booking_date = %s 
                AND status != 'Cancelled'
                AND booking_id != %s
                AND start_time < %s AND end_time > %s
            """, (room_id, booking_date, exclude_booking_id, end_time, start_time))
        else:
            cur.execute("""
                SELECT COUNT(*) 
                FROM Bookings 
                WHERE room_id = %s 
                AND booking_date = %s 
                AND status != 'Cancelled'
                AND start_time < %s AND end_time > %s
            """, (room_id, booking_date, end_time, start_time))
        
        count = cur.fetchone()[0]
        return count == 0
    except Exception as e:
        print(f"Error checking room availability: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


def check_room_exists(room_id: int) -> bool:
    """Check if a room exists and is available."""
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT room_id, room_status FROM Rooms WHERE room_id = %s", (room_id,))
        row = cur.fetchone()
        return row is not None and row[1] == 'Available'
    except Exception as e:
        print(f"Error checking room: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


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


def create_booking(booking_data: Dict) -> Dict:
    """
    Create a new booking.
    
    Args:
        booking_data: Dictionary containing booking details (user_id, room_id, booking_date, start_time, end_time).
        
    Returns:
        Created booking dictionary or error message.
    """
    result = {}
    conn = None
    try:
        # Validate required fields
        required_fields = ['user_id', 'room_id', 'booking_date', 'start_time', 'end_time']
        if not all(field in booking_data for field in required_fields):
            return {"error": "Missing required fields", "status": "error"}
        
        user_id = booking_data['user_id']
        room_id = booking_data['room_id']
        booking_date = booking_data['booking_date']
        start_time = booking_data['start_time']
        end_time = booking_data['end_time']
        
        # Validate user and room exist
        if not check_user_exists(user_id):
            return {"error": "User does not exist", "status": "error"}
        
        if not check_room_exists(room_id):
            return {"error": "Room does not exist or is not available", "status": "error"}
        
        # Check availability
        if not check_room_availability(room_id, booking_date, start_time, end_time):
            return {"error": "Room is not available for the requested time slot", "status": "error"}
        
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO Bookings (user_id, room_id, booking_date, start_time, end_time, status)
            VALUES (%s, %s, %s, %s, %s, 'Confirmed')
            RETURNING booking_id, user_id, room_id, booking_date, start_time, end_time, status, created_at, updated_at
        """, (user_id, room_id, booking_date, start_time, end_time))
        
        row = cur.fetchone()
        conn.commit()
        
        if row:
            result = dict(row)
            # Fetch additional details
            cur.execute("""
                SELECT 
                    b.booking_id,
                    b.user_id,
                    b.room_id,
                    b.booking_date,
                    b.start_time,
                    b.end_time,
                    b.status,
                    b.created_at,
                    b.updated_at,
                    u.username,
                    u.user_name,
                    r.room_name,
                    r.room_location,
                    r.Capacity
                FROM Bookings b
                JOIN Users u ON b.user_id = u.user_id
                JOIN Rooms r ON b.room_id = r.room_id
                WHERE b.booking_id = %s
            """, (result['booking_id'],))
            full_row = cur.fetchone()
            if full_row:
                result = dict(full_row)
        
    except psycopg2.IntegrityError as e:
        if conn:
            conn.rollback()
        result = {"error": "Booking conflict: Room is already booked for this time slot", "status": "error"}
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to create booking: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result


def update_booking(booking_id: int, booking_data: Dict, user_id: Optional[int] = None, is_admin: bool = False) -> Dict:
    """
    Update an existing booking.
    
    Args:
        booking_id: The ID of the booking to update.
        booking_data: Dictionary containing fields to update.
        user_id: ID of the user making the request (for authorization).
        is_admin: Whether the user is an admin.
        
    Returns:
        Updated booking dictionary or error message.
    """
    result = {}
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if booking exists and user has permission
        cur.execute("SELECT user_id, room_id, booking_date, start_time, end_time FROM Bookings WHERE booking_id = %s", (booking_id,))
        existing = cur.fetchone()
        
        if not existing:
            return {"error": "Booking not found", "status": "error"}
        
        existing = dict(existing)
        
        # Authorization check
        if user_id and not is_admin and existing['user_id'] != user_id:
            return {"error": "Unauthorized: You can only update your own bookings", "status": "error"}
        
        # Get updated values
        room_id = booking_data.get('room_id', existing['room_id'])
        booking_date = booking_data.get('booking_date', existing['booking_date'])
        start_time = booking_data.get('start_time', existing['start_time'])
        end_time = booking_data.get('end_time', existing['end_time'])
        status = booking_data.get('status', existing.get('status', 'Confirmed'))
        
        # Validate room exists if changed
        if room_id != existing['room_id'] and not check_room_exists(room_id):
            return {"error": "Room does not exist or is not available", "status": "error"}
        
        # Check availability if time/date/room changed
        if (room_id != existing['room_id'] or 
            booking_date != existing['booking_date'] or 
            start_time != existing['start_time'] or 
            end_time != existing['end_time']):
            
            if not check_room_availability(room_id, str(booking_date), str(start_time), str(end_time), booking_id):
                return {"error": "Room is not available for the requested time slot", "status": "error"}
        
        # Update booking
        cur.execute("""
            UPDATE Bookings 
            SET room_id = %s,
                booking_date = %s,
                start_time = %s,
                end_time = %s,
                status = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE booking_id = %s
            RETURNING booking_id, user_id, room_id, booking_date, start_time, end_time, status, created_at, updated_at
        """, (room_id, booking_date, start_time, end_time, status, booking_id))
        
        row = cur.fetchone()
        conn.commit()
        
        if row:
            result = dict(row)
            # Fetch additional details
            cur.execute("""
                SELECT 
                    b.booking_id,
                    b.user_id,
                    b.room_id,
                    b.booking_date,
                    b.start_time,
                    b.end_time,
                    b.status,
                    b.created_at,
                    b.updated_at,
                    u.username,
                    u.user_name,
                    r.room_name,
                    r.room_location,
                    r.Capacity
                FROM Bookings b
                JOIN Users u ON b.user_id = u.user_id
                JOIN Rooms r ON b.room_id = r.room_id
                WHERE b.booking_id = %s
            """, (booking_id,))
            full_row = cur.fetchone()
            if full_row:
                result = dict(full_row)
        
    except psycopg2.IntegrityError as e:
        if conn:
            conn.rollback()
        result = {"error": "Booking conflict: Room is already booked for this time slot", "status": "error"}
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to update booking: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result


def cancel_booking(booking_id: int, user_id: Optional[int] = None, is_admin: bool = False) -> Dict:
    """
    Cancel a booking.
    
    Args:
        booking_id: The ID of the booking to cancel.
        user_id: ID of the user making the request (for authorization).
        is_admin: Whether the user is an admin.
        
    Returns:
        Success message or error.
    """
    result = {}
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if booking exists and user has permission
        cur.execute("SELECT user_id, status FROM Bookings WHERE booking_id = %s", (booking_id,))
        existing = cur.fetchone()
        
        if not existing:
            return {"error": "Booking not found", "status": "error"}
        
        existing = dict(existing)
        
        # Authorization check
        if user_id and not is_admin and existing['user_id'] != user_id:
            return {"error": "Unauthorized: You can only cancel your own bookings", "status": "error"}
        
        if existing['status'] == 'Cancelled':
            return {"error": "Booking is already cancelled", "status": "error"}
        
        # Update status to Cancelled
        cur.execute("""
            UPDATE Bookings 
            SET status = 'Cancelled',
                updated_at = CURRENT_TIMESTAMP
            WHERE booking_id = %s
            RETURNING booking_id, status
        """, (booking_id,))
        
        row = cur.fetchone()
        conn.commit()
        
        if row:
            result = {"message": "Booking cancelled successfully", "booking_id": booking_id, "status": "success"}
        else:
            result = {"error": "Failed to cancel booking", "status": "error"}
        
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to cancel booking: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result


def get_conflicting_bookings(room_id: int, booking_date: str, start_time: str, end_time: str) -> List[Dict]:
    """
    Get all bookings that conflict with a given time slot.
    Used for conflict resolution by admins.
    
    Args:
        room_id: The ID of the room.
        booking_date: Date of the booking (YYYY-MM-DD format).
        start_time: Start time (HH:MM:SS format).
        end_time: End time (HH:MM:SS format).
        
    Returns:
        List of conflicting booking dictionaries.
    """
    conflicts = []
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                b.booking_id,
                b.user_id,
                b.room_id,
                b.booking_date,
                b.start_time,
                b.end_time,
                b.status,
                b.created_at,
                u.username,
                u.user_name,
                r.room_name
            FROM Bookings b
            JOIN Users u ON b.user_id = u.user_id
            JOIN Rooms r ON b.room_id = r.room_id
            WHERE b.room_id = %s 
            AND b.booking_date = %s 
            AND b.status != 'Cancelled'
            AND b.start_time < %s AND b.end_time > %s
            ORDER BY b.start_time
        """, (room_id, booking_date, end_time, start_time))
        
        rows = cur.fetchall()
        conflicts = [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching conflicts: {e}")
        conflicts = []
    finally:
        if 'conn' in locals():
            conn.close()
    return conflicts


def resolve_booking_conflict(booking_id: int, resolution_action: str, admin_id: int) -> Dict:
    """
    Resolve a booking conflict by admin.
    Actions: 'cancel', 'modify', 'override'
    
    Args:
        booking_id: The ID of the booking to resolve.
        resolution_action: Action to take ('cancel', 'modify', 'override').
        admin_id: ID of the admin resolving the conflict.
        
    Returns:
        Success message or error.
    """
    result = {}
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get the booking
        cur.execute("SELECT * FROM Bookings WHERE booking_id = %s", (booking_id,))
        booking = cur.fetchone()
        
        if not booking:
            return {"error": "Booking not found", "status": "error"}
        
        booking = dict(booking)
        
        if resolution_action == 'cancel':
            cur.execute("""
                UPDATE Bookings 
                SET status = 'Cancelled',
                    updated_at = CURRENT_TIMESTAMP
                WHERE booking_id = %s
                RETURNING booking_id, status
            """, (booking_id,))
            result = {"message": "Booking cancelled to resolve conflict", "booking_id": booking_id, "status": "success"}
        
        elif resolution_action == 'modify':
            # This would require additional data for modification
            result = {"message": "Modify action requires additional booking data", "status": "error"}
        
        elif resolution_action == 'override':
            # Keep the booking but mark as admin-overridden
            result = {"message": "Booking override confirmed", "booking_id": booking_id, "status": "success"}
        else:
            return {"error": "Invalid resolution action. Use 'cancel', 'modify', or 'override'", "status": "error"}
        
        conn.commit()
        
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to resolve conflict: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result


def get_stuck_bookings() -> List[Dict]:
    """
    Get bookings that are in stuck states (e.g., status inconsistencies).
    Admin can use this to identify and fix stuck bookings.
    
    Returns:
        List of potentially stuck booking dictionaries.
    """
    stuck = []
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Find bookings that might be stuck:
        # 1. Bookings with status 'Confirmed' but room is marked as 'Booked' for past dates
        # 2. Bookings with end_time in the past but status is still 'Confirmed'
        cur.execute("""
            SELECT 
                b.booking_id,
                b.user_id,
                b.room_id,
                b.booking_date,
                b.start_time,
                b.end_time,
                b.status,
                b.created_at,
                u.username,
                r.room_name,
                r.room_status
            FROM Bookings b
            JOIN Users u ON b.user_id = u.user_id
            JOIN Rooms r ON b.room_id = r.room_id
            WHERE (
                (b.status = 'Confirmed' AND b.booking_date < CURRENT_DATE) OR
                (b.status = 'Confirmed' AND b.booking_date = CURRENT_DATE AND b.end_time < CURRENT_TIME)
            )
            ORDER BY b.booking_date DESC, b.start_time DESC
        """)
        
        rows = cur.fetchall()
        stuck = [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching stuck bookings: {e}")
        stuck = []
    finally:
        if 'conn' in locals():
            conn.close()
    return stuck


def unblock_stuck_booking(booking_id: int, action: str = 'complete') -> Dict:
    """
    Unblock a stuck booking by admin.
    Actions: 'complete' (mark as completed) or 'cancel' (cancel the booking).
    
    Args:
        booking_id: The ID of the stuck booking.
        action: Action to take ('complete' or 'cancel').
        
    Returns:
        Success message or error.
    """
    result = {}
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if booking exists
        cur.execute("SELECT status FROM Bookings WHERE booking_id = %s", (booking_id,))
        existing = cur.fetchone()
        
        if not existing:
            return {"error": "Booking not found", "status": "error"}
        
        if action == 'complete':
            cur.execute("""
                UPDATE Bookings 
                SET status = 'Completed',
                    updated_at = CURRENT_TIMESTAMP
                WHERE booking_id = %s
                RETURNING booking_id, status
            """, (booking_id,))
            result = {"message": "Booking marked as completed", "booking_id": booking_id, "status": "success"}
        
        elif action == 'cancel':
            cur.execute("""
                UPDATE Bookings 
                SET status = 'Cancelled',
                    updated_at = CURRENT_TIMESTAMP
                WHERE booking_id = %s
                RETURNING booking_id, status
            """, (booking_id,))
            result = {"message": "Stuck booking cancelled", "booking_id": booking_id, "status": "success"}
        else:
            return {"error": "Invalid action. Use 'complete' or 'cancel'", "status": "error"}
        
        conn.commit()
        
    except Exception as e:
        if conn:
            conn.rollback()
        result = {"error": f"Failed to unblock booking: {str(e)}", "status": "error"}
    finally:
        if conn:
            conn.close()
    
    return result

