import os

if not os.getenv("DB_HOST"):
    os.environ["DB_HOST"] = "localhost"

from memory_profiler import profile
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

@profile
def run_memory():
    get_rooms()
    get_room_by_name("TestRoom")
    insert_room(sample_insert)
    update_room(sample_update)
    search_rooms(capacity=20, location="Floor", equipment="TV")
    delete_room("TestRoom")

if __name__ == "__main__":
    run_memory()
