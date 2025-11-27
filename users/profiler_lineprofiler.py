import os

if not os.getenv("DB_HOST"):
    os.environ["DB_HOST"] = "localhost"

from line_profiler import LineProfiler
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

def main():
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
    lp = LineProfiler()

    lp.add_function(get_users)
    lp.add_function(get_user_by_username)
    lp.add_function(insert_user)
    lp.add_function(update_user)
    lp.add_function(update_role)
    lp.add_function(delete_user)
    lp.add_function(reset_password)
    lp.add_function(update_own_profile)
    lp.add_function(login_user)
    lp.add_function(get_booking_history)

    lp_wrapper = lp(main)
    lp_wrapper()

    lp.print_stats()
