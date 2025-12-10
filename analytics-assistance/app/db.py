from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DATABASE_URL from environment (PostgreSQL required)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Please set it in .env file. "
        "Example: DATABASE_URL=postgresql+asyncpg://user:password@localhost:5430/analytics-llm"
    )

# Create async engine
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,  # set True to see SQL logs (good for debugging)
    pool_size=10,  # Connection pool size
    max_overflow=20  # Max connections beyond pool_size
)