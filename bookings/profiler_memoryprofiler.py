import os

if not os.getenv("DB_HOST"):
    os.environ["DB_HOST"] = "localhost"

# Set service URLs to localhost for local profiling (outside Docker)
# These will be used if services are running locally, otherwise circuit breaker falls back to DB
if not os.getenv("ROOMS_SERVICE_URL"):
    os.environ["ROOMS_SERVICE_URL"] = "http://localhost:5000"
if not os.getenv("USERS_SERVICE_URL"):
    os.environ["USERS_SERVICE_URL"] = "http://localhost:5001"

from memory_profiler import profile
from booking_model import (
    get_all_bookings,
    get_booking_by_id,
    get_user_bookings,
    get_room_bookings,
    check_room_availability,
    create_booking,
    update_booking,
    cancel_booking,
    get_conflicting_bookings,
    get_stuck_bookings,
)

sample_booking = {
    "user_id": 1,
    "room_id": 1,
    "booking_date": "2024-12-20",
    "start_time": "10:00:00",
    "end_time": "11:00:00",
    "purpose": "Team meeting",
    "status": "confirmed"
}

@profile
def run_memory_tasks():
    get_all_bookings()
    get_booking_by_id(1)
    get_user_bookings(1)
    get_room_bookings(1)
    check_room_availability(1, "2024-12-20", "10:00:00", "11:00:00")
    create_booking(sample_booking)
    update_booking(1, {"purpose": "Updated meeting"}, user_id=1)
    get_conflicting_bookings(1, "2024-12-20", "10:00:00", "11:00:00")
    get_stuck_bookings()
    cancel_booking(1, user_id=1)

if __name__ == "__main__":
    run_memory_tasks()

