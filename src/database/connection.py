"""
Async PostgreSQL connection pool using asyncpg.
Manages concurrent database access efficiently.
"""
import asyncpg
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from loguru import logger

from src.utils.config import get_settings


class Database:
    """
    Async PostgreSQL connection pool.
    
    Why a pool?
    - Creating a new connection takes ~50ms — too slow per query
    - A pool keeps connections ready for reuse
    - min_size=5: always keep 5 ready
    - max_size=20: never exceed 20 concurrent connections
    """
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        settings = get_settings()
        self.dsn = settings.database_url
    
    async def connect(self) -> bool:
        """Initialize the connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self.dsn,
                min_size=5,
                max_size=20,
                command_timeout=60,
            )
            
            # Test the connection
            async with self.pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                logger.success(f"✅ Database connected: {version[:50]}...")
            
            return True
        except Exception as e:
            logger.exception(f"❌ Database connection failed: {e}")
            return False
    
    @asynccontextmanager
    async def acquire(self):
        """Context manager for acquiring a connection."""
        if not self.pool:
            raise RuntimeError("Database not connected. Call connect() first.")
        async with self.pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query (INSERT/UPDATE/DELETE)."""
        async with self.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> List[Dict]:
        """Fetch multiple rows."""
        async with self.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def fetchrow(self, query: str, *args) -> Optional[Dict]:
        """Fetch a single row."""
        async with self.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetchval(self, query: str, *args):
        """Fetch a single value."""
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)
    
    async def close(self):
        """Close all connections."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")


# Global singleton
_db: Optional[Database] = None


async def get_db() -> Database:
    """Get or create the global database instance."""
    global _db
    if _db is None:
        _db = Database()
        await _db.connect()
    return _db


async def close_db():
    """Close the global database instance."""
    global _db
    if _db:
        await _db.close()
        _db = None