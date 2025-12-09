from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

DATABASE_URL = "sqlite+aiosqlite:///./data/analytics.db"

# Create async engine
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False  # set True to see SQL logs (good for debugging)
)