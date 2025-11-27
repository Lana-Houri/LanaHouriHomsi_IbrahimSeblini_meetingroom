"""
Simple Circuit Breaker Pattern Implementation
Provides fault tolerance for inter-service communication.
"""
import time
from enum import Enum
from typing import Callable, Any, Optional
import requests


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests immediately
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Simple circuit breaker implementation.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, reject requests immediately
    - HALF_OPEN: Testing if service recovered, allow limited requests
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying again (half-open)
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.total_requests = 0
        self.total_failures = 0
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments for function
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Original exception from function
        """
        # Check if circuit should transition to half-open
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.failure_count = 0
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        # Try to execute function
        self.total_requests += 1
        try:
            result = func(*args, **kwargs)
            # Success - reset failure count
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                print(f"Circuit breaker for service recovered - transitioning to CLOSED")
            self.failure_count = 0
            return result
            
        except self.expected_exception as e:
            self.failure_count += 1
            self.total_failures += 1
            self.last_failure_time = time.time()
            
            # Open circuit if threshold reached
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"Circuit breaker OPENED after {self.failure_count} failures")
            
            raise e
    
    def reset(self):
        """Manually reset circuit breaker to closed state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and request is rejected."""
    pass


# Global circuit breakers for each service
circuit_breakers = {
    'users': CircuitBreaker(failure_threshold=5, recovery_timeout=60),
    'rooms': CircuitBreaker(failure_threshold=5, recovery_timeout=60),
    'bookings': CircuitBreaker(failure_threshold=5, recovery_timeout=60),
    'reviews': CircuitBreaker(failure_threshold=5, recovery_timeout=60),
}


def call_service_with_circuit_breaker(
    service_name: str,
    method: str,
    url: str,
    **kwargs
) -> requests.Response:
    """
    Make HTTP request to another service with circuit breaker protection.
    
    Args:
        service_name: Name of target service ('users', 'rooms', etc.)
        method: HTTP method ('GET', 'POST', etc.)
        url: Full URL to call
        **kwargs: Additional arguments for requests (headers, json, etc.)
        
    Returns:
        Response object
        
    Raises:
        CircuitBreakerOpenError: If circuit is open
        requests.RequestException: If request fails
    """
    import requests.exceptions
    
    breaker = circuit_breakers.get(service_name)
    if not breaker:
        # No circuit breaker for this service, make direct call
        return getattr(requests, method.lower())(url, timeout=5, **kwargs)
    
    def make_request():
        response = getattr(requests, method.lower())(url, timeout=5, **kwargs)
        # Treat non-2xx status codes as failures
        if response.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP {response.status_code}: {response.text}")
        return response
    
    # Update expected exception to catch request exceptions
    breaker.expected_exception = (requests.exceptions.RequestException, requests.exceptions.HTTPError)
    
    return breaker.call(make_request)


def get_circuit_breaker_status(service_name: str = None) -> dict:
    """
    Get status of circuit breaker(s).
    
    Args:
        service_name: Name of service, or None for all services
        
    Returns:
        Dictionary with circuit breaker status
    """
    if service_name:
        breaker = circuit_breakers.get(service_name)
        if not breaker:
            return {"error": f"No circuit breaker for service: {service_name}"}
        
        return {
            "service": service_name,
            "state": breaker.state.value,
            "failure_count": breaker.failure_count,
            "failure_threshold": breaker.failure_threshold,
            "total_requests": breaker.total_requests,
            "total_failures": breaker.total_failures,
            "last_failure_time": breaker.last_failure_time,
            "recovery_timeout": breaker.recovery_timeout,
            "time_until_recovery": max(0, breaker.recovery_timeout - (time.time() - breaker.last_failure_time)) if breaker.last_failure_time else None
        }
    else:
        # Return all circuit breakers
        status = {}
        for name, breaker in circuit_breakers.items():
            status[name] = {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "failure_threshold": breaker.failure_threshold,
                "total_requests": breaker.total_requests,
                "total_failures": breaker.total_failures,
            }
        return status


def reset_circuit_breaker(service_name: str) -> dict:
    """
    Manually reset a circuit breaker.
    
    Args:
        service_name: Name of service to reset
        
    Returns:
        Success message
    """
    breaker = circuit_breakers.get(service_name)
    if not breaker:
        return {"error": f"No circuit breaker for service: {service_name}"}
    
    breaker.reset()
    return {"message": f"Circuit breaker for {service_name} reset successfully", "state": breaker.state.value}

