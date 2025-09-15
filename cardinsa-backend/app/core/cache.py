# app/core/cache.py

"""
Cache module for the application.
Provides a simple in-memory cache implementation and an interface for Redis if needed.
"""

import json
import time
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import asyncio
from threading import Lock

from app.core.settings import settings


class InMemoryCache:
    """
    Simple in-memory cache implementation with TTL support.
    For production, consider using Redis instead.
    """
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                
                # Check if expired
                if entry['expires_at'] and datetime.now() > entry['expires_at']:
                    del self._cache[key]
                    return None
                
                return entry['value']
            
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        expires_at = None
        if ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        with self._lock:
            self._cache[key] = {
                'value': value,
                'created_at': datetime.now(),
                'expires_at': expires_at
            }
    
    async def setex(self, key: str, ttl: int, value: str) -> None:
        """Set value with expiration time."""
        await self.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        result = await self.get(key)
        return result is not None
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> None:
        """Remove expired entries."""
        now = datetime.now()
        expired_keys = []
        
        with self._lock:
            for key, entry in self._cache.items():
                if entry['expires_at'] and now > entry['expires_at']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_entries = len(self._cache)
            expired_count = 0
            now = datetime.now()
            
            for entry in self._cache.values():
                if entry['expires_at'] and now > entry['expires_at']:
                    expired_count += 1
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_count,
                'active_entries': total_entries - expired_count,
                'cache_type': 'in_memory'
            }


class RedisCache:
    """
    Redis cache implementation (placeholder for future Redis integration).
    This would require redis-py dependency.
    """
    
    def __init__(self, redis_url: str = None):
        # For now, fall back to in-memory cache
        # In production, you would initialize Redis client here:
        # import redis
        # self.redis = redis.from_url(redis_url)
        self._fallback_cache = InMemoryCache()
        print("Warning: Redis not configured, using in-memory cache fallback")
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis cache."""
        # return await self.redis.get(key)
        return await self._fallback_cache.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set value in Redis cache."""
        # if ttl:
        #     await self.redis.setex(key, ttl, value)
        # else:
        #     await self.redis.set(key, value)
        await self._fallback_cache.set(key, value, ttl)
    
    async def setex(self, key: str, ttl: int, value: str) -> None:
        """Set value with expiration time."""
        # await self.redis.setex(key, ttl, value)
        await self._fallback_cache.setex(key, ttl, value)
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        # result = await self.redis.delete(key)
        # return result > 0
        return await self._fallback_cache.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        # return await self.redis.exists(key)
        return await self._fallback_cache.exists(key)
    
    async def clear(self) -> None:
        """Clear Redis cache."""
        # await self.redis.flushdb()
        await self._fallback_cache.clear()


class NoOpCache:
    """
    No-operation cache that doesn't store anything.
    Useful for development or when caching is disabled.
    """
    
    async def get(self, key: str) -> Optional[str]:
        """Always returns None."""
        return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Does nothing."""
        pass
    
    async def setex(self, key: str, ttl: int, value: str) -> None:
        """Does nothing."""
        pass
    
    async def delete(self, key: str) -> bool:
        """Always returns False."""
        return False
    
    async def exists(self, key: str) -> bool:
        """Always returns False."""
        return False
    
    async def clear(self) -> None:
        """Does nothing."""
        pass


# Global cache instance
_cache_instance = None


def get_cache_client():
    """
    Get the configured cache client.
    
    Returns:
        Cache client instance based on configuration
    """
    global _cache_instance
    
    if _cache_instance is None:
        # Check if caching is enabled in settings
        cache_enabled = getattr(settings, 'CACHE_ENABLED', True)
        
        if not cache_enabled:
            _cache_instance = NoOpCache()
        else:
            # Check for Redis configuration
            redis_url = getattr(settings, 'REDIS_URL', None)
            
            if redis_url:
                _cache_instance = RedisCache(redis_url)
            else:
                _cache_instance = InMemoryCache()
    
    return _cache_instance


def clear_cache():
    """Clear the cache and reset the instance."""
    global _cache_instance
    if _cache_instance:
        asyncio.create_task(_cache_instance.clear())
    _cache_instance = None


# Convenience functions for common cache operations
async def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    """Set a value in cache with JSON serialization."""
    cache = get_cache_client()
    json_value = json.dumps(value, default=str)
    await cache.setex(key, ttl, json_value)


async def cache_get(key: str, default: Any = None) -> Any:
    """Get a value from cache with JSON deserialization."""
    cache = get_cache_client()
    cached_value = await cache.get(key)
    
    if cached_value is None:
        return default
    
    try:
        return json.loads(cached_value)
    except (json.JSONDecodeError, TypeError):
        return default


async def cache_delete(key: str) -> bool:
    """Delete a key from cache."""
    cache = get_cache_client()
    return await cache.delete(key)


# Cache decorators for functions
def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            import hashlib
            
            key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            cache_key = f"{key_prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = await cache_get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await cache_set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


# Export the main interface
__all__ = [
    'get_cache_client',
    'clear_cache',
    'cache_set',
    'cache_get', 
    'cache_delete',
    'cache_result',
    'InMemoryCache',
    'RedisCache',
    'NoOpCache'
]