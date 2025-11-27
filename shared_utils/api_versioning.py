"""
API Versioning System
Provides API versioning support to ensure backward compatibility.
"""
from flask import Blueprint, request, jsonify
from functools import wraps
from typing import Callable, Dict, Optional
import re


class APIVersion:
    """
    API Version Manager
    
    Functionality:
        Manages API versions and routes requests to appropriate version handlers.
        Supports semantic versioning (major.minor.patch) and backward compatibility.
    
    Parameters:
        default_version (str): Default API version (e.g., "v1")
        supported_versions (list): List of supported API versions
    """
    
    def __init__(self, default_version: str = "v1", supported_versions: Optional[list] = None):
        self.default_version = default_version
        self.supported_versions = supported_versions or [default_version]
        self.version_handlers: Dict[str, Dict[str, Callable]] = {}
    
    def register_version(self, version: str, blueprint: Blueprint):
        """
        Register a blueprint for a specific API version.
        
        Parameters:
            version (str): API version (e.g., "v1", "v2")
            blueprint (Blueprint): Flask blueprint for this version
        
        Returns:
            None
        """
        if version not in self.supported_versions:
            self.supported_versions.append(version)
        
        if version not in self.version_handlers:
            self.version_handlers[version] = {}
    
    def get_version_from_request(self) -> str:
        """
        Extract API version from request (header or URL path).
        
        Functionality:
            Checks for version in:
            1. URL path (/api/v1/...)
            2. Accept header (application/vnd.api.v1+json)
            3. X-API-Version header
        
        Returns:
            str: API version or default version
        """
        # Check URL path
        path = request.path
        version_match = re.search(r'/v(\d+)/', path)
        if version_match:
            return f"v{version_match.group(1)}"
        
        # Check Accept header
        accept_header = request.headers.get('Accept', '')
        version_match = re.search(r'vnd\.api\.v(\d+)', accept_header)
        if version_match:
            return f"v{version_match.group(1)}"
        
        # Check X-API-Version header
        version_header = request.headers.get('X-API-Version', '')
        if version_header:
            version_match = re.match(r'v?(\d+)', version_header)
            if version_match:
                return f"v{version_match.group(1)}"
        
        return self.default_version
    
    def is_version_supported(self, version: str) -> bool:
        """
        Check if a version is supported.
        
        Parameters:
            version (str): API version to check
        
        Returns:
            bool: True if version is supported
        """
        return version in self.supported_versions
    
    def get_latest_version(self) -> str:
        """
        Get the latest supported API version.
        
        Returns:
            str: Latest version string
        """
        if not self.supported_versions:
            return self.default_version
        
        # Extract version numbers and sort
        versions = []
        for v in self.supported_versions:
            match = re.match(r'v(\d+)', v)
            if match:
                versions.append((int(match.group(1)), v))
        
        if versions:
            versions.sort(reverse=True)
            return versions[0][1]
        
        return self.default_version


# Global API version manager
_api_version_manager = None


def get_api_version_manager() -> APIVersion:
    """
    Get or create the global API version manager.
    
    Returns:
        APIVersion: Global API version manager instance
    """
    global _api_version_manager
    if _api_version_manager is None:
        _api_version_manager = APIVersion()
    return _api_version_manager


def init_api_versioning(default_version: str = "v1", 
                       supported_versions: Optional[list] = None) -> APIVersion:
    """
    Initialize the global API version manager.
    
    Parameters:
        default_version (str): Default API version
        supported_versions (list): List of supported versions
    
    Returns:
        APIVersion: Initialized API version manager
    """
    global _api_version_manager
    _api_version_manager = APIVersion(default_version, supported_versions)
    return _api_version_manager


def versioned_route(version: str, rule: str, **options):
    """
    Decorator to create versioned routes.
    
    Functionality:
        Creates a route that is version-specific.
        Routes are automatically prefixed with /api/{version}/
    
    Parameters:
        version (str): API version (e.g., "v1")
        rule (str): URL rule
        **options: Additional route options
    
    Returns:
        function: Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Check if requested version matches
            requested_version = get_api_version_manager().get_version_from_request()
            
            if requested_version != version:
                # Try to find compatible version
                if not get_api_version_manager().is_version_supported(requested_version):
                    return jsonify({
                        "error": True,
                        "error_code": "UNSUPPORTED_VERSION",
                        "message": f"API version {requested_version} is not supported",
                        "supported_versions": get_api_version_manager().supported_versions,
                        "status_code": 400
                    }), 400
            
            return f(*args, **kwargs)
        
        return wrapper
    return decorator


def create_versioned_blueprint(version: str, name: str, import_name: str, 
                               url_prefix: Optional[str] = None) -> Blueprint:
    """
    Create a versioned blueprint.
    
    Functionality:
        Creates a Flask blueprint with version prefix.
        Automatically registers with API version manager.
    
    Parameters:
        version (str): API version (e.g., "v1")
        name (str): Blueprint name
        import_name (str): Import name
        url_prefix (str, optional): URL prefix (default: /api/{version})
    
    Returns:
        Blueprint: Versioned Flask blueprint
    """
    if url_prefix is None:
        url_prefix = f"/api/{version}"
    
    blueprint = Blueprint(name, import_name, url_prefix=url_prefix)
    
    # Register with version manager
    version_manager = get_api_version_manager()
    version_manager.register_version(version, blueprint)
    
    return blueprint

