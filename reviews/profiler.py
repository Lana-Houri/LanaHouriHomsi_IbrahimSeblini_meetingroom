import cProfile
import pstats
import os

# Set database connection parameters for local profiling (outside Docker)
if not os.getenv("DB_HOST"):
    os.environ["DB_HOST"] = "localhost"
if not os.getenv("DB_NAME"):
    os.environ["DB_NAME"] = "meetingroom"
if not os.getenv("DB_USER"):
    os.environ["DB_USER"] = "admin"
if not os.getenv("DB_PASSWORD"):
    os.environ["DB_PASSWORD"] = "password"

# Set service URLs to localhost for local profiling (outside Docker)
# These will be used if services are running locally, otherwise circuit breaker falls back to DB
if not os.getenv("ROOMS_SERVICE_URL"):
    os.environ["ROOMS_SERVICE_URL"] = "http://localhost:5000"
if not os.getenv("USERS_SERVICE_URL"):
    os.environ["USERS_SERVICE_URL"] = "http://localhost:5001"

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
    get_review_reports,
)

sample_review = {
    "user_id": 1,
    "room_id": 1,
    "rating": 5,
    "comment": "Great room with excellent facilities"
}

def main():
    try:
        print("Starting review model profiling...")
        print("Note: Service call failures (401, etc.) are expected and will fall back to DB queries.")
        print("This is normal for profiling model functions.\n")
        
        get_all_reviews()
        get_review_by_id(1)
        get_reviews_by_room(1)
        get_reviews_by_room(1, include_flagged=True)
        get_user_reviews(1)
        get_flagged_reviews()
        create_review(sample_review)
        update_review(1, {"rating": 4, "comment": "Updated review"}, user_id=1)
        flag_review(1, "Inappropriate content", user_id=1)
        unflag_review(1, moderator_id=1)
        get_review_reports()
        delete_review(1, user_id=1)
        
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
        stats.dump_stats("review_microservice.prof")

        print("Profiling complete -> review_microservice.prof")
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

