"""
Report Generator Service

This service executes REAL SQL queries against the database
and returns actual data (not mock data!).

It builds safe, parameterized SQL queries based on user requirements.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from typing import List, Dict, Any, Optional
import logging
from app.schemas.schema_registry import get_table_schema

logger = logging.getLogger(__name__)


async def generate_report(
    engine: AsyncEngine,
    table_name: str,
    columns: List[str],
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Execute a real SQL query and return actual database results.
    
    Args:
        engine: SQLAlchemy async engine
        table_name: Name of the table to query
        columns: List of columns to select
        filters: Optional filters (e.g., {'segment': 'Enterprise', 'mrr': {'>': 500}})
        limit: Maximum number of rows to return (capped at 1000)
    
    Returns:
        Dictionary with:
        - table_name: str
        - columns: List[str]
        - row_count: int
        - data: List[Dict[str, Any]]
        - query_executed: str (for debugging)
    
    Example:
        result = await generate_report(
            engine=engine,
            table_name='crm_customers',
            columns=['customer_id', 'first_name', 'segment', 'mrr'],
            filters={'segment': 'Enterprise'},
            limit=100
        )
    """
    
    # ═══════════════════════════════════════════════════════════
    # STEP 1: Validate and cap limit
    # ═══════════════════════════════════════════════════════════
    
    if limit > 1000:
        limit = 1000
        logger.warning(f"Limit capped at 1000 rows (requested: {limit})")
    
    # ═══════════════════════════════════════════════════════════
    # STEP 2: Get schema information and build full table name
    # ═══════════════════════════════════════════════════════════
    
    table_info = get_table_schema(table_name)
    
    # Build full table name with schema prefix (for PostgreSQL)
    if table_info and table_info.get('schema'):
        full_table_name = f"{table_info['schema']}.{table_name}"
    else:
        full_table_name = table_name
    
    logger.info(f"Using full table name: {full_table_name}")
    
    # ═══════════════════════════════════════════════════════════
    # STEP 3: Build SQL query
    # ═══════════════════════════════════════════════════════════
    
    # Build SELECT clause
    columns_str = ", ".join(columns)
    
    # Build WHERE clause
    where_clause = ""
    params = {}
    
    if filters:
        conditions = []
        for col, value in filters.items():
            if isinstance(value, dict):
                # Handle operators like {'mrr': {'>': 500}}
                for operator, filter_value in value.items():
                    param_name = f"{col}_{operator.replace('>', 'gt').replace('<', 'lt').replace('=', 'eq')}"
                    if operator == '>':
                        conditions.append(f"{col} > :{param_name}")
                    elif operator == '<':
                        conditions.append(f"{col} < :{param_name}")
                    elif operator == '>=':
                        conditions.append(f"{col} >= :{param_name}")
                    elif operator == '<=':
                        conditions.append(f"{col} <= :{param_name}")
                    elif operator == '=':
                        conditions.append(f"{col} = :{param_name}")
                    elif operator == '!=':
                        conditions.append(f"{col} != :{param_name}")
                    params[param_name] = filter_value
            else:
                # Simple equality: {'segment': 'Enterprise'}
                param_name = f"{col}_eq"
                conditions.append(f"{col} = :{param_name}")
                params[param_name] = value
        
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
    
    # Build final query with schema prefix
    sql_query = f"SELECT {columns_str} FROM {full_table_name}{where_clause} LIMIT :limit"
    params['limit'] = limit
    
    logger.info(f"Executing query: {sql_query}")
    logger.info(f"With params: {params}")
    
    # ═══════════════════════════════════════════════════════════
    # STEP 3: Execute query and fetch results
    # ═══════════════════════════════════════════════════════════
    
    async with engine.begin() as conn:
        result = await conn.execute(text(sql_query), params)
        rows = result.fetchall()
        
        # Convert rows to list of dictionaries
        data = []
        for row in rows:
            # row._mapping gives us a dict-like object
            data.append(dict(row._mapping))
    
    # ═══════════════════════════════════════════════════════════
    # STEP 4: Return results
    # ═══════════════════════════════════════════════════════════
    
    return {
        "table_name": table_name,
        "columns": columns,
        "row_count": len(data),
        "data": data,
        "query_executed": sql_query.replace(":limit", str(limit))
        .replace(":".join([f":{k}" for k in params.keys()]), 
                 ", ".join([str(v) for v in params.values()]))
    }


# ══════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ══════════════════════════════════════════════════════════════════

"""
Example 1: Simple query (no filters)
-------------------------------------

result = await generate_report(
    engine=engine,
    table_name='crm_customers',
    columns=['customer_id', 'first_name', 'last_name'],
    limit=10
)

# Returns:
{
    "table_name": "crm_customers",
    "columns": ["customer_id", "first_name", "last_name"],
    "row_count": 10,
    "data": [
        {"customer_id": "CUST-001", "first_name": "John", "last_name": "Doe"},
        ...
    ],
    "query_executed": "SELECT customer_id, first_name, last_name FROM crm_customers LIMIT 10"
}


Example 2: Query with simple filter
------------------------------------

result = await generate_report(
    engine=engine,
    table_name='crm_customers',
    columns=['customer_id', 'segment', 'mrr'],
    filters={'segment': 'Enterprise'},
    limit=50
)

# Returns:
{
    "table_name": "crm_customers",
    "columns": ["customer_id", "segment", "mrr"],
    "row_count": 50,
    "data": [
        {"customer_id": "CUST-001", "segment": "Enterprise", "mrr": 850},
        ...
    ],
    "query_executed": "SELECT ... FROM crm_customers WHERE segment = 'Enterprise' LIMIT 50"
}


Example 3: Query with comparison operators
-------------------------------------------

result = await generate_report(
    engine=engine,
    table_name='crm_customers',
    columns=['customer_id', 'mrr'],
    filters={'mrr': {'>': 500}},
    limit=100
)

# Returns data where MRR > 500
"""


