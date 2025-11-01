from abc import ABC, abstractmethod
from typing import Any
import diskcache as dc
import asyncio


class ICache(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any:
        """
        Retrieve a value from the cache by its key.
        Returns None if the key does not exist.
        """
        pass

    @abstractmethod
    async def put(self, key: str, value: Any, ttl: int = 60) -> None:
        """
        Store a value in the cache with a given key and optional TTL (seconds).
        """
        pass


class DCCache(ICache):
    def __init__(self, cache_dir: str = "/tmp/dc_cache"):
        self.cache = dc.Cache(cache_dir)

    async def get(self, key: str) -> Any:
        # Run the synchronous get in a thread
        return await asyncio.to_thread(self.cache.get, key)

    async def put(self, key: str, value: Any, ttl: int = 60) -> None:
        # Run the synchronous set in a thread
        await asyncio.to_thread(self.cache.set, key, value, ttl)
