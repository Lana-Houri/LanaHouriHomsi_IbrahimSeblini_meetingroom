-- Performance Optimization: Database Indexes
-- This migration adds indexes for frequently queried fields to improve query performance

-- Index on room_name for faster room lookups
CREATE INDEX IF NOT EXISTS idx_rooms_name ON Rooms(room_name);

-- Composite index on booking_date and room_id for availability queries
CREATE INDEX IF NOT EXISTS idx_bookings_date_room ON Bookings(booking_date, room_id);

-- Composite index on booking_date, start_time, end_time for availability checks
CREATE INDEX IF NOT EXISTS idx_bookings_datetime ON Bookings(booking_date, start_time, end_time);

-- Index on booking status for filtering by status
CREATE INDEX IF NOT EXISTS idx_bookings_status ON Bookings(status);

-- Index on user username for faster user lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON Users(username);

-- Index on user email for faster email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON Users(email);

-- Index on room status for filtering available rooms
CREATE INDEX IF NOT EXISTS idx_rooms_status ON Rooms(room_status);

-- Composite index for room availability queries (status + location)
CREATE INDEX IF NOT EXISTS idx_rooms_status_location ON Rooms(room_status, room_location);

-- Index on booking created_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_bookings_created_at ON Bookings(created_at);

-- Index on booking updated_at for tracking recent changes
CREATE INDEX IF NOT EXISTS idx_bookings_updated_at ON Bookings(updated_at);

-- Note: Existing indexes from init.sql:
-- - idx_bookings_user ON Bookings(user_id)
-- - idx_bookings_room ON Bookings(room_id)
-- - idx_bookings_date ON Bookings(booking_date)
-- - idx_reviews_room ON Reviews(room_id)
-- - idx_reviews_user ON Reviews(user_id)
-- - idx_reviews_flagged ON Reviews(is_flagged) WHERE is_flagged = TRUE

