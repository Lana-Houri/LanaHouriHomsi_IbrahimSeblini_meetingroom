# Postman Test Guide - Smart Meeting Room System

## Setup Instructions

1. **Start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Verify services are running:**
   - Users Service: http://127.0.0.1:5001/
   - Rooms Service: http://127.0.0.1:5000/
   - Bookings Service: http://127.0.0.1:5002/
   - Reviews Service: http://127.0.0.1:5003/

3. **In Postman, set up environment variables (optional but recommended):**
   - `base_url_users`: http://127.0.0.1:5001
   - `base_url_rooms`: http://127.0.0.1:5000
   - `base_url_bookings`: http://127.0.0.1:5002
   - `base_url_reviews`: http://127.0.0.1:5003

---

## SERVICE 1: USERS SERVICE (Port 5001)

### 1. Get All Users (Admin/Auditor)
```
GET http://127.0.0.1:5001/admin/users
Headers: (none required for this endpoint)
```

### 2. Add New User (Admin)
```
POST http://127.0.0.1:5001/admin/users/add
Content-Type: application/json

Body (raw JSON):
{
  "user_name": "John Doe",
  "username": "johndoe",
  "email": "john@example.com",
  "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqBWVHxkd0",
  "user_role": "regular user"
}
```

### 3. Add Admin User
```
POST http://127.0.0.1:5001/admin/users/add
Content-Type: application/json

Body:
{
  "user_name": "Admin User",
  "username": "admin",
  "email": "admin@example.com",
  "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqBWVHxkd0",
  "user_role": "Admin"
}
```

### 4. Add Facility Manager
```
POST http://127.0.0.1:5001/admin/users/add
Content-Type: application/json

Body:
{
  "user_name": "Facility Manager",
  "username": "facilitymgr",
  "email": "facility@example.com",
  "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqBWVHxkd0",
  "user_role": "Facility Manager"
}
```

### 5. Add Moderator
```
POST http://127.0.0.1:5001/admin/users/add
Content-Type: application/json

Body:
{
  "user_name": "Moderator User",
  "username": "moderator",
  "email": "moderator@example.com",
  "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqBWVHxkd0",
  "user_role": "moderator"
}
```

### 6. Get User by Username
```
GET http://127.0.0.1:5001/admin/users/johndoe
```

### 7. Update User (Admin)
```
PUT http://127.0.0.1:5001/admin/user/update
Content-Type: application/json

Body:
{
  "user_name": "John Updated",
  "username": "johndoe",
  "email": "john.updated@example.com",
  "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqBWVHxkd0",
  "user_role": "regular user"
}
```

### 8. Update User Role (Admin)
```
PUT http://127.0.0.1:5001/admin/update/user_role
Content-Type: application/json

Body:
{
  "username": "johndoe",
  "user_role": "Facility Manager"
}
```

### 9. Reset Password (Admin)
```
PUT http://127.0.0.1:5001/api/admin/reset_password
Content-Type: application/json

Body:
{
  "username": "johndoe",
  "new_password": "newpassword123"
}
```

### 10. Get Regular User Profile
```
GET http://127.0.0.1:5001/regular_user/johndoe
```

### 11. Update Own Profile (Regular User)
```
PUT http://127.0.0.1:5001/regular_user/update
Content-Type: application/json

Body:
{
  "username": "johndoe",
  "user_name": "John Updated Name",
  "email": "john.newemail@example.com",
  "password": "newpassword123"
}
```

### 12. Delete User (Admin)
```
DELETE http://127.0.0.1:5001/admin/users/delete/johndoe
```

### 13. Get All Users (Auditor - Read Only)
```
GET http://127.0.0.1:5001/auditor/users
```

---

## SERVICE 2: ROOMS SERVICE (Port 5000)

### 1. Get All Rooms
```
GET http://127.0.0.1:5000/api/rooms
```

### 2. Add New Room (Admin/Facility Manager)
```
POST http://127.0.0.1:5000/rooms/add
Content-Type: application/json

Body:
{
  "room_name": "Conference Room A",
  "Capacity": 20,
  "room_location": "Floor 3",
  "room_status": "Available"
}
```

