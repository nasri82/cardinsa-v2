# app/core/rate_limiting.py

"""
Rate Limiting Module for API Endpoints

Provides rate limiting functionality for underwriting and other API routes
to prevent abuse and ensure system stability.
"""

import time
import asyncio
from typing import Dict, Optional, Callable, Any
from functools import wraps
from collections import defaultdict, deque
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
import redis
from app.core.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# In-memory storage for rate limiting (fallback if Redis unavailable)
_rate_limit_storage = defaultdict(deque)
_rate_limit_locks = defaultdict(asyncio.Lock)

class RateLimiter:
    """Rate limiter with multiple algorithms support"""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        algorithm: str = "sliding_window",
        storage_backend: str = "memory"
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.algorithm = algorithm
        self.storage_backend = storage_backend
        
        # Initialize Redis client if available
        self.redis_client = None
        if storage_backend == "redis":
            try:
                self.redis_client = redis.Redis(
                    host=getattr(settings, 'REDIS_HOST', 'localhost'),
                    port=getattr(settings, 'REDIS_PORT', 6379),
                    db=getattr(settings, 'REDIS_DB', 0),
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Rate limiter using Redis backend")
            except Exception as e:
                logger.warning(f"Redis unavailable, falling back to memory: {e}")
                self.storage_backend = "memory"
    
    def limit(self, limit_string: str):
        """
        Decorator method compatible with Flask-Limiter style syntax
        
        Args:
            limit_string: Limit in format "10/minute", "100/hour", etc.
        
        Usage:
            @rate_limiter.limit("10/minute")
            async def my_endpoint():
                pass
        """
        # Parse limit string like "10/minute"
        parts = limit_string.split('/')
        if len(parts) != 2:
            raise ValueError(f"Invalid limit format: {limit_string}. Use format like '10/minute'")
        
        count = int(parts[0])
        period = parts[1].lower()
        
        # Convert to requests per minute/hour
        if period in ['minute', 'min', 'm']:
            requests_per_minute = count
            requests_per_hour = count * 60
        elif period in ['hour', 'hr', 'h']:
            requests_per_minute = count // 60 if count > 60 else count
            requests_per_hour = count
        elif period in ['second', 'sec', 's']:
            requests_per_minute = count * 60
            requests_per_hour = count * 3600
        else:
            raise ValueError(f"Unknown period: {period}. Use 'minute', 'hour', or 'second'")
        
        return rate_limit(
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour,
            limiter=self
        )
    
    async def is_allowed(self, key: str) -> tuple[bool, dict]:
        """
        Check if request is allowed for given key
        
        Returns:
            (is_allowed, info_dict)
        """
        if self.algorithm == "sliding_window":
            return await self._sliding_window_check(key)
        elif self.algorithm == "token_bucket":
            return await self._token_bucket_check(key)
        else:
            return await self._fixed_window_check(key)
    
    async def _sliding_window_check(self, key: str) -> tuple[bool, dict]:
        """Sliding window rate limiting algorithm"""
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600
        
        if self.storage_backend == "redis" and self.redis_client:
            return await self._redis_sliding_window(key, now, minute_ago, hour_ago)
        else:
            return await self._memory_sliding_window(key, now, minute_ago, hour_ago)
    
    async def _redis_sliding_window(self, key: str, now: float, minute_ago: float, hour_ago: float) -> tuple[bool, dict]:
        """Redis-based sliding window implementation"""
        try:
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(f"{key}:minute", 0, minute_ago)
            pipe.zremrangebyscore(f"{key}:hour", 0, hour_ago)
            
            # Count current requests
            pipe.zcard(f"{key}:minute")
            pipe.zcard(f"{key}:hour")
            
            results = pipe.execute()
            minute_count = results[2]
            hour_count = results[3]
            
            # Check limits
            if minute_count >= self.requests_per_minute:
                return False, {
                    "error": "Rate limit exceeded",
                    "limit_type": "per_minute",
                    "current_count": minute_count,
                    "limit": self.requests_per_minute,
                    "reset_time": int(now + 60)
                }
            
            if hour_count >= self.requests_per_hour:
                return False, {
                    "error": "Rate limit exceeded", 
                    "limit_type": "per_hour",
                    "current_count": hour_count,
                    "limit": self.requests_per_hour,
                    "reset_time": int(now + 3600)
                }
            
            # Add current request
            pipe.zadd(f"{key}:minute", {str(now): now})
            pipe.zadd(f"{key}:hour", {str(now): now})
            pipe.expire(f"{key}:minute", 60)
            pipe.expire(f"{key}:hour", 3600)
            pipe.execute()
            
            return True, {
                "allowed": True,
                "minute_count": minute_count + 1,
                "hour_count": hour_count + 1,
                "minute_limit": self.requests_per_minute,
                "hour_limit": self.requests_per_hour
            }
            
        except Exception as e:
            logger.error(f"Redis rate limiting error: {e}")
            # Fallback to memory
            return await self._memory_sliding_window(key, now, minute_ago, hour_ago)
    
    async def _memory_sliding_window(self, key: str, now: float, minute_ago: float, hour_ago: float) -> tuple[bool, dict]:
        """Memory-based sliding window implementation"""
        async with _rate_limit_locks[key]:
            requests = _rate_limit_storage[key]
            
            # Remove old requests
            while requests and requests[0] < hour_ago:
                requests.popleft()
            
            # Count recent requests
            minute_count = sum(1 for req_time in requests if req_time > minute_ago)
            hour_count = len(requests)
            
            # Check limits
            if minute_count >= self.requests_per_minute:
                return False, {
                    "error": "Rate limit exceeded",
                    "limit_type": "per_minute", 
                    "current_count": minute_count,
                    "limit": self.requests_per_minute,
                    "reset_time": int(now + 60)
                }
            
            if hour_count >= self.requests_per_hour:
                return False, {
                    "error": "Rate limit exceeded",
                    "limit_type": "per_hour",
                    "current_count": hour_count, 
                    "limit": self.requests_per_hour,
                    "reset_time": int(now + 3600)
                }
            
            # Add current request
            requests.append(now)
            
            return True, {
                "allowed": True,
                "minute_count": minute_count + 1,
                "hour_count": hour_count + 1,
                "minute_limit": self.requests_per_minute,
                "hour_limit": self.requests_per_hour
            }
    
    async def _token_bucket_check(self, key: str) -> tuple[bool, dict]:
        """Token bucket algorithm implementation"""
        # Simplified token bucket for this example
        bucket_key = f"bucket:{key}"
        now = time.time()
        
        if self.redis_client:
            try:
                # Get current bucket state
                bucket_data = self.redis_client.hmget(bucket_key, ['tokens', 'last_refill'])
                tokens = float(bucket_data[0] or self.requests_per_minute)
                last_refill = float(bucket_data[1] or now)
                
                # Refill tokens based on time passed
                time_passed = now - last_refill
                tokens = min(self.requests_per_minute, tokens + (time_passed * self.requests_per_minute / 60))
                
                if tokens >= 1:
                    tokens -= 1
                    self.redis_client.hmset(bucket_key, {'tokens': tokens, 'last_refill': now})
                    self.redis_client.expire(bucket_key, 3600)
                    return True, {"allowed": True, "tokens_remaining": tokens}
                else:
                    return False, {"error": "Rate limit exceeded", "tokens_remaining": tokens}
                    
            except Exception as e:
                logger.error(f"Token bucket Redis error: {e}")
        
        # Memory fallback
        return True, {"allowed": True, "tokens_remaining": self.requests_per_minute}
    
    async def _fixed_window_check(self, key: str) -> tuple[bool, dict]:
        """Fixed window rate limiting"""
        now = int(time.time())
        window = now // 60  # 1-minute windows
        window_key = f"{key}:{window}"
        
        if self.redis_client:
            try:
                count = self.redis_client.get(window_key) or 0
                count = int(count)
                
                if count >= self.requests_per_minute:
                    return False, {
                        "error": "Rate limit exceeded",
                        "current_count": count,
                        "limit": self.requests_per_minute,
                        "window": window,
                        "reset_time": (window + 1) * 60
                    }
                
                pipe = self.redis_client.pipeline()
                pipe.incr(window_key)
                pipe.expire(window_key, 60)
                pipe.execute()
                
                return True, {
                    "allowed": True,
                    "count": count + 1,
                    "limit": self.requests_per_minute,
                    "window": window
                }
                
            except Exception as e:
                logger.error(f"Fixed window Redis error: {e}")
        
        return True, {"allowed": True}


# Default rate limiter instance
default_rate_limiter = RateLimiter(
    requests_per_minute=100,
    requests_per_hour=5000,
    algorithm="sliding_window"
)

# Rate limiter for underwriting (more restrictive)
underwriting_rate_limiter = RateLimiter(
    requests_per_minute=30,
    requests_per_hour=500,
    algorithm="sliding_window"
)

# Create a global rate_limiter instance that routes can import
rate_limiter = RateLimiter(
    requests_per_minute=60,
    requests_per_hour=1000,
    algorithm="sliding_window"
)


def rate_limit(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
    key_func: Optional[Callable] = None,
    limiter: Optional[RateLimiter] = None
):
    """
    Decorator for rate limiting API endpoints
    
    Args:
        requests_per_minute: Max requests per minute
        requests_per_hour: Max requests per hour  
        key_func: Function to generate rate limit key
        limiter: Custom RateLimiter instance
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # If no request found, skip rate limiting
                return await func(*args, **kwargs)
            
            # Generate rate limit key
            if key_func:
                key = key_func(request)
            else:
                # Default: use client IP + endpoint
                client_ip = request.client.host
                endpoint = request.url.path
                key = f"{client_ip}:{endpoint}"
            
            # Use provided limiter or create one
            if limiter:
                rate_limiter = limiter
            else:
                rate_limiter = RateLimiter(requests_per_minute, requests_per_hour)
            
            # Check rate limit
            allowed, info = await rate_limiter.is_allowed(key)
            
            if not allowed:
                # Add rate limit headers
                headers = {
                    "X-RateLimit-Limit-Minute": str(requests_per_minute),
                    "X-RateLimit-Limit-Hour": str(requests_per_hour),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info.get("reset_time", 0))
                }
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=info.get("error", "Rate limit exceeded"),
                    headers=headers
                )
            
            # Add success headers
            if info.get("allowed"):
                response = await func(*args, **kwargs)
                
                # Add rate limit headers to response if it's a JSONResponse
                if hasattr(response, 'headers'):
                    response.headers["X-RateLimit-Limit-Minute"] = str(requests_per_minute)
                    response.headers["X-RateLimit-Limit-Hour"] = str(requests_per_hour)
                    response.headers["X-RateLimit-Remaining-Minute"] = str(
                        requests_per_minute - info.get("minute_count", 0)
                    )
                    response.headers["X-RateLimit-Remaining-Hour"] = str(
                        requests_per_hour - info.get("hour_count", 0)
                    )
                
                return response
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def underwriting_rate_limit(key_func: Optional[Callable] = None):
    """
    Rate limiter specifically for underwriting endpoints
    More restrictive limits for resource-intensive operations
    """
    return rate_limit(
        requests_per_minute=30,
        requests_per_hour=500,
        key_func=key_func,
        limiter=underwriting_rate_limiter
    )


# Utility functions for common rate limiting patterns

def get_user_key(request: Request) -> str:
    """Generate rate limit key based on authenticated user"""
    user = getattr(request.state, 'user', None)
    if user:
        return f"user:{user.id}"
    return f"ip:{request.client.host}"


def get_ip_key(request: Request) -> str:
    """Generate rate limit key based on IP address"""
    return f"ip:{request.client.host}"


def get_endpoint_key(request: Request) -> str:
    """Generate rate limit key based on endpoint"""
    return f"endpoint:{request.url.path}"


def get_user_endpoint_key(request: Request) -> str:
    """Generate rate limit key based on user + endpoint"""
    user = getattr(request.state, 'user', None)
    if user:
        return f"user:{user.id}:endpoint:{request.url.path}"
    return f"ip:{request.client.host}:endpoint:{request.url.path}"


# Health check for rate limiter
async def rate_limiter_health_check() -> Dict[str, Any]:
    """Health check for rate limiting system"""
    status = {
        "status": "healthy",
        "backend": default_rate_limiter.storage_backend,
        "algorithm": default_rate_limiter.algorithm,
        "redis_available": False
    }
    
    if default_rate_limiter.redis_client:
        try:
            await default_rate_limiter.redis_client.ping()
            status["redis_available"] = True
        except Exception as e:
            status["redis_error"] = str(e)
            status["status"] = "degraded"
    
    return status