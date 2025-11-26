# Enhanced Features Implementation Guide

## Overview
This document explains the implementation of:
1. Circuit Breaker Pattern for inter-service communication
2. Rate Limiting and Throttling
3. Auditing and Logging
4. Encryption for sensitive data
5. Secure Configuration Management

## 1. Circuit Breaker Pattern

### Purpose
Prevents cascading failures when one service is down. If a service fails multiple times, the circuit "opens" and rejects requests immediately, giving the service time to recover.

### Implementation
**File:** `shared_utils/circuit_breaker.py`

**Usage Example:**
```python
from shared_utils.circuit_breaker import call_service_with_circuit_breaker

# In booking_model.py when calling users service
try:
    response = call_service_with_circuit_breaker(
        service_name='users',
        method='GET',
        url='http://users-service:5001/admin/users/1',
        headers={'X-User-ID': '1'}
    )
    user_data = response.json()
except CircuitBreakerOpenError:
    # Service is down, use cached data or return error
    return {"error": "Users service temporarily unavailable"}
```

### How It Works
- **CLOSED State**: Normal operation, requests pass through
- **OPEN State**: Too many failures (default: 5), reject all requests
- **HALF_OPEN State**: After timeout (default: 60s), test if service recovered

### Configuration
- `failure_threshold`: Number of failures before opening (default: 5)
- `recovery_timeout`: Seconds to wait before retrying (default: 60)

## 2. Rate Limiting and Throttling

### Purpose
Prevents API abuse by limiting the number of requests per time period.

### Implementation
**File:** `shared_utils/rate_limiter.py`

**Usage in app.py:**
```python
from shared_utils.rate_limiter import init_rate_limiter

app = Flask(__name__)
limiter = init_rate_limiter(app)
```

**Usage in routes:**
```python
from flask_limiter import limiter
from shared_utils.rate_limiter import rate_limit_authenticated

@booking_bp.route('/api/bookings', methods=['GET'])
@limiter.limit("100/hour")  # Simple limit
@log_request_response
def api_get_all_bookings():
    ...
```

### Rate Limits
- **Public endpoints**: 100 requests/hour
- **Authenticated endpoints**: 500 requests/hour
- **Admin endpoints**: 1000 requests/hour
- **Strict endpoints**: 10 requests/minute

### Storage
- Currently uses in-memory storage (for development)
- For production, use Redis: `storage_uri="redis://localhost:6379"`

## 3. Auditing and Logging

### Purpose
Logs all API requests and responses for security auditing and debugging.

### Implementation
**File:** `shared_utils/audit_logger.py`

**Usage:**
```python
from shared_utils.audit_logger import log_request_response, log_admin_action

@booking_bp.route('/api/bookings', methods=['POST'])
@log_request_response  # Automatically logs request/response
def api_create_booking():
    ...

# For admin actions
log_admin_action("User deleted", {"username": "john"})
```

### Log Format
```
2024-12-15 10:30:45 | INFO | REQUEST: {"method": "POST", "path": "/api/bookings", ...} | RESPONSE: {"status_code": 201, ...}
```

### Log Location
- Logs stored in `logs/` directory
- Each service has its own log file (e.g., `bookings_audit.log`)
- Sensitive data (passwords, tokens) automatically redacted

### Features
- Automatic request/response logging
- Sensitive data sanitization
- Admin action logging
- Security event logging

## 4. Encryption

### Purpose
Encrypts sensitive data (passwords, emails, booking details) before storage/transmission.

### Implementation
**File:** `shared_utils/encryption.py`

**Usage:**
```python
from shared_utils.encryption import get_encryption, SENSITIVE_FIELDS

encryption = get_encryption()

# Encrypt sensitive fields in user data
encrypted_data = encryption.encrypt_dict(user_data, ['email', 'password_hash'])

# Decrypt when needed
decrypted_data = encryption.decrypt_dict(encrypted_data, ['email', 'password_hash'])
```

### Encryption Key
- Stored in environment variable: `ENCRYPTION_KEY`
- Or use AWS Secrets Manager (see Configuration Management)
- Key must be 32 bytes, base64-encoded

### Sensitive Fields
Default sensitive fields: `password_hash`, `email`, `phone`, `credit_card`, `ssn`, `api_key`, `secret`

## 5. Secure Configuration Management

### Purpose
Securely manages sensitive configuration (DB passwords, API keys) using environment variables or AWS Secrets Manager.

### Implementation
**File:** `shared_utils/config_manager.py`

