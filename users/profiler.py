import cProfile
import pstats
import os

if not os.getenv("DB_HOST"):
    os.environ["DB_HOST"] = "localhost"

from user_model import (
    get_users,
    get_user_by_username,
    insert_user,
    update_user,
    delete_user,
    update_role,
    reset_password,
    update_own_profile,
    login_user,
    get_booking_history,
)

sample_user = {
    "user_name": "Lana Houri",
    "username": "Lanatest",
    "username_old": "lanah",
    "email": "lana@gmail.com",
    "password": "123456",
    "user_role": "Admin"
}

def main():
    try:
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
        stats.dump_stats("user_microservice.prof")

        print("Profiling complete -> user_microservice.prof")
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