### 3. Add Room with Equipment
```
POST http://127.0.0.1:5000/rooms/add
Content-Type: application/json

Body:
{
  "room_name": "Meeting Room B",
  "Capacity": 10,
  "room_location": "Floor 2",
  "equipment": "Projector, Whiteboard, Video Conference",
  "room_status": "Available"
}
```

### 4. Get Room by Name
```
GET http://127.0.0.1:5000/api/rooms/Conference Room A
```

### 5. Update Room (Admin/Facility Manager)
```
PUT http://127.0.0.1:5000/api/rooms/update
Content-Type: application/json

Body:
{
  "room_name": "Conference Room A",
  "Capacity": 25,
  "room_location": "Floor 3",
  "room_status": "Available"
}
```

### 6. Delete Room (Admin/Facility Manager)
```
DELETE http://127.0.0.1:5000/api/rooms/delete/Conference Room A
```

---

## SERVICE 3: BOOKINGS SERVICE (Port 5002)

**Important:** Include authentication headers for most endpoints:
- `X-User-ID: <user_id>`
- `X-User-Role: <role>`

### 1. Get All Bookings (Admin/Facility Manager/Auditor)
```
GET http://127.0.0.1:5002/api/bookings
Headers:
  X-User-ID: 1
  X-User-Role: Admin
```

### 2. Get Specific Booking
```
GET http://127.0.0.1:5002/api/bookings/1
Headers:
  X-User-ID: 1
  X-User-Role: regular user
```

### 3. Get User's Booking History
```
GET http://127.0.0.1:5002/api/bookings/user/1
Headers:
  X-User-ID: 1
  X-User-Role: regular user
```

### 4. Get Room Bookings (All dates)
```
GET http://127.0.0.1:5002/api/bookings/room/1
```

### 5. Get Room Bookings for Specific Date
```
GET http://127.0.0.1:5002/api/bookings/room/1?date=2024-12-15
```

### 6. Check Room Availability
```
GET http://127.0.0.1:5002/api/bookings/availability?room_id=1&date=2024-12-15&start_time=10:00:00&end_time=11:00:00
```

### 7. Create Booking (Regular User)
```
POST http://127.0.0.1:5002/api/bookings
Content-Type: application/json
Headers:
  X-User-ID: 1
  X-User-Role: regular user

Body:
{
  "user_id": 1,
  "room_id": 1,
  "booking_date": "2024-12-15",
  "start_time": "10:00:00",
  "end_time": "11:00:00"
}
```

### 8. Create Another Booking (Different Time Slot)
```
POST http://127.0.0.1:5002/api/bookings
Content-Type: application/json
Headers:
  X-User-ID: 1
  X-User-Role: regular user

Body:
{
  "user_id": 1,
  "room_id": 1,
  "booking_date": "2024-12-15",
  "start_time": "14:00:00",
  "end_time": "15:30:00"
}
```

### 9. Try to Create Overlapping Booking (Should Fail)
```
POST http://127.0.0.1:5002/api/bookings
Content-Type: application/json
Headers:
  X-User-ID: 2
  X-User-Role: regular user

Body:
{
  "user_id": 2,
  "room_id": 1,
  "booking_date": "2024-12-15",
  "start_time": "10:30:00",
  "end_time": "11:30:00"
}
```
**Expected:** Error - Room is not available

### 10. Update Booking (User's Own Booking)
```
PUT http://127.0.0.1:5002/api/bookings/1
Content-Type: application/json
Headers:
  X-User-ID: 1
  X-User-Role: regular user

Body:
{
  "start_time": "10:30:00",
  "end_time": "11:30:00"
}
```

### 11. Cancel Booking
```
PUT http://127.0.0.1:5002/api/bookings/1/cancel
Headers:
  X-User-ID: 1
  X-User-Role: regular user
```

### 12. Force Cancel Booking (Admin Only)
```
PUT http://127.0.0.1:5002/api/admin/bookings/2/force-cancel
Headers:
  X-User-ID: 1
  X-User-Role: Admin
```

