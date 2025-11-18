CREATE TABLE Users(
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(50) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_role VARCHAR(50) CHECK (role IN ('Admin','regular user', 'moderator', 'Facility Manager','Auditor')),
);

CREATE TABLE Rooms(
    room_id SERIAL PRIMARY KEY,
    room_name VARCHAR(100) NOT NULL,
    Capacity INT NOT NULL,
    room_location VARCHAR(100) NOT NULL,
    room_status VARCHAR(50) CHECK (role IN ('Available', 'Booked')) DEFAULT 'Available',
)
