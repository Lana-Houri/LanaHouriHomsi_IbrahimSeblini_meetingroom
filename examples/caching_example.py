"""
Example: Using Caching in Booking Model
Demonstrates how to integrate caching for room availability checks.
"""
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared_utils.cache_manager import get_cache_manager, init_cache_manager

# Initialize cache manager (typically done in app.py)
cache = init_cache_manager(
    redis_host=os.getenv('REDIS_HOST', 'localhost'),
    redis_port=int(os.getenv('REDIS_PORT', 6379)),
    default_ttl=300  # 5 minutes
)


def check_room_availability_cached(room_id: int, booking_date: str, 
                                   start_time: str, end_time: str) -> bool:
    """
    Check room availability with caching.
    
    Functionality:
        Checks if a room is available, using cache to avoid repeated database queries.
        Cache key includes room_id, date, and time slot.
        Cache expires after 5 minutes (default TTL).
    
    Parameters:
        room_id (int): Room ID
        booking_date (str): Booking date (YYYY-MM-DD)
        start_time (str): Start time (HH:MM:SS)
        end_time (str): End time (HH:MM:SS)
    
    Returns:
        bool: True if available, False otherwise
    """
    cache_key = f"room_availability:{room_id}:{booking_date}:{start_time}:{end_time}"
    
    # Try to get from cache
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        print(f"Cache HIT for room {room_id} on {booking_date}")
        return cached_result
    
    # Cache miss - query database
    print(f"Cache MISS for room {room_id} on {booking_date} - querying database")
    
    # Simulate database query (replace with actual query)
    from booking_model import check_room_availability
    is_available = check_room_availability(room_id, booking_date, start_time, end_time)
    
    # Cache the result
    cache.set(cache_key, is_available, ttl=300)  # Cache for 5 minutes
    
    return is_available


# Using the @cached decorator
@cache.cached(prefix="room_availability", ttl=300)
def check_room_availability_decorated(room_id: int, booking_date: str,
                                    start_time: str, end_time: str) -> bool:
    """
    Check room availability using cache decorator.
    
    Functionality:
        Same as above but using the @cached decorator for automatic caching.
        The decorator automatically generates cache keys and handles cache get/set.
    """
    from booking_model import check_room_availability
    return check_room_availability(room_id, booking_date, start_time, end_time)


def get_user_data_cached(user_id: int) -> dict:
    """
    Get user data with caching.
    
    Functionality:
        Retrieves user data from cache if available, otherwise queries database.
        User data is cached for 10 minutes.
    """
    cache_key = f"user_data:{user_id}"
    
    cached_user = cache.get(cache_key)
    if cached_user:
        return cached_user
    
    # Query database (simulated)
    # from user_model import get_user_by_id
    # user = get_user_by_id(user_id)
    user = {"user_id": user_id, "username": "example", "role": "regular user"}
    
    # Cache for 10 minutes
    cache.set(cache_key, user, ttl=600)
    
    return user


def invalidate_room_cache(room_id: int):
    """
    Invalidate all cache entries for a room.
    
    Functionality:
        Clears all cached data related to a specific room.
        Useful when room data changes (e.g., room status updated).
    """
    pattern = f"room_availability:{room_id}:*"
    deleted_count = cache.clear(pattern)
    print(f"Invalidated {deleted_count} cache entries for room {room_id}")


if __name__ == "__main__":
    # Example usage
    print("=== Caching Example ===")
    
    # Check availability (will query database)
    result1 = check_room_availability_cached(1, "2024-01-15", "10:00:00", "11:00:00")
    print(f"Result 1: {result1}")
    
    # Check again (will use cache)
    result2 = check_room_availability_cached(1, "2024-01-15", "10:00:00", "11:00:00")
    print(f"Result 2: {result2}")
    
    # Get user data
    user = get_user_data_cached(1)
    print(f"User: {user}")
    
    # Invalidate cache
    invalidate_room_cache(1)