### 13. Admin Override Booking
```
PUT http://127.0.0.1:5002/api/admin/bookings/2
Content-Type: application/json
Headers:
  X-User-ID: 1
  X-User-Role: Admin

Body:
{
  "room_id": 2,
  "booking_date": "2024-12-16",
  "start_time": "09:00:00",
  "end_time": "10:00:00",
  "status": "Confirmed"
}
```

---

## SERVICE 4: REVIEWS SERVICE (Port 5003)

**Important:** Include authentication headers for most endpoints:
- `X-User-ID: <user_id>`
- `X-User-Role: <role>`

### 1. Get All Reviews (Admin/Moderator/Auditor/Facility Manager)
```
GET http://127.0.0.1:5003/api/reviews
Headers:
  X-User-ID: 1
  X-User-Role: Admin
```

### 2. Get Specific Review
```
GET http://127.0.0.1:5003/api/reviews/1
```

### 3. Get Reviews for a Room
```
GET http://127.0.0.1:5003/api/reviews/room/1
```

### 4. Get User's Reviews
```
GET http://127.0.0.1:5003/api/reviews/user/1
Headers:
  X-User-ID: 1
  X-User-Role: regular user
```

### 5. Submit Review (Regular User)
```
POST http://127.0.0.1:5003/api/reviews
Content-Type: application/json
Headers:
  X-User-ID: 1
  X-User-Role: regular user

Body:
{
  "user_id": 1,
  "room_id": 1,
  "rating": 5,
  "comment": "Excellent room with great equipment and comfortable seating!"
}
```

### 6. Submit Another Review
```
POST http://127.0.0.1:5003/api/reviews
Content-Type: application/json
Headers:
  X-User-ID: 2
  X-User-Role: regular user

Body:
{
  "user_id": 2,
  "room_id": 1,
  "rating": 4,
  "comment": "Good room, but could use better lighting."
}
```

### 7. Submit Review with Low Rating
```
POST http://127.0.0.1:5003/api/reviews
Content-Type: application/json
Headers:
  X-User-ID: 3
  X-User-Role: regular user

Body:
{
  "user_id": 3,
  "room_id": 1,
  "rating": 2,
  "comment": "Room was too cold and equipment didn't work properly."
}
```

### 8. Try Invalid Rating (Should Fail)
```
POST http://127.0.0.1:5003/api/reviews
Content-Type: application/json
Headers:
  X-User-ID: 1
  X-User-Role: regular user

Body:
{
  "user_id": 1,
  "room_id": 1,
  "rating": 6,
  "comment": "This should fail"
}
```
**Expected:** Error - Rating must be between 1 and 5

### 9. Update Review (User's Own Review)
```
PUT http://127.0.0.1:5003/api/reviews/1
Content-Type: application/json
Headers:
  X-User-ID: 1
  X-User-Role: regular user

Body:
{
  "rating": 4,
  "comment": "Updated comment: Still a great room!"
}
```

### 10. Delete Review (User's Own Review)
```
DELETE http://127.0.0.1:5003/api/reviews/1
Headers:
  X-User-ID: 1
  X-User-Role: regular user
```

### 11. Flag Review as Inappropriate
```
POST http://127.0.0.1:5003/api/reviews/3/flag
Content-Type: application/json
Headers:
  X-User-ID: 2
  X-User-Role: regular user

Body:
{
  "flag_reason": "Inappropriate language"
}
```

### 12. Get Flagged Reviews (Moderator/Admin)
```
GET http://127.0.0.1:5003/api/reviews/flagged
Headers:
  X-User-ID: 1
  X-User-Role: moderator
```

### 13. Unflag Review (Moderator/Admin)
```
PUT http://127.0.0.1:5003/api/moderator/reviews/3/unflag
Headers:
  X-User-ID: 1
  X-User-Role: moderator
```

### 14. Remove Review (Moderator/Admin)
```
DELETE http://127.0.0.1:5003/api/moderator/reviews/3/remove
Headers:
  X-User-ID: 1
  X-User-Role: moderator
```

### 15. Admin Override Review
```
PUT http://127.0.0.1:5003/api/admin/reviews/2
Content-Type: application/json
Headers:
  X-User-ID: 1
  X-User-Role: Admin

Body:
{
  "rating": 3,
  "comment": "Moderated comment by admin"
}
```

