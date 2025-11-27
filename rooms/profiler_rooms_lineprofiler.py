import os

if not os.getenv("DB_HOST"):
    os.environ["DB_HOST"] = "localhost"

from line_profiler import LineProfiler
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
    "Capacity": 20,
    "room_location": "Main Hall",
    "equipment": "TV",
    "room_status": "Available"
}

sample_update = {
    "room_name": "TestRoom",
    "Capacity": 25,
    "room_location": "West Hall",
    "equipment": "Projector",
    "room_status": "Booked"
}

def main():
    get_rooms()
    get_room_by_name("TestRoom")
    insert_room(sample_insert)
    update_room(sample_update)
    search_rooms(capacity=20, location="Floor", equipment="TV")
    delete_room("TestRoom")

if __name__ == "__main__":
    lp = LineProfiler()

    lp.add_function(get_rooms)
    lp.add_function(get_room_by_name)
    lp.add_function(insert_room)
    lp.add_function(update_room)
    lp.add_function(delete_room)
    lp.add_function(search_rooms)

    lp_wrapper = lp(main)
    lp_wrapper()

    lp.print_stats()
