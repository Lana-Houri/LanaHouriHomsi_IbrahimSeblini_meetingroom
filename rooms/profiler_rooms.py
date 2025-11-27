import cProfile
import pstats
import os

if not os.getenv("DB_HOST"):
    os.environ["DB_HOST"] = "localhost"

from rooms_model import (
    get_rooms,
    get_room_by_name,
    insert_room,
    update_room,
    delete_room,
    search_rooms,
)

sample_insert = {
    "room_name": "TestRoom",
    "Capacity": 25,
    "room_location": "CCC",
    "equipment": "Projector",
    "room_status": "Available"
}

sample_update = {
    "room_name": "TestRoom",
    "Capacity": 30,
    "room_location": "Oxy",
    "equipment": "TV",
    "room_status": "Booked"
}

def run_all():
    try:
        get_rooms()
        get_room_by_name("TestRoom")
        insert_room(sample_insert)
        update_room(sample_update)
        search_rooms(capacity=20, location="Floor", equipment="TV")
        delete_room("TestRoom")
    except Exception as e:
        print(f"Error during profiling: {e}")
        print("Note: Make sure the database is running and accessible.")

if __name__ == "__main__":
    try:
        profiler = cProfile.Profile()
        profiler.enable()

        run_all()

        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats("cumtime")
        stats.dump_stats("rooms_microservice.prof")

        print("Profiling complete -> rooms_microservice.prof")
    except ValueError as e:
        error_msg = str(e)
        if ("profiling tool is already active" in error_msg.lower() or 
            "profiler is already active" in error_msg.lower() or
            "another profiler" in error_msg.lower()):
            print("Note: Profiling is already active (likely run with -m cProfile)")
            print("Running run_all() without creating additional profiler...")
            run_all()
            print("Profiling complete -> Check the output file specified with -m cProfile")
        else:
            raise
