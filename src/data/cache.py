"""
Data Cache - Caching layer for performance optimization
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
import hashlib
import json
import pickle
from datetime import datetime, timedelta
import os


class DataCache:
    """
    Data caching system for performance optimization
    
    Features:
    - File-based caching (pickle, parquet)
    - Memory caching with LRU eviction
    - TTL (Time To Live) support
    - Cache invalidation
    - Compression support
    
    Usage:
        cache = DataCache(cache_dir="./cache")
        cache.set("key", df, ttl=3600)
        df = cache.get("key")
    """
    
    def __init__(
        self,
        cache_dir: str = "./outputs/cache",
        enable_memory_cache: bool = True,
        memory_cache_size: int = 100,
        default_ttl: int = 86400,  # 24 hours
        compression: str = "snappy"
    ):
        """
        Initialize data cache
        
        Args:
            cache_dir: Directory for file cache
            enable_memory_cache: Enable in-memory caching
            memory_cache_size: Maximum items in memory cache
            default_ttl: Default TTL in seconds
            compression: Compression method ("snappy", "gzip", None)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.enable_memory_cache = enable_memory_cache
        self.memory_cache_size = memory_cache_size
        self.default_ttl = default_ttl
        self.compression = compression
        
        # Memory cache with metadata
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"DataCache initialized: dir={cache_dir}, memory={enable_memory_cache}")
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache key hash"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str, suffix: str = ".parquet") -> Path:
        """Get cache file path"""
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}{suffix}"
    
    def _is_expired(self, timestamp: datetime, ttl: int) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() - timestamp > timedelta(seconds=ttl)
    
    def get(self, key: str) -> Optional[pd.DataFrame]:
        """
        Get cached data
        
        Args:
            key: Cache key
            
        Returns:
            Cached DataFrame or None if not found/expired
        """
        # Try memory cache first
        if self.enable_memory_cache:
            cached = self._memory_cache.get(key)
            if cached:
                if not self._is_expired(cached["timestamp"], cached["ttl"]):
                    logger.debug(f"Memory cache hit: {key}")
                    return cached["data"]
                else:
                    del self._memory_cache[key]
        
        # Try file cache
        cache_path = self._get_cache_path(key)
        meta_path = self._get_cache_path(key, ".meta.json")
        
        if cache_path.exists() and meta_path.exists():
            try:
                # Load metadata
                with open(meta_path, "r") as f:
                    meta = json.load(f)
                
                timestamp = datetime.fromisoformat(meta["timestamp"])
                ttl = meta.get("ttl", self.default_ttl)
                
                if self._is_expired(timestamp, ttl):
                    self.delete(key)
                    return None
                
                # Load data
                if cache_path.suffix == ".parquet":
                    df = pd.read_parquet(cache_path)
                else:
                    with open(cache_path, "rb") as f:
                        df = pickle.load(f)
                
                # Update memory cache
                if self.enable_memory_cache:
                    self._set_memory_cache(key, df, ttl)
                
                logger.debug(f"File cache hit: {key}")
                return df
                
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                self.delete(key)
        
        return None
    
    def set(
        self,
        key: str,
        data: pd.DataFrame,
        ttl: Optional[int] = None
    ):
        """
        Set cache data
        
        Args:
            key: Cache key
            data: DataFrame to cache
            ttl: Time to live in seconds (None for default)
        """
        ttl = ttl or self.default_ttl
        
        # Set memory cache
        if self.enable_memory_cache:
            self._set_memory_cache(key, data, ttl)
        
        # Set file cache
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_cache_path(key, ".meta.json")
            
            # Save data
            if self.compression and self.compression != "none":
                data.to_parquet(cache_path, compression=self.compression)
            else:
                data.to_parquet(cache_path)
            
            # Save metadata
            meta = {
                "key": key,
                "timestamp": datetime.now().isoformat(),
                "ttl": ttl,
                "shape": list(data.shape),
                "columns": list(data.columns)
            }
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=2)
            
            logger.debug(f"Cache set: {key}")
            
        except Exception as e:
            logger.warning(f"Failed to set cache: {e}")
    
    def _set_memory_cache(self, key: str, data: pd.DataFrame, ttl: int):
        """Set memory cache with LRU eviction"""
        # Simple LRU: remove oldest if full
        if len(self._memory_cache) >= self.memory_cache_size:
            oldest_key = min(
                self._memory_cache.keys(),
                key=lambda k: self._memory_cache[k]["timestamp"]
            )
            del self._memory_cache[oldest_key]
        
        self._memory_cache[key] = {
            "data": data,
            "timestamp": datetime.now(),
            "ttl": ttl
        }
    
    def delete(self, key: str):
        """Delete cache entry"""
        # Delete from memory
        if key in self._memory_cache:
            del self._memory_cache[key]
        
        # Delete from file
        cache_path = self._get_cache_path(key)
        meta_path = self._get_cache_path(key, ".meta.json")
        
        if cache_path.exists():
            cache_path.unlink()
        if meta_path.exists():
            meta_path.unlink()
        
        logger.debug(f"Cache deleted: {key}")
    
    def clear(self):
        """Clear all cache"""
        # Clear memory
        self._memory_cache.clear()
        
        # Clear files
        for file in self.cache_dir.glob("*"):
            file.unlink()
        
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        file_count = len(list(self.cache_dir.glob("*.parquet")))
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*"))
        
        return {
            "memory_cache_size": len(self._memory_cache),
            "file_cache_count": file_count,
            "total_size_mb": total_size / (1024 * 1024),
            "cache_dir": str(self.cache_dir)
        }
    
    def cache_data_fetch(self, func):
        """
        Decorator to cache data fetching functions
        
        Usage:
            @cache.cache_data_fetch
            def fetch_data(symbol, start_date, end_date):
                ...
        """
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
            
            # Try to get from cache
            cached = self.get(key)
            if cached is not None:
                return cached
            
            # Call function and cache result
            result = func(*args, **kwargs)
            if result is not None and not (isinstance(result, pd.DataFrame) and result.empty):
                self.set(key, result)
            
            return result
        
        return wrapper
