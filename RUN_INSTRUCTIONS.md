# Smart Meeting Room Management System - Run Instructions

## Overview
This project consists of 4 microservices for managing a smart meeting room system:
- **Service 1: Users** (Port 5001) - User management and authentication
- **Service 2: Rooms** (Port 5000) - Room management and availability
- **Service 3: Bookings** (Port 5002) - Meeting room bookings
- **Service 4: Reviews** (Port 5003) - Room and service reviews

## Prerequisites
- Docker and Docker Compose installed
- Postman (for API testing)

## How to Run the System

### Step 1: Start All Services with Docker Compose

From the project root directory, run:

```bash
docker-compose up --build
```

This command will:
1. Build Docker images for all 4 services
2. Start the PostgreSQL database container
3. Initialize the database with the schema (tables for Users, Rooms, Bookings, Reviews)
4. Start all 4 service containers on their respective ports

### Step 2: Verify Services are Running

Check that all containers are running:
```bash
docker-compose ps
```

You should see 5 containers:
- `meetingroom_db` (PostgreSQL)
- `users_service` (Port 5001)
- `rooms_service` (Port 5000)
- `bookings_service` (Port 5002)
- `reviews_service` (Port 5003)

### Step 3: Test the APIs with Postman

#### Service Endpoints:

**Users Service (Port 5001)**
- `GET http://localhost:5001/admin/users` - Get all users
- `POST http://localhost:5001/admin/users/add` - Register new user
- `GET http://localhost:5001/admin/users/<username>` - Get user by username
- `PUT http://localhost:5001/admin/user/update` - Update user
- `DELETE http://localhost:5001/admin/users/delete/<username>` - Delete user

**Rooms Service (Port 5000)**
- `GET http://localhost:5000/api/rooms` - Get all rooms
- `POST http://localhost:5000/rooms/add` - Add new room
- `GET http://localhost:5000/api/rooms/<room_name>` - Get room by name
- `PUT http://localhost:5000/api/rooms/update` - Update room
- `DELETE http://localhost:5000/api/rooms/delete/<room_name>` - Delete room

**Bookings Service (Port 5002)**
- `GET http://localhost:5002/api/bookings` - Get all bookings (Admin/Facility Manager/Auditor)
- `GET http://localhost:5002/api/bookings/<booking_id>` - Get specific booking
- `GET http://localhost:5002/api/bookings/user/<user_id>` - Get user's booking history
- `GET http://localhost:5002/api/bookings/room/<room_id>?date=YYYY-MM-DD` - Get room bookings
- `GET http://localhost:5002/api/bookings/availability?room_id=X&date=YYYY-MM-DD&start_time=HH:MM:SS&end_time=HH:MM:SS` - Check availability
- `POST http://localhost:5002/api/bookings` - Create new booking
- `PUT http://localhost:5002/api/bookings/<booking_id>` - Update booking
- `PUT http://localhost:5002/api/bookings/<booking_id>/cancel` - Cancel booking
- `PUT http://localhost:5002/api/admin/bookings/<booking_id>/force-cancel` - Force cancel (Admin only)

**Reviews Service (Port 5003)**
- `GET http://localhost:5003/api/reviews` - Get all reviews (Admin/Moderator/Auditor)
- `GET http://localhost:5003/api/reviews/<review_id>` - Get specific review
- `GET http://localhost:5003/api/reviews/room/<room_id>` - Get reviews for a room
- `GET http://localhost:5003/api/reviews/user/<user_id>` - Get user's reviews
- `GET http://localhost:5003/api/reviews/flagged` - Get flagged reviews (Moderator/Admin)
- `POST http://localhost:5003/api/reviews` - Submit new review
- `PUT http://localhost:5003/api/reviews/<review_id>` - Update review
- `DELETE http://localhost:5003/api/reviews/<review_id>` - Delete review
- `POST http://localhost:5003/api/reviews/<review_id>/flag` - Flag review as inappropriate
- `PUT http://localhost:5003/api/moderator/reviews/<review_id>/unflag` - Unflag review (Moderator/Admin)
- `DELETE http://localhost:5003/api/moderator/reviews/<review_id>/remove` - Remove review (Moderator/Admin)

