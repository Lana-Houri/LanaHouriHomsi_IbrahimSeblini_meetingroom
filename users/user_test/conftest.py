import pytest
from unittest.mock import patch
import sys
import os

# Add parent directory to path
SYS_PATH_ROOT = os.path.dirname(os.path.dirname(__file__))
if SYS_PATH_ROOT not in sys.path:
    sys.path.insert(0, SYS_PATH_ROOT)

# Patch decorators before importing routes
@pytest.fixture(autouse=True)
def mock_auth_decorators():
    """Automatically mock authentication decorators for all tests"""
    def pass_through(f):
        return f
    
    def mock_role_required(*roles):
        def decorator(f):
            return f
        return decorator
    
    with patch("user_routes.token_required", side_effect=lambda f: f), \
         patch("user_routes.role_required", side_effect=mock_role_required):
        yield

