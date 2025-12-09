from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config
from typing import Dict, Any


# Store table schemas in memory
SCHEMA_CACHE: Dict[str, dict] = {}

async def load_schema(engine: AsyncEngine) -> None:
    """
    Load all tables & columns from the DB into SCHEMA_CACHE.
    Runs at FastAPI startup.
    
    """

    global SCHEMA_CACHE

    metadata = MetaData()

    async with engine.begin() as conn:
        await conn.run_sync(metadata.reflect)

    for table_name, table in metadata.tables.items():
        SCHEMA_CACHE[table_name] = table_to_dict(table)

def table_to_dict(table) -> Dict[str, Any]:
    """Convert SQLAlchemy table into JSON-friendly dict"""
    cols = []
    for col in table.columns:
        cols.append({
            "name": col.name,
            "type": str(col.type),
            "nullable": col.nullable,
            "primary_key": col.primary_key,
        })
    return {
        "table_name": table.name,
        "columns": cols,
    }

def get_table_schema(table_name: str):
    return SCHEMA_CACHE.get(table_name)

def list_tables():
    return list(SCHEMA_CACHE.keys())
