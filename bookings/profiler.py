import cProfile
import pstats
import os

if not os.getenv("DB_HOST"):
    os.environ["DB_HOST"] = "localhost"

# Set service URLs to localhost for local profiling (outside Docker)
# These will be used if services are running locally, otherwise circuit breaker falls back to DB
if not os.getenv("ROOMS_SERVICE_URL"):
    os.environ["ROOMS_SERVICE_URL"] = "http://localhost:5000"
if not os.getenv("USERS_SERVICE_URL"):
    os.environ["USERS_SERVICE_URL"] = "http://localhost:5001"

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

def main():
    try:
        print("Starting booking model profiling...")
        print("Note: Service call failures (401, etc.) are expected and will fall back to DB queries.")
        print("This is normal for profiling model functions.\n")
        
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
        
        print("\nProfiling operations completed successfully!")
    except Exception as e:
        print(f"Error during profiling: {e}")
        print("Note: Make sure the database is running and accessible.")


if __name__ == "__main__":
    try:
        profiler = cProfile.Profile()
        profiler.enable()

        main()

        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats("cumtime")
        stats.dump_stats("booking_microservice.prof")

        print("Profiling complete -> booking_microservice.prof")
    except ValueError as e:
        error_msg = str(e)
        if ("profiling tool is already active" in error_msg.lower() or 
            "profiler is already active" in error_msg.lower() or
            "another profiler" in error_msg.lower()):
            print("Note: Profiling is already active (likely run with -m cProfile)")
            print("Running main() without creating additional profiler...")
            main()
            print("Profiling complete -> Check the output file specified with -m cProfile")
        else:
            raise

