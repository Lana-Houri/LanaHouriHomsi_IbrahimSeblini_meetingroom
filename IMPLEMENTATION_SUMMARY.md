# Implementation Summary - Services 3 & 4

## What Was Implemented

### Service 3: Bookings Service (Port 5002)

**Location:** `bookings/`

**Files Created:**
- `booking_model.py` - Database operations for bookings
- `booking_routes.py` - API endpoints and route handlers
- `app.py` - Flask application
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `__init__.py` - Package initialization

**Key Features Implemented:**
1. **Viewing all bookings** - `GET /api/bookings` (Admin/Facility Manager/Auditor)
2. **Making a booking** - `POST /api/bookings` with user_id, room_id, date, start_time, end_time
3. **Updating bookings** - `PUT /api/bookings/<id>` - Users can update own, admins can update any
4. **Canceling bookings** - `PUT /api/bookings/<id>/cancel` - Users can cancel own, admins can force cancel
5. **Checking room availability** - `GET /api/bookings/availability` with room_id, date, start_time, end_time
6. **Booking history** - `GET /api/bookings/user/<user_id>` - Users can view own, admins can view any
7. **Room-specific bookings** - `GET /api/bookings/room/<room_id>?date=YYYY-MM-DD`
8. **Admin overrides** - Force cancel and override booking updates

**Database Features:**
- Overlap detection to prevent double-booking
- Time slot validation (end_time > start_time)
- Status tracking (Confirmed, Cancelled, Completed)
- Foreign key relationships with Users and Rooms
- Proper indexes for performance

**RBAC Implementation:**
- **Admin**: Full access, can view all, force cancel, override
- **Facility Manager**: Can view all bookings, create/update/cancel
- **Regular User**: Can create/update/cancel own bookings, view own history
- **Auditor**: Read-only access to all bookings

### Service 4: Reviews Service (Port 5003)

**Location:** `reviews/`

**Files Created:**
- `review_model.py` - Database operations for reviews
- `review_routes.py` - API endpoints and route handlers
- `app.py` - Flask application
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `__init__.py` - Package initialization

**Key Features Implemented:**
1. **Submitting reviews** - `POST /api/reviews` with user_id, room_id, rating (1-5), comment
2. **Updating reviews** - `PUT /api/reviews/<id>` - Users can update own, moderators/admins can update any
3. **Deleting reviews** - `DELETE /api/reviews/<id>` - Users can delete own, moderators/admins can delete any
4. **Retrieving room reviews** - `GET /api/reviews/room/<room_id>` - Filters flagged reviews for regular users
5. **Moderation features**:
   - `POST /api/reviews/<id>/flag` - Flag inappropriate reviews
   - `GET /api/reviews/flagged` - View flagged reviews (Moderator/Admin)
   - `PUT /api/moderator/reviews/<id>/unflag` - Unflag reviews
   - `DELETE /api/moderator/reviews/<id>/remove` - Remove reviews

**Security Features:**
- **Input sanitization** - HTML escaping to prevent XSS attacks
- **SQL injection prevention** - Parameterized queries, input validation
- **Rating validation** - Ensures rating is between 1-5
- **Comment sanitization** - Escapes special characters

**Database Features:**
- Rating constraint (1-5)
- Flagging system for inappropriate content
- Moderation tracking (who moderated, when)
- Foreign key relationships with Users and Rooms
- Indexes for performance (including partial index on flagged reviews)

**RBAC Implementation:**
- **Admin**: Full access, can moderate, override, view all
- **Moderator**: Can flag/unflag, remove reviews, view flagged
- **Facility Manager**: Can view all reviews including flagged
- **Regular User**: Can create/update/delete own reviews, flag others' reviews
- **Auditor**: Read-only access to all reviews

## Database Schema Updates

**File:** `database/init.sql`

**New Tables Added:**

### Bookings Table
```sql
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
```

### Reviews Table
```sql
CREATE TABLE Reviews(
    review_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    room_id INT NOT NULL REFERENCES Rooms(room_id) ON DELETE CASCADE,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    is_flagged BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    is_moderated BOOLEAN DEFAULT FALSE,
    moderated_by INT REFERENCES Users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes Added:**
- `idx_bookings_user` - For user booking history queries
- `idx_bookings_room` - For room availability queries
- `idx_bookings_date` - For date-based filtering
- `idx_reviews_room` - For room review queries
- `idx_reviews_user` - For user review queries
- `idx_reviews_flagged` - Partial index for flagged reviews

**Schema Fixes:**
- Fixed SQL syntax errors in Users and Rooms tables
- Added `equipment` field to Rooms table
- Fixed CHECK constraint syntax
- Added 'Service Account' role to user_role enum

## Docker Configuration

### Main docker-compose.yml
- Orchestrates all 4 services + database
- Health checks for database
- Proper service dependencies
- Network configuration for inter-service communication
- Volume persistence for database

### Individual Dockerfiles
- All services use Python 3.11-slim base image
- Proper dependency installation
- Correct port exposures
- Non-root user considerations

## Authentication & Authorization

**Implementation:**
- Header-based authentication (simplified for project)
- `X-User-ID` header for user identification
- `X-User-Role` header for role-based access control
- In production, this would use JWT tokens or session management

**Role Permissions Summary:**

| Role | Bookings | Reviews |
|------|----------|---------|
| Admin | Full access, override, force cancel | Full access, moderate, override |
| Facility Manager | View all, manage rooms | View all including flagged |
| Moderator | N/A | Flag/unflag, remove reviews |
| Regular User | Own bookings only | Own reviews, flag others |
| Auditor | Read-only | Read-only |
| Service Account | API calls | API calls |

## Key Implementation Details

### Bookings Service
1. **Overlap Detection**: Proper time slot overlap algorithm (start < new_end AND end > new_start)
2. **Availability Checking**: Excludes cancelled bookings, handles updates properly
3. **Cascade Deletes**: Bookings deleted when user or room is deleted
4. **Status Management**: Tracks Confirmed, Cancelled, Completed states

### Reviews Service
1. **Input Sanitization**: HTML escaping, SQL injection prevention
2. **Flagging System**: Users can flag, moderators can unflag/remove
3. **Moderation Tracking**: Records who moderated and when
4. **Rating Validation**: Enforced at database and application level

## Testing Recommendations

### Postman Collection Structure
1. **Setup**: Create users with different roles
2. **Rooms**: Add test rooms
3. **Bookings**: Test create, update, cancel, availability
4. **Reviews**: Test create, update, delete, flag, moderate
5. **RBAC**: Test each role's permissions

### Key Test Cases
- Booking overlap prevention
- Room availability with multiple bookings
- Review rating validation
- Flag/unflag workflow
- Role-based access restrictions
- Input sanitization (try XSS in comments)

## Notes on Existing Services

**Changes Made to Existing Services:**
- Fixed port conflict in `rooms/app.py` (changed from 5001 to 5000)
- Created Dockerfiles for users and rooms services
- Updated database schema to fix SQL syntax errors

**Existing Service Issues (Not Fixed):**
- Users and Rooms services access rows as dictionaries without RealDictCursor
- Some SQL uses `?` placeholders instead of `%s` for PostgreSQL
- These would cause runtime errors but were left as-is per instructions

## How to Run

See `RUN_INSTRUCTIONS.md` for detailed step-by-step instructions.

Quick start:
```bash
docker-compose up --build
```

Then test with Postman using the endpoints documented in RUN_INSTRUCTIONS.md.

