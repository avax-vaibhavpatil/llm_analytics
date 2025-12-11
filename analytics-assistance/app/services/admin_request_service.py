"""
Admin Request Service - Handle saving non-matched queries

This service handles the business logic for saving queries that couldn't
be fulfilled due to missing columns.

Flow:
    User query → Missing columns detected → User clicks "Register with Admin"
    → Frontend sends data → This service saves to DB → Returns confirmation

Why separate service?
- Routes should only handle HTTP (request/response)
- Services handle business logic (database operations)
- Easier to test and maintain
"""

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from typing import Dict, Any
from datetime import datetime


async def save_admin_request(
    engine: AsyncEngine,
    original_query: str,
    technical_interpretation: str,
    table_name: str,
    required_columns: list[str],
    missing_columns: list[str],
    available_columns: list[str]
) -> int:
    """
    Save a non-matched/partial-matched query to admin_report_requests table.
    
    This function inserts a new record when user registers their query
    with admin because required columns are missing.
    
    Args:
        engine: SQLAlchemy async engine (database connection)
        original_query: User's exact query text
        technical_interpretation: LLM's understanding of the query
        table_name: Table user tried to query
        required_columns: List of columns needed
        missing_columns: List of columns that don't exist
        available_columns: List of columns that do exist
    
    Returns:
        int: ID of the newly inserted record
        
    Example:
        >>> request_id = await save_admin_request(
        ...     engine=engine,
        ...     original_query="give me date of birth",
        ...     technical_interpretation="User wants date_of_birth column...",
        ...     table_name="crm_customers",
        ...     required_columns=["date_of_birth"],
        ...     missing_columns=["date_of_birth"],
        ...     available_columns=[]
        ... )
        >>> print(request_id)  # 123
    """
    
    # ═══════════════════════════════════════════════════════════
    # STEP 1: Prepare the data
    # ═══════════════════════════════════════════════════════════
    
    # Create a title from first 50 chars of query
    request_title = original_query[:50] + "..." if len(original_query) > 50 else original_query
    
    # Build a comprehensive description with all details
    request_description = f"""
Original Query: "{original_query}"

Table: {table_name}

Technical Interpretation:
{technical_interpretation}

Required Columns: {', '.join(required_columns)}
Missing Columns: {', '.join(missing_columns)}
Available Columns: {', '.join(available_columns) if available_columns else 'None'}

Status: Pending admin review
    """.strip()
    
    # Set request type
    request_type = "missing_columns"
    
    # Set status
    status = "pending"
    
    # ═══════════════════════════════════════════════════════════
    # STEP 2: Build SQL INSERT query
    # ═══════════════════════════════════════════════════════════
    
    # Why use text() and not ORM?
    # - Simpler for single inserts
    # - Don't need ORM model for this simple operation
    # - Direct SQL is clear and explicit
    
    insert_query = text("""
        INSERT INTO metadata.admin_report_requests (
            request_title,
            request_description,
            request_type,
            status,
            created_at,
            updated_at
        )
        VALUES (
            :request_title,
            :request_description,
            :request_type,
            :status,
            :created_at,
            :updated_at
        )
        RETURNING request_id
    """)
    
    # ═══════════════════════════════════════════════════════════
    # STEP 3: Execute query with parameters
    # ═══════════════════════════════════════════════════════════
    
    # Use async context manager for safe connection handling
    async with engine.begin() as conn:
        result = await conn.execute(
            insert_query,
            {
                "request_title": request_title,
                "request_description": request_description,
                "request_type": request_type,
                "status": status,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        )
        
        # Get the returned request_id
        request_id = result.scalar_one()
        
        # Note: No need to commit() when using engine.begin()
        # It auto-commits when exiting the context manager
        
        return request_id

