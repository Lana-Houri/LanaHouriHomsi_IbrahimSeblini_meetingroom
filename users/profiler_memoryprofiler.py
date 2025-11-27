import os

if not os.getenv("DB_HOST"):
    os.environ["DB_HOST"] = "localhost"

from memory_profiler import profile
from user_model import (
    get_users,
    get_user_by_username,
    insert_user,
    update_user,
    update_role,
    delete_user,
    reset_password,
    update_own_profile,
    login_user,
    get_booking_history,
)

sample_user = {
    "user_name": "Lana Houri",
    "username": "Lanatest",
    "email": "lana@gmail.com",
    "password": "123456",
    "user_role": "Admin",
    "username_old": "lanah"
}

@profile
def run_memory_tasks():
    get_users()
    get_user_by_username("Lanatest")
    insert_user(sample_user)
    update_user(sample_user)
    update_role("Lanatest", "Facility Manager")
    reset_password("Lanatest", "new123")
    update_own_profile(sample_user)
    login_user("Lanatest", "new123")
    get_booking_history("Lanatest")
    delete_user("Lanatest")

if __name__ == "__main__":
    run_memory_tasks()
