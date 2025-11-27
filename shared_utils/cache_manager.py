"""
Cache Manager
Provides caching functionality for frequently accessed data like room availability and user data.
Supports both in-memory caching and Redis (if available).
"""
import os
import json
import hashlib
from functools import wraps
from typing import Any, Optional, Callable

# Try to import Redis for distributed caching
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

# In-memory cache fallback
_memory_cache = {}
_cache_timestamps = {}


class CacheManager:
    """
    Cache Manager for storing and retrieving cached data.
    
    Functionality:
        Provides caching mechanism for frequently accessed data.
        Supports both Redis (distributed) and in-memory caching.
        Automatically handles cache expiration and key generation.
    
    Parameters:
        redis_host (str, optional): Redis host (default: from env or 'localhost')
        redis_port (int, optional): Redis port (default: from env or 6379)
        redis_db (int, optional): Redis database number (default: 0)
        default_ttl (int, optional): Default time-to-live in seconds (default: 300)
    """
    
    def __init__(self, redis_host: Optional[str] = None, 
                 redis_port: Optional[int] = None,
                 redis_db: int = 0,
                 default_ttl: int = 300):
        self.default_ttl = default_ttl
        self.redis_client = None
        self.use_redis = False
        
        if REDIS_AVAILABLE:
            try:
                host = redis_host or os.getenv('REDIS_HOST', 'localhost')
                port = redis_port or int(os.getenv('REDIS_PORT', 6379))
                self.redis_client = redis.Redis(
                    host=host,
                    port=port,
                    db=redis_db,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                self.use_redis = True
                print("Cache Manager: Using Redis for distributed caching")
            except Exception as e:
                print(f"Cache Manager: Redis not available, using in-memory cache: {e}")
                self.use_redis = False
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate a cache key from prefix and arguments.
        
        Parameters:
            prefix (str): Key prefix
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            str: Generated cache key
        """
        key_parts = [prefix]
        if args:
            key_parts.extend(str(arg) for arg in args)
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend(f"{k}:{v}" for k, v in sorted_kwargs)
        
        key_string = ":".join(key_parts)
        # Create hash for long keys
        if len(key_string) > 200:
            key_string = prefix + ":" + hashlib.md5(key_string.encode()).hexdigest()
        
        return key_string
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from cache.
        
        Parameters:
            key (str): Cache key
        
        Returns:
            Any or None: Cached value if found and not expired, None otherwise
        """
        if self.use_redis and self.redis_client:
            try:
                cached = self.redis_client.get(key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                print(f"Cache get error (Redis): {e}")
                return None
        else:
            # In-memory cache
            if key in _memory_cache:
                if key in _cache_timestamps:
                    import time
                    if time.time() - _cache_timestamps[key] < self.default_ttl:
                        return _memory_cache[key]
                    else:
                        # Expired
                        del _memory_cache[key]
                        del _cache_timestamps[key]
                else:
                    return _memory_cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value in cache.
        
        Parameters:
            key (str): Cache key
            value (Any): Value to cache (must be JSON serializable)
            ttl (int, optional): Time-to-live in seconds (default: self.default_ttl)
        
        Returns:
            bool: True if successful, False otherwise
        """
        ttl = ttl or self.default_ttl
        
        if self.use_redis and self.redis_client:
            try:
                serialized = json.dumps(value)
                self.redis_client.setex(key, ttl, serialized)
                return True
            except Exception as e:
                print(f"Cache set error (Redis): {e}")
                return False
        else:
            # In-memory cache
            try:
                _memory_cache[key] = value
                import time
                _cache_timestamps[key] = time.time()
                return True
            except Exception as e:
                print(f"Cache set error (Memory): {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Parameters:
            key (str): Cache key to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.delete(key)
                return True
            except Exception as e:
                print(f"Cache delete error (Redis): {e}")
                return False
        else:
            # In-memory cache
            try:
                if key in _memory_cache:
                    del _memory_cache[key]
                if key in _cache_timestamps:
                    del _cache_timestamps[key]
                return True
            except Exception:
                return False
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache entries.
        
        Parameters:
            pattern (str, optional): Pattern to match keys (e.g., "room:*")
        
        Returns:
            int: Number of keys deleted
        """
        if self.use_redis and self.redis_client:
            try:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        return self.redis_client.delete(*keys)
                else:
                    return self.redis_client.flushdb()
            except Exception as e:
                print(f"Cache clear error (Redis): {e}")
                return 0
        else:
            # In-memory cache
            try:
                if pattern:
                    keys_to_delete = [k for k in _memory_cache.keys() if k.startswith(pattern.rstrip('*'))]
                    for key in keys_to_delete:
                        if key in _memory_cache:
                            del _memory_cache[key]
                        if key in _cache_timestamps:
                            del _cache_timestamps[key]
                    return len(keys_to_delete)
                else:
                    count = len(_memory_cache)
                    _memory_cache.clear()
                    _cache_timestamps.clear()
                    return count
            except Exception:
                return 0
    
    def cached(self, prefix: str, ttl: Optional[int] = None):
        """
        Decorator to cache function results.
        
        Parameters:
            prefix (str): Cache key prefix
            ttl (int, optional): Time-to-live in seconds
        
        Returns:
            function: Decorated function with caching
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator


# Global cache manager instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """
    Get or create the global cache manager instance.
    
    Returns:
        CacheManager: Global cache manager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def init_cache_manager(redis_host: Optional[str] = None,
                      redis_port: Optional[int] = None,
                      redis_db: int = 0,
                      default_ttl: int = 300) -> CacheManager:
    """
    Initialize the global cache manager.
    
    Parameters:
        redis_host (str, optional): Redis host
        redis_port (int, optional): Redis port
        redis_db (int): Redis database number
        default_ttl (int): Default time-to-live in seconds
    
    Returns:
        CacheManager: Initialized cache manager instance
    """
    global _cache_manager
    _cache_manager = CacheManager(redis_host, redis_port, redis_db, default_ttl)
    return _cache_manager

