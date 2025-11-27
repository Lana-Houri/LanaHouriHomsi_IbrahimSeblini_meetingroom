"""
Custom Exception Handling Framework
Provides standardized error handling and error messages across all services.
"""
from flask import jsonify, request
from typing import Dict, Any, Optional
import traceback
import logging


class APIException(Exception):
    """
    Base exception class for API errors.
    
    Functionality:
        Base class for all custom API exceptions.
        Provides standardized error response format.
    
    Parameters:
        message (str): Error message
        status_code (int): HTTP status code (default: 500)
        error_code (str, optional): Application-specific error code
        details (dict, optional): Additional error details
    """
    
    def __init__(self, message: str, status_code: int = 500, 
                 error_code: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON response.
        
        Returns:
            dict: Error response dictionary
        """
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details
        }


class ValidationError(APIException):
    """
    Exception for validation errors (400 Bad Request).
    
    Functionality:
        Raised when request validation fails.
    """
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if field:
            error_details["field"] = field
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR", details=error_details)


class AuthenticationError(APIException):
    """
    Exception for authentication errors (401 Unauthorized).
    
    Functionality:
        Raised when authentication fails.
    """
    
    def __init__(self, message: str = "Authentication required", details: Optional[Dict] = None):
        super().__init__(message, status_code=401, error_code="AUTHENTICATION_ERROR", details=details or {})


class AuthorizationError(APIException):
    """
    Exception for authorization errors (403 Forbidden).
    
    Functionality:
        Raised when user lacks required permissions.
    """
    
    def __init__(self, message: str = "Insufficient permissions", 
                 required_role: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if required_role:
            error_details["required_role"] = required_role
        super().__init__(message, status_code=403, error_code="AUTHORIZATION_ERROR", details=error_details)


class NotFoundError(APIException):
    """
    Exception for resource not found errors (404 Not Found).
    
    Functionality:
        Raised when requested resource does not exist.
    """
    
    def __init__(self, resource: str, resource_id: Optional[str] = None, details: Optional[Dict] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        error_details = details or {}
        error_details["resource"] = resource
        if resource_id:
            error_details["resource_id"] = resource_id
        super().__init__(message, status_code=404, error_code="NOT_FOUND", details=error_details)


class ConflictError(APIException):
    """
    Exception for resource conflict errors (409 Conflict).
    
    Functionality:
        Raised when operation conflicts with existing resource state.
    """
    
    def __init__(self, message: str, conflict_type: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if conflict_type:
            error_details["conflict_type"] = conflict_type
        super().__init__(message, status_code=409, error_code="CONFLICT_ERROR", details=error_details)


class DatabaseError(APIException):
    """
    Exception for database operation errors (500 Internal Server Error).
    
    Functionality:
        Raised when database operations fail.
    """
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict] = None):
        super().__init__(message, status_code=500, error_code="DATABASE_ERROR", details=details or {})


class ServiceUnavailableError(APIException):
    """
    Exception for service unavailable errors (503 Service Unavailable).
    
    Functionality:
        Raised when a dependent service is unavailable.
    """
    
    def __init__(self, service: Optional[str] = None, details: Optional[Dict] = None):
        message = "Service unavailable"
        if service:
            message = f"{service} service is unavailable"
        error_details = details or {}
        if service:
            error_details["service"] = service
        super().__init__(message, status_code=503, error_code="SERVICE_UNAVAILABLE", details=error_details)


class RateLimitError(APIException):
    """
    Exception for rate limit errors (429 Too Many Requests).
    
    Functionality:
        Raised when rate limit is exceeded.
    """
    
    def __init__(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if retry_after:
            error_details["retry_after"] = retry_after
        super().__init__(message, status_code=429, error_code="RATE_LIMIT_ERROR", details=error_details)


def register_error_handlers(app):
    """
    Register global error handlers for Flask application.
    
    Functionality:
        Registers error handlers for custom exceptions and general exceptions.
        Provides standardized error responses across all services.
    
    Parameters:
        app: Flask application instance
    
    Returns:
        None
    """
    
    @app.errorhandler(APIException)
    def handle_api_exception(error: APIException):
        """
        Handle custom API exceptions.
        
        Parameters:
            error: APIException instance
        
        Returns:
            JSON response with error details
        """
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle 400 Bad Request errors."""
        return jsonify({
            "error": True,
            "error_code": "BAD_REQUEST",
            "message": "Bad request",
            "status_code": 400,
            "details": {}
        }), 400
    
    @app.errorhandler(401)
    def handle_unauthorized(error):
        """Handle 401 Unauthorized errors."""
        return jsonify({
            "error": True,
            "error_code": "UNAUTHORIZED",
            "message": "Authentication required",
            "status_code": 401,
            "details": {}
        }), 401
    
    @app.errorhandler(403)
    def handle_forbidden(error):
        """Handle 403 Forbidden errors."""
        return jsonify({
            "error": True,
            "error_code": "FORBIDDEN",
            "message": "Insufficient permissions",
            "status_code": 403,
            "details": {}
        }), 403
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found errors."""
        return jsonify({
            "error": True,
            "error_code": "NOT_FOUND",
            "message": "Resource not found",
            "status_code": 404,
            "details": {}
        }), 404
    
    @app.errorhandler(409)
    def handle_conflict(error):
        """Handle 409 Conflict errors."""
        return jsonify({
            "error": True,
            "error_code": "CONFLICT",
            "message": "Resource conflict",
            "status_code": 409,
            "details": {}
        }), 409
    
    @app.errorhandler(429)
    def handle_rate_limit(error):
        """Handle 429 Rate Limit errors."""
        return jsonify({
            "error": True,
            "error_code": "RATE_LIMIT",
            "message": "Rate limit exceeded",
            "status_code": 429,
            "details": {}
        }), 429
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 Internal Server Error."""
        # Log the error for debugging
        logging.error(f"Internal server error: {str(error)}")
        logging.error(traceback.format_exc())
        
        return jsonify({
            "error": True,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred",
            "status_code": 500,
            "details": {}
        }), 500
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """
        Handle all unhandled exceptions.
        
        Parameters:
            error: Exception instance
        
        Returns:
            JSON response with error details
        """
        # Log the error
        logging.error(f"Unhandled exception: {str(error)}")
        logging.error(traceback.format_exc())
        
        # Return generic error response
        return jsonify({
            "error": True,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "status_code": 500,
            "details": {}
        }), 500


def create_error_response(message: str, status_code: int = 500, 
                          error_code: Optional[str] = None,
                          details: Optional[Dict] = None) -> tuple:
    """
    Create a standardized error response.
    
    Functionality:
        Helper function to create standardized error responses.
    
    Parameters:
        message (str): Error message
        status_code (int): HTTP status code
        error_code (str, optional): Error code
        details (dict, optional): Additional details
    
    Returns:
        tuple: (JSON response, status_code)
    """
    response = {
        "error": True,
        "error_code": error_code or "ERROR",
        "message": message,
        "status_code": status_code,
        "details": details or {}
    }
    return jsonify(response), status_code

