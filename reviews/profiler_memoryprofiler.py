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

from memory_profiler import profile
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

@profile
def run_memory_tasks():
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

if __name__ == "__main__":
    run_memory_tasks()