### 16. Get All Reviews (Auditor - Read Only)
```
GET http://127.0.0.1:5003/api/auditor/reviews
Headers:
  X-User-ID: 1
  X-User-Role: Auditor
```

---

## TESTING RBAC (Role-Based Access Control)

### Test 1: Regular User Trying to Access Admin Endpoint
```
GET http://127.0.0.1:5002/api/bookings
Headers:
  X-User-ID: 1
  X-User-Role: regular user
```
**Expected:** 403 Forbidden - "Unauthorized: Only admins, facility managers, and auditors can view all bookings"

### Test 2: User Trying to Update Another User's Booking
```
PUT http://127.0.0.1:5002/api/bookings/2
Content-Type: application/json
Headers:
  X-User-ID: 1
  X-User-Role: regular user

Body:
{
  "start_time": "11:00:00",
  "end_time": "12:00:00"
}
```
**Expected:** 403 Forbidden - "Unauthorized: You can only update your own bookings"

### Test 3: User Trying to Delete Another User's Review
```
DELETE http://127.0.0.1:5003/api/reviews/2
Headers:
  X-User-ID: 1
  X-User-Role: regular user
```
**Expected:** 403 Forbidden - "Unauthorized: You can only delete your own reviews"

### Test 4: Regular User Trying to View Flagged Reviews
```
GET http://127.0.0.1:5003/api/reviews/flagged
Headers:
  X-User-ID: 1
  X-User-Role: regular user
```
**Expected:** 403 Forbidden - "Unauthorized: Only admins and moderators can view flagged reviews"

---

## TESTING INPUT VALIDATION

### Test 1: Invalid Rating (Should Fail)
```
POST http://127.0.0.1:5003/api/reviews
Content-Type: application/json
Headers:
  X-User-ID: 1
  X-User-Role: regular user

Body:
{
  "user_id": 1,
  "room_id": 1,
  "rating": 0,
  "comment": "Test"
}
```
**Expected:** Error - Rating must be between 1 and 5

### Test 2: XSS Attempt in Review Comment (Should be Sanitized)
```
POST http://127.0.0.1:5003/api/reviews
Content-Type: application/json
Headers:
  X-User-ID: 1
  X-User-Role: regular user

Body:
{
  "user_id": 1,
  "room_id": 1,
  "rating": 5,
  "comment": "<script>alert('XSS')</script>"
}
```
**Expected:** Comment should be sanitized and stored safely

### Test 3: Invalid Time Slot (End before Start)
```
POST http://127.0.0.1:5002/api/bookings
Content-Type: application/json
Headers:
  X-User-ID: 1
  X-User-Role: regular user

Body:
{
  "user_id": 1,
  "room_id": 1,
  "booking_date": "2024-12-15",
  "start_time": "11:00:00",
  "end_time": "10:00:00"
}
```
**Expected:** Database constraint error - end_time must be > start_time

---

## RECOMMENDED TESTING SEQUENCE

1. **Setup Phase:**
   - Create users with different roles (Admin, regular user, Facility Manager, moderator, Auditor)
   - Create rooms

2. **Bookings Testing:**
   - Create bookings
   - Test overlap prevention
   - Test availability checking
   - Test update/cancel
   - Test RBAC (users can only manage own bookings)

3. **Reviews Testing:**
   - Submit reviews
   - Test rating validation
   - Test input sanitization
   - Test flagging/unflagging
   - Test moderation features
   - Test RBAC (users can only manage own reviews)

4. **Integration Testing:**
   - Create booking → Submit review for that room
   - Test user booking history
   - Test room reviews display

---

## TROUBLESHOOTING

### If you get connection errors:
- Verify services are running: `docker-compose ps`
- Check service logs: `docker-compose logs <service_name>`

### If you get authentication errors:
- Make sure you're including `X-User-ID` and `X-User-Role` headers
- Verify the user_id exists in the database

### If you get database errors:
- Check database is running: `docker-compose ps db`
- Verify database connection: Check service logs

### If you get 404 errors:
- Verify the endpoint URL is correct
- Check the service is running on the correct port