### Authentication Headers

For testing with different user roles, include these headers in your Postman requests:

```
X-User-ID: <user_id>
X-User-Role: <role>
```

**Available Roles:**
- `Admin` - Full system access
- `regular user` - Basic user access
- `moderator` - Review moderation access
- `Facility Manager` - Room and booking management
- `Auditor` - Read-only access
- `Service Account` - API service account

### Example API Requests

#### 1. Create a User (Users Service)
```json
POST http://localhost:5001/admin/users/add
Content-Type: application/json

{
  "user_name": "John Doe",
  "username": "johndoe",
  "email": "john@example.com",
  "password_hash": "hashed_password",
  "user_role": "regular user"
}
```

#### 2. Add a Room (Rooms Service)
```json
POST http://localhost:5000/rooms/add
Content-Type: application/json

{
  "room_name": "Conference Room A",
  "Capacity": 20,
  "room_location": "Floor 3",
  "room_status": "Available"
}
```

#### 3. Create a Booking (Bookings Service)
```json
POST http://localhost:5002/api/bookings
Content-Type: application/json
X-User-ID: 1
X-User-Role: regular user

{
  "user_id": 1,
  "room_id": 1,
  "booking_date": "2024-12-15",
  "start_time": "10:00:00",
  "end_time": "11:00:00"
}
```

#### 4. Submit a Review (Reviews Service)
```json
POST http://localhost:5003/api/reviews
Content-Type: application/json
X-User-ID: 1
X-User-Role: regular user

{
  "user_id": 1,
  "room_id": 1,
  "rating": 5,
  "comment": "Great room with excellent equipment!"
}
```

## Stopping the Services

To stop all services:
```bash
docker-compose down
```

To stop and remove volumes (clears database data):
```bash
docker-compose down -v
```

## Database Access

The PostgreSQL database is accessible at:
- Host: `localhost`
- Port: `5432`
- Database: `meetingroom`
- Username: `admin`
- Password: `password`

## Troubleshooting

### Services not starting
1. Check Docker is running: `docker ps`
2. Check logs: `docker-compose logs <service_name>`
3. Rebuild containers: `docker-compose up --build --force-recreate`

### Database connection issues
1. Ensure database container is healthy: `docker-compose ps`
2. Wait for database to initialize (check logs)
3. Verify database credentials match in all services

### Port conflicts
If ports are already in use, modify the port mappings in `docker-compose.yml`

## Project Structure

```
PROJECT/
├── users/           # Service 1: Users
│   ├── app.py
│   ├── user_model.py
│   ├── user_routes.py
│   ├── requirements.txt
│   └── Dockerfile
├── rooms/           # Service 2: Rooms
│   ├── app.py
│   ├── rooms_model.py
│   ├── rooms_routes.py
│   ├── requirements.txt
│   └── Dockerfile
├── bookings/        # Service 3: Bookings (NEW)
│   ├── app.py
│   ├── booking_model.py
│   ├── booking_routes.py
│   ├── requirements.txt
│   └── Dockerfile
├── reviews/         # Service 4: Reviews (NEW)
│   ├── app.py
│   ├── review_model.py
│   ├── review_routes.py
│   ├── requirements.txt
│   └── Dockerfile
├── database/
│   ├── init.sql     # Database schema
│   └── docker-compose.yaml
└── docker-compose.yml  # Main orchestration file
```

## Notes

- Service 1 (Users) and Service 2 (Rooms) were provided and should not be modified except for the port fix in rooms service
- Service 3 (Bookings) and Service 4 (Reviews) are newly implemented
- All services use PostgreSQL database with proper connection pooling
- Input validation and sanitization is implemented in Reviews service to prevent SQL injection and XSS
- Role-based access control (RBAC) is implemented across all endpoints
- The system supports inter-service communication through API calls

