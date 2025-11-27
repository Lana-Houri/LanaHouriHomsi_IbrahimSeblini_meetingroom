"""
Auditing and Logging System
Logs all API requests and responses for auditing purposes.
"""
import logging
import json
from datetime import datetime
from functools import wraps
from flask import request, g
import os


# Configure logging
def setup_audit_logger(log_file: str = "audit.log"):
    """
    Setup audit logger.
    
    Args:
        log_file: Path to audit log file
    """
    logger = logging.getLogger('audit')
    logger.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_path = os.path.join(log_dir, log_file)
    
    # File handler for audit logs
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    # Also log to console in development
    if os.getenv('FLASK_ENV') == 'development':
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


# Initialize audit logger
audit_logger = setup_audit_logger()


def log_request_response(func):
    """
    Decorator to log API requests and responses.
    
    Usage:
        @log_request_response
        @app.route('/api/endpoint')
        def my_endpoint():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get request info
        request_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_id': request.headers.get('X-User-ID'),
            'user_role': request.headers.get('X-User-Role'),
            'query_params': dict(request.args),
        }
        
        # Log request body (sanitize sensitive data)
        if request.is_json:
            body = request.get_json()
            # Remove sensitive fields
            sanitized_body = sanitize_sensitive_data(body)
            request_info['request_body'] = sanitized_body
        
        # Execute function
        try:
            response = func(*args, **kwargs)
            
            # Get response info
            response_info = {
                'status_code': response.status_code if hasattr(response, 'status_code') else 200,
            }
            
            # Log response data if JSON
            if hasattr(response, 'get_json'):
                try:
                    response_data = response.get_json()
                    sanitized_response = sanitize_sensitive_data(response_data)
                    response_info['response_body'] = sanitized_response
                except:
                    pass
            
            # Log successful request
            audit_logger.info(
                f"REQUEST: {json.dumps(request_info)} | "
                f"RESPONSE: {json.dumps(response_info)}"
            )
            
            return response
            
        except Exception as e:
            # Log error
            error_info = {
                'error_type': type(e).__name__,
                'error_message': str(e)
            }
            audit_logger.error(
                f"REQUEST: {json.dumps(request_info)} | "
                f"ERROR: {json.dumps(error_info)}"
            )
            raise
    
    return wrapper


def sanitize_sensitive_data(data):
    """
    Remove sensitive information from data before logging.
    
    Args:
        data: Dictionary or list to sanitize
        
    Returns:
        Sanitized data
    """
    if isinstance(data, dict):
        sensitive_keys = ['password', 'password_hash', 'token', 'api_key', 'secret']
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, (dict, list)):
                sanitized[key] = sanitize_sensitive_data(value)
            else:
                sanitized[key] = value
        return sanitized
    elif isinstance(data, list):
        return [sanitize_sensitive_data(item) for item in data]
    else:
        return data


def log_admin_action(action: str, details: dict = None):
    """
    Log administrative actions.
    
    Args:
        action: Description of the action
        details: Additional details
    """
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'action': action,
        'user_id': request.headers.get('X-User-ID'),
        'user_role': request.headers.get('X-User-Role'),
        'ip_address': request.remote_addr,
    }
    
    if details:
        log_entry['details'] = sanitize_sensitive_data(details)
    
    audit_logger.info(f"ADMIN_ACTION: {json.dumps(log_entry)}")


def log_security_event(event_type: str, details: dict = None):
    """
    Log security-related events.
    
    Args:
        event_type: Type of security event
        details: Additional details
    """
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'ip_address': request.remote_addr,
        'path': request.path,
    }
    
    if details:
        log_entry['details'] = sanitize_sensitive_data(details)
    
    audit_logger.warning(f"SECURITY_EVENT: {json.dumps(log_entry)}")

