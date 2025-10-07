"""
Redis cache configuration and utilities
"""

import redis.asyncio as redis
from app.core.config import settings
import json
from typing import Optional, Any
from datetime import timedelta


# Create Redis client with error handling
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_available = True
except Exception as e:
    print(f"Redis connection failed: {e}")
    redis_client = None
    redis_available = False


class CacheManager:
    """Redis cache manager with utility methods"""
    
    @staticmethod
    async def set(
        key: str, 
        value: Any, 
        expire: Optional[timedelta] = None
    ) -> bool:
        """Set a value in cache with optional expiration"""
        if not redis_available or not redis_client:
            return False
        try:
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            if expire:
                return await redis_client.setex(key, int(expire.total_seconds()), serialized_value)
            else:
                return await redis_client.set(key, serialized_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get a value from cache"""
        if not redis_available or not redis_client:
            return None
        try:
            value = await redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    @staticmethod
    async def delete(key: str) -> bool:
        """Delete a key from cache"""
        if not redis_available or not redis_client:
            return False
        try:
            return await redis_client.delete(key) > 0
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    async def exists(key: str) -> bool:
        """Check if a key exists in cache"""
        if not redis_available or not redis_client:
            return False
        try:
            return await redis_client.exists(key) > 0
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False


# Cache key generators
def event_search_cache_key(zip_codes: list, filters: dict) -> str:
    """Generate cache key for event search"""
    filter_str = "_".join([f"{k}:{v}" for k, v in sorted(filters.items())])
    zip_str = "_".join(sorted(zip_codes)) if zip_codes else "all"
    return f"events:search:{zip_str}:{filter_str}"


def user_profile_cache_key(user_id: str) -> str:
    """Generate cache key for user profile"""
    return f"user:profile:{user_id}"
