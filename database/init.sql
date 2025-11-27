CREATE TABLE Users(
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(50) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_role VARCHAR(50) CHECK (user_role IN ('Admin','regular user', 'moderator', 'Facility Manager','Auditor', 'Service Account'))
);

CREATE TABLE Rooms(
    room_id SERIAL PRIMARY KEY,
    room_name VARCHAR(100) NOT NULL,
    Capacity INT NOT NULL,
    room_location VARCHAR(100) NOT NULL,
    equipment TEXT,
    room_status VARCHAR(50) CHECK (room_status IN ('Available', 'Booked', 'Out-of-Service')) DEFAULT 'Available'
);

CREATE TABLE Bookings(
    booking_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    room_id INT NOT NULL REFERENCES Rooms(room_id) ON DELETE CASCADE,
    booking_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status VARCHAR(50) CHECK (status IN ('Confirmed', 'Cancelled', 'Completed')) DEFAULT 'Confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_time_slot CHECK (end_time > start_time),
    CONSTRAINT no_overlapping_bookings UNIQUE (room_id, booking_date, start_time, end_time)
);

CREATE TABLE Reviews(
    review_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    room_id INT NOT NULL REFERENCES Rooms(room_id) ON DELETE CASCADE,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    is_flagged BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    is_moderated BOOLEAN DEFAULT FALSE,
    is_hidden BOOLEAN DEFAULT FALSE,
    moderated_by INT REFERENCES Users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Basic indexes
CREATE INDEX idx_bookings_user ON Bookings(user_id);
CREATE INDEX idx_bookings_room ON Bookings(room_id);
CREATE INDEX idx_bookings_date ON Bookings(booking_date);
CREATE INDEX idx_reviews_room ON Reviews(room_id);
CREATE INDEX idx_reviews_user ON Reviews(user_id);
CREATE INDEX idx_reviews_flagged ON Reviews(is_flagged) WHERE is_flagged = TRUE;

-- Performance optimization indexes (for frequently queried fields)
CREATE INDEX idx_rooms_name ON Rooms(room_name);
CREATE INDEX idx_bookings_date_room ON Bookings(booking_date, room_id);
CREATE INDEX idx_bookings_datetime ON Bookings(booking_date, start_time, end_time);
CREATE INDEX idx_bookings_status ON Bookings(status);
CREATE INDEX idx_users_username ON Users(username);
CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_rooms_status ON Rooms(room_status);
CREATE INDEX idx_rooms_status_location ON Rooms(room_status, room_location);
CREATE INDEX idx_bookings_created_at ON Bookings(created_at);
CREATE INDEX idx_bookings_updated_at ON Bookings(updated_at);
