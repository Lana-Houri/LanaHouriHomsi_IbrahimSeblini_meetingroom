# Implementation Guide: Performance Optimization & Advanced Development Practices

This guide explains how to use the newly implemented features.

## Table of Contents

1. [Caching Mechanism](#caching-mechanism)
2. [Load Balancing](#load-balancing)
3. [Database Indexing](#database-indexing)
4. [Custom Exception Handling](#custom-exception-handling)
5. [API Versioning](#api-versioning)

---

## 1. Caching Mechanism

### Overview

The caching system provides in-memory and Redis-based caching for frequently accessed data like room availability and user data.

### Location

- **Module**: `shared_utils/cache_manager.py`
- **Example**: `examples/caching_example.py`

### Usage

#### Basic Usage

```python
from shared_utils.cache_manager import get_cache_manager

# Get cache manager instance
cache = get_cache_manager()

# Store data in cache
cache.set("user:123", {"username": "john", "role": "Admin"}, ttl=600)

# Retrieve from cache
user_data = cache.get("user:123")

# Delete from cache
cache.delete("user:123")

# Clear all cache entries matching a pattern
cache.clear("user:*")
```

#### Using the @cached Decorator

```python
from shared_utils.cache_manager import get_cache_manager

cache = get_cache_manager()

@cache.cached(prefix="room_availability", ttl=300)
def check_room_availability(room_id, date, start_time, end_time):
    # This function's results will be automatically cached
    return database_query(...)
```

#### Integration in Booking Model

```python
from shared_utils.cache_manager import get_cache_manager

cache = get_cache_manager()

def check_room_availability(room_id, booking_date, start_time, end_time):
    cache_key = f"room_avail:{room_id}:{booking_date}:{start_time}:{end_time}"
    
    # Try cache first
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Query database
    result = database_query(...)
    
    # Cache result
    cache.set(cache_key, result, ttl=300)
    return result
```

### Configuration

Set environment variables:
- `REDIS_HOST`: Redis server host (default: localhost)
- `REDIS_PORT`: Redis server port (default: 6379)

If Redis is not available, the system automatically falls back to in-memory caching.

### Cache Invalidation

When data changes, invalidate related cache entries:

```python
# Invalidate all room availability cache for a room
cache.clear("room_avail:1:*")

# Invalidate user data
cache.delete("user:123")
```

---

## 2. Load Balancing

### Overview

Load balancing configurations are provided for both HAProxy and Nginx to distribute traffic across multiple service instances.

### Location

- **HAProxy**: `load_balancer/haproxy.cfg`
- **Nginx**: `load_balancer/nginx.conf`
- **Documentation**: `load_balancer/README.md`

### HAProxy Setup

1. Install HAProxy:
```bash
sudo apt-get install haproxy
```

2. Copy configuration:
```bash
sudo cp load_balancer/haproxy.cfg /etc/haproxy/haproxy.cfg
```

3. Start HAProxy:
```bash
sudo systemctl start haproxy
```

4. Access statistics: http://localhost:8404/stats (admin/admin)

### Nginx Setup

1. Install Nginx:
```bash
sudo apt-get install nginx
```

2. Copy configuration:
```bash
sudo cp load_balancer/nginx.conf /etc/nginx/sites-available/meetingroom
sudo ln -s /etc/nginx/sites-available/meetingroom /etc/nginx/sites-enabled/
```

3. Test and start:
```bash
sudo nginx -t
sudo systemctl start nginx
```

### Docker Compose Integration

Add to `docker-compose.yml`:

```yaml
  haproxy:
    image: haproxy:latest
    ports:
      - "80:80"
      - "8404:8404"
    volumes:
      - ./load_balancer/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg
    depends_on:
      - users-service
      - rooms-service
      - bookings-service
    networks:
      - meetingroom-network
```

### Load Balancing Algorithms

- **HAProxy**: roundrobin (default), leastconn, source
- **Nginx**: round-robin (default), least_conn, ip_hash

---

## 3. Database Indexing

### Overview

Performance indexes have been added for frequently queried fields.

### Location

- **Migration Script**: `database/migrations/add_performance_indexes.sql`

### Indexes Created

1. **Room Name Index**: `idx_rooms_name` on `Rooms(room_name)`
2. **Booking Date + Room Index**: `idx_bookings_date_room` on `Bookings(booking_date, room_id)`
3. **Booking DateTime Index**: `idx_bookings_datetime` on `Bookings(booking_date, start_time, end_time)`
4. **Booking Status Index**: `idx_bookings_status` on `Bookings(status)`
5. **User Username Index**: `idx_users_username` on `Users(username)`
6. **User Email Index**: `idx_users_email` on `Users(email)`
7. **Room Status Index**: `idx_rooms_status` on `Rooms(room_status)`
8. **Room Status + Location Index**: `idx_rooms_status_location` on `Rooms(room_status, room_location)`

### Applying Indexes

Run the migration script:

```bash
psql -U admin -d meetingroom -f database/migrations/add_performance_indexes.sql
```

Or via Docker:

```bash
docker exec -i meetingroom_db psql -U admin -d meetingroom < database/migrations/add_performance_indexes.sql
```

### Performance Impact

These indexes significantly improve query performance for:
- Room lookups by name
- Availability checks by date and room
- User lookups by username/email
- Filtering by status

---

## 4. Custom Exception Handling

### Overview

A standardized error handling framework provides consistent error responses across all services.

### Location

- **Module**: `shared_utils/error_handler.py`
- **Example**: `examples/error_handling_example.py`

### Exception Classes

1. **ValidationError** (400): Request validation failures
2. **AuthenticationError** (401): Authentication failures
3. **AuthorizationError** (403): Authorization failures
4. **NotFoundError** (404): Resource not found
5. **ConflictError** (409): Resource conflicts
6. **DatabaseError** (500): Database operation failures
7. **ServiceUnavailableError** (503): Service unavailable
8. **RateLimitError** (429): Rate limit exceeded

### Usage

#### Register Error Handlers

```python
from flask import Flask
from shared_utils.error_handler import register_error_handlers

app = Flask(__name__)
register_error_handlers(app)
```

#### Raise Exceptions

```python
from shared_utils.error_handler import ValidationError, NotFoundError

# Validation error
if not username:
    raise ValidationError("Username is required", field="username")

# Not found error
if not booking:
    raise NotFoundError("Booking", resource_id=booking_id)

# Authorization error
if user_role != "Admin":
    raise AuthorizationError("Admin access required", required_role="Admin")
```

#### Error Response Format

All errors return a standardized format:

```json
{
    "error": true,
    "error_code": "VALIDATION_ERROR",
    "message": "Username is required",
    "status_code": 400,
    "details": {
        "field": "username"
    }
}
```

### Integration Example

```python
from shared_utils.error_handler import (
    register_error_handlers,
    ValidationError,
    NotFoundError
)

app = Flask(__name__)
register_error_handlers(app)

@app.route('/api/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    booking = get_booking_by_id(booking_id)
    
    if not booking:
        raise NotFoundError("Booking", resource_id=str(booking_id))
    
    return jsonify(booking)
```

---

## 5. API Versioning

### Overview

API versioning system ensures backward compatibility by supporting multiple API versions simultaneously.

### Location

- **Module**: `shared_utils/api_versioning.py`
- **Example**: `examples/api_versioning_example.py`

### Usage

#### Initialize Versioning

```python
from shared_utils.api_versioning import init_api_versioning

init_api_versioning(
    default_version="v1",
    supported_versions=["v1", "v2"]
)
```

#### Create Versioned Blueprints

```python
from shared_utils.api_versioning import create_versioned_blueprint

# Create v1 blueprint
v1_bp = create_versioned_blueprint("v1", "v1_api", __name__)

# Create v2 blueprint
v2_bp = create_versioned_blueprint("v2", "v2_api", __name__)

# Register routes
@v1_bp.route('/bookings', methods=['GET'])
def get_bookings_v1():
    return jsonify({"version": "v1", "bookings": [...]})

@v2_bp.route('/bookings', methods=['GET'])
def get_bookings_v2():
    return jsonify({"version": "v2", "data": {"bookings": [...]}})

# Register blueprints
app.register_blueprint(v1_bp)
app.register_blueprint(v2_bp)
```

### Version Detection

The system detects API version from:

1. **URL Path**: `/api/v1/bookings` or `/api/v2/bookings`
2. **Accept Header**: `application/vnd.api.v1+json`
3. **X-API-Version Header**: `v1` or `v2`

### Example Requests

```bash
# Via URL path
curl http://localhost:5000/api/v1/bookings

# Via Accept header
curl -H "Accept: application/vnd.api.v1+json" http://localhost:5000/api/bookings

# Via X-API-Version header
curl -H "X-API-Version: v1" http://localhost:5000/api/bookings
```

### Migration Strategy

1. **Create new version blueprint** alongside existing routes
2. **Implement new features** in the new version
3. **Maintain backward compatibility** in old version
4. **Deprecate old version** after migration period
5. **Remove old version** when no longer needed

---

## Integration Checklist

### For Each Service

- [ ] Initialize cache manager in `app.py`
- [ ] Register error handlers in `app.py`
- [ ] Add caching to frequently accessed functions
- [ ] Replace generic errors with custom exceptions
- [ ] Implement API versioning if needed
- [ ] Update routes to use versioned blueprints

### Example Service Integration

```python
# app.py
from flask import Flask
from shared_utils.cache_manager import init_cache_manager
from shared_utils.error_handler import register_error_handlers
from shared_utils.api_versioning import init_api_versioning

app = Flask(__name__)

# Initialize features
init_cache_manager(default_ttl=300)
register_error_handlers(app)
init_api_versioning(default_version="v1", supported_versions=["v1", "v2"])

# Register blueprints
from booking_routes import booking_bp
app.register_blueprint(booking_bp)
```

---

## Testing

### Test Caching

```python
# Test cache hit/miss
result1 = check_room_availability(1, "2024-01-15", "10:00", "11:00")  # Cache miss
result2 = check_room_availability(1, "2024-01-15", "10:00", "11:00")  # Cache hit
```

### Test Error Handling

```python
# Test validation error
response = client.post('/api/bookings', json={})
assert response.status_code == 400
assert "VALIDATION_ERROR" in response.json["error_code"]
```

### Test API Versioning

```python
# Test v1
response = client.get('/api/v1/bookings')
assert response.json["version"] == "v1"

# Test v2
response = client.get('/api/v2/bookings')
assert response.json["version"] == "v2"
```

---

## Performance Monitoring

### Cache Statistics

Monitor cache hit/miss rates:
- High hit rate = good performance
- Low hit rate = may need to adjust TTL or cache keys

### Database Query Performance

Use `EXPLAIN ANALYZE` to verify indexes are being used:

```sql
EXPLAIN ANALYZE SELECT * FROM Bookings WHERE booking_date = '2024-01-15' AND room_id = 1;
```

### Load Balancer Statistics

- **HAProxy**: http://localhost:8404/stats
- **Nginx**: Monitor access logs and error logs

---

## Troubleshooting

### Cache Not Working

1. Check Redis connection (if using Redis)
2. Verify cache keys are consistent
3. Check TTL values
4. Review cache invalidation logic

### Errors Not Standardized

1. Ensure `register_error_handlers(app)` is called
2. Use custom exception classes
3. Check error response format

### API Versioning Issues

1. Verify version is in `supported_versions`
2. Check version detection logic
3. Ensure blueprints are registered correctly

---

## Next Steps

1. **Integrate caching** into booking and rooms models
2. **Replace error responses** with custom exceptions
3. **Implement API versioning** for new features
4. **Deploy load balancer** in production
5. **Monitor performance** and adjust as needed

---

## Support

For questions or issues, refer to:
- Example files in `examples/` directory
- Source code in `shared_utils/` directory
- Load balancer documentation in `load_balancer/README.md`

