"""
Rate Limiting Utilities
Simple rate limiting using Flask-Limiter.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask


def init_rate_limiter(app: Flask) -> Limiter:
    """
    Initialize rate limiter for Flask app.
    
    Args:
        app: Flask application instance
        
    Returns:
        Limiter instance
    """
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"  # In-memory storage (use Redis in production)
    )
    return limiter


# Rate limit decorators for different endpoint types
def rate_limit_public():
    """Rate limit for public endpoints: 100 requests per hour."""
    return {"per_method": True, "limit_value": "100/hour"}


def rate_limit_authenticated():
    """Rate limit for authenticated endpoints: 500 requests per hour."""
    return {"per_method": True, "limit_value": "500/hour"}


def rate_limit_admin():
    """Rate limit for admin endpoints: 1000 requests per hour."""
    return {"per_method": True, "limit_value": "1000/hour"}


def rate_limit_strict():
    """Strict rate limit: 10 requests per minute."""
    return {"per_method": True, "limit_value": "10/minute"}

