from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config
from typing import Dict, Any


# Store table schemas in memory
SCHEMA_CACHE: Dict[str, dict] = {}

async def load_schema(engine: AsyncEngine) -> None:
    """
    Load all tables & columns from the DB into SCHEMA_CACHE.
    Runs at FastAPI startup.
    
    For PostgreSQL: Loads tables from 'public' and 'metadata' schemas
    For SQLite: Loads all tables
    """

    global SCHEMA_CACHE

    # Define schemas to load (for PostgreSQL)
    schemas_to_load = []
    
    if 'postgresql' in str(engine.url):
        # PostgreSQL: Load from 'public' (main data tables) and 'metadata' (tracking tables)
        schemas_to_load = ['public', 'metadata']
    else:
        # SQLite: No schema concept
        schemas_to_load = [None]

    # Load tables from each schema
    for schema in schemas_to_load:
        metadata = MetaData()
        
        async with engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: metadata.reflect(
                bind=sync_conn, 
                schema=schema
            ))

        for table_name, table in metadata.tables.items():
            # For PostgreSQL, table_name will be 'schema.table_name'
            # Store both the full name and clean name
            clean_name = table_name.split('.')[-1] if '.' in table_name else table_name
            
            table_dict = table_to_dict(table)
            # Store the schema information
            table_dict['schema'] = schema
            table_dict['full_name'] = table_name
            
            SCHEMA_CACHE[clean_name] = table_dict

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