**Usage:**
```python
from shared_utils.config_manager import config_manager

# Get database config
db_config = config_manager.get_db_config()
# Returns: {'host': 'db', 'database': 'meetingroom', 'user': 'admin', 'password': 'password'}

# Get encryption key
encryption_key = config_manager.get_encryption_key()

# Get API keys
api_keys = config_manager.get_api_keys()
```

### Configuration Sources (Priority Order)
1. **Environment Variables** (default, always checked first)
2. **AWS Secrets Manager** (if `USE_AWS_SECRETS=true`)

### Environment Variables
```bash
# Database
DB_HOST=db
DB_NAME=meetingroom
DB_USER=admin
DB_PASSWORD=password

# Encryption
ENCRYPTION_KEY=<base64-encoded-32-byte-key>

# AWS Secrets Manager (optional)
USE_AWS_SECRETS=false
AWS_REGION=us-east-1
```

### AWS Secrets Manager Setup
1. Install boto3: `pip install boto3`
2. Set environment variables:
   ```bash
   export USE_AWS_SECRETS=true
   export AWS_REGION=us-east-1
   export AWS_ACCESS_KEY_ID=your-key
   export AWS_SECRET_ACCESS_KEY=your-secret
   ```
3. Create secrets in AWS Secrets Manager
4. Access secrets by name: `config_manager.get_secret('my-secret-name')`

## Integration Steps

### Step 1: Update Requirements
All services now include:
- `Flask-Limiter==3.5.0` (rate limiting)
- `cryptography==42.0.5` (encryption)
- `boto3==1.34.51` (AWS Secrets Manager, optional)

### Step 2: Update app.py
```python
from shared_utils.rate_limiter import init_rate_limiter
from shared_utils.audit_logger import setup_audit_logger

app = Flask(__name__)
limiter = init_rate_limiter(app)
setup_audit_logger('service_name_audit.log')
```

### Step 3: Update Models
```python
from shared_utils.config_manager import config_manager

def connect_to_db():
    db_config = config_manager.get_db_config()
    return psycopg2.connect(**db_config)
```

### Step 4: Update Routes
```python
from shared_utils.audit_logger import log_request_response
from flask_limiter import limiter

@route('/api/endpoint')
@limiter.limit("100/hour")
@log_request_response
def my_endpoint():
    ...
```

## Example: Complete Integration

### bookings/app.py
```python
from flask import Flask, jsonify
from flask_cors import CORS
from booking_routes import booking_bp
from shared_utils.rate_limiter import init_rate_limiter
from shared_utils.audit_logger import setup_audit_logger

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize features
limiter = init_rate_limiter(app)
setup_audit_logger('bookings_audit.log')

app.register_blueprint(booking_bp)
```

### bookings/booking_model.py
```python
from shared_utils.config_manager import config_manager

def connect_to_db():
    db_config = config_manager.get_db_config()
    return psycopg2.connect(**db_config)
```

### bookings/booking_routes.py
```python
from shared_utils.audit_logger import log_request_response
from flask_limiter import limiter

@booking_bp.route('/api/bookings', methods=['GET'])
@limiter.limit("100/hour")
@log_request_response
def api_get_all_bookings():
    ...
```

## Testing

### Test Rate Limiting
```bash
# Make 101 requests quickly
for i in {1..101}; do curl http://localhost:5002/api/bookings; done
# Should get 429 Too Many Requests after limit
```

### Test Circuit Breaker
```python
# Simulate service failure
# After 5 failures, circuit opens
# Requests are rejected immediately
# After 60 seconds, circuit goes to half-open
```

### Test Audit Logging
```bash
# Check logs directory
cat logs/bookings_audit.log
# Should see all API requests/responses
```

### Test Encryption
```python
from shared_utils.encryption import get_encryption

enc = get_encryption()
encrypted = enc.encrypt("sensitive data")
decrypted = enc.decrypt(encrypted)
assert decrypted == "sensitive data"
```

## Production Recommendations

1. **Rate Limiting**: Use Redis for distributed rate limiting
2. **Circuit Breaker**: Monitor circuit states and alert on opens
3. **Audit Logs**: Ship logs to centralized system (ELK, CloudWatch)
4. **Encryption**: Use AWS KMS for key management
5. **Configuration**: Always use AWS Secrets Manager in production
6. **Logs**: Rotate log files regularly
7. **Monitoring**: Set up alerts for security events

## Security Best Practices

1. **Never log passwords**: Already handled by sanitization
2. **Rotate encryption keys**: Regularly rotate keys
3. **Limit access to logs**: Restrict who can view audit logs
4. **Monitor rate limits**: Alert on excessive rate limit hits
5. **Circuit breaker alerts**: Alert when circuits open
6. **Encrypt at rest**: Use encrypted database
7. **Use HTTPS**: Always use TLS in production

