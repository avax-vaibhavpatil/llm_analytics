"""
Analytics Routes - Main API Endpoints

This module contains all the API endpoints that users interact with.
It wires together all the modules we built:
- schema_registry (get table schemas)
- column_planner (LLM analysis)
- column_matcher (compare required vs available)
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from app.routes.schema import (
    AnalyzeColumnsRequest,
    AnalyzeColumnsResponse,
    ErrorResponse,
    ListTablesResponse,
    TableInfo,
    TableSchemaResponse,
    GenerateReportRequest,
    GenerateReportResponse,
    RegisterAdminQueryRequest,
    RegisterAdminQueryResponse
)
from app.schemas.schema_registry import list_tables, get_table_schema
from app.services.column_planner import plan_columns
from app.services.column_matcher import match_columns
from app.services.report_generator import generate_report
from app.services.admin_request_service import save_admin_request
from app.db import engine


# ══════════════════════════════════════════════════════════════════
# CREATE ROUTER
# ══════════════════════════════════════════════════════════════════

router = APIRouter()


# ══════════════════════════════════════════════════════════════════
# MAIN ENDPOINT - Analyze Columns for Requirement
# ══════════════════════════════════════════════════════════════════

@router.post(
    "/analyze/columns",
    response_model=AnalyzeColumnsResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Table not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Analyze Column Requirements",
    description="""
    Analyze a natural language analytics requirement and determine:
    - What columns are required
    - Which columns exist in the table
    - Which columns are missing
    - Recommendations for proceeding
    
    This is the main endpoint that completes your user story!
    """
)
async def analyze_columns(request: AnalyzeColumnsRequest):
    """
    🎯 Main Analysis Endpoint - Wires Everything Together
    
    Flow:
    1. Validate table exists
    2. Get table schema from cache
    3. Send to LLM for analysis (column_planner)
    4. Match required vs available columns (column_matcher)
    5. Return complete response
    
    Example Request:
        POST /api/analyze/columns
        {
          "table_name": "crm_customers",
          "requirement": "Show me average MRR by industry"
        }
    
    Example Response:
        {
          "technical_summary": "Calculate average MRR grouped by industry",
          "required_columns": ["mrr", "industry"],
          "available_columns": ["mrr", "industry"],
          "missing_columns": [],
          "recommendations": ["✅ All columns available"]
        }
    """
    
    # ═══════════════════════════════════════════════════════════
    # STEP 1: Validate table exists
    # ═══════════════════════════════════════════════════════════
    
    available_tables = list_tables()
    
    if request.table_name not in available_tables:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Table '{request.table_name}' not found",
                "detail": f"Available tables: {', '.join(available_tables)}"
            }
        )
    
    # ═══════════════════════════════════════════════════════════
    # STEP 2: Get table schema from cache (fast!)
    # ═══════════════════════════════════════════════════════════
    
    table_schema = get_table_schema(request.table_name)
    
    if not table_schema:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to retrieve table schema",
                "detail": "Schema cache may be corrupted"
            }
        )
    
    # ═══════════════════════════════════════════════════════════
    # STEP 3: LLM Analysis - Determine required columns
    # ═══════════════════════════════════════════════════════════
    
    try:
        llm_result = await plan_columns(
            table_name=request.table_name,
            table_schema=table_schema,
            user_requirement=request.requirement,
            verbose=False  # Set to True to see token usage in logs
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "LLM analysis failed",
                "detail": str(e)
            }
        )
    
    # ═══════════════════════════════════════════════════════════
    # STEP 4: Column Matching - Compare required vs available
    # ═══════════════════════════════════════════════════════════
    
    try:
        match_result = match_columns(table_schema, llm_result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Column matching failed",
                "detail": str(e)
            }
        )
    
    # ═══════════════════════════════════════════════════════════
    # STEP 5: Return complete response
    # ═══════════════════════════════════════════════════════════
    
    return AnalyzeColumnsResponse(**match_result.to_dict())


# ══════════════════════════════════════════════════════════════════
# HELPER ENDPOINTS - List tables and schemas
# ══════════════════════════════════════════════════════════════════

@router.get(
    "/tables",
    response_model=ListTablesResponse,
    summary="List All Tables",
    description="Get a list of all available tables in the database"
)
async def get_tables():
    """
    List all available tables.
    
    Returns table names and column counts.
    Users can use this to select which table to analyze.
    """
    
    tables = list_tables()
    
    table_info_list = []
    for table_name in tables:
        schema = get_table_schema(table_name)
        table_info_list.append(
            TableInfo(
                table_name=table_name,
                column_count=len(schema['columns'])
            )
        )
    
    return ListTablesResponse(
        tables=table_info_list,
        total_tables=len(tables)
    )


@router.get(
    "/tables/{table_name}/schema",
    response_model=TableSchemaResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Table not found"}
    },
    summary="Get Table Schema",
    description="Get detailed schema information for a specific table"
)
async def get_table_schema_endpoint(table_name: str):
    """
    Get detailed schema for a specific table.
    
    Shows all columns with their types, nullable status, etc.
    Useful for exploring what data is available.
    """
    
    available_tables = list_tables()
    
    if table_name not in available_tables:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Table '{table_name}' not found",
                "detail": f"Available tables: {', '.join(available_tables)}"
            }
        )
    
    schema = get_table_schema(table_name)
    
    return TableSchemaResponse(
        table_name=table_name,
        columns=schema['columns'],
        total_columns=len(schema['columns'])
    )


# ══════════════════════════════════════════════════════════════════
# REPORT GENERATION ENDPOINT - Fetch REAL Data
# ══════════════════════════════════════════════════════════════════

@router.post(
    "/reports/generate",
    response_model=GenerateReportResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Table not found"},
        500: {"model": ErrorResponse, "description": "Query execution failed"}
    },
    summary="Generate Report with Real Data",
    description="""
    Execute a SQL query and return REAL DATA from the database.
    
    This endpoint replaces mock data with actual database results!
    """
)
async def generate_report_endpoint(request: GenerateReportRequest):
    """
    🔥 NEW ENDPOINT - Fetch REAL Data from Database
    
    This endpoint executes an actual SQL query and returns real results.
    No more mock data!
    
    Flow:
    1. Validate table exists
    2. Build safe SQL query with filters
    3. Execute query against database
    4. Return actual data
    
    Example Request:
        POST /api/reports/generate
        {
          "table_name": "crm_customers",
          "columns": ["customer_id", "first_name", "segment", "mrr"],
          "filters": {"segment": "Enterprise"},
          "limit": 50
        }
    
    Example Response:
        {
          "table_name": "crm_customers",
          "columns": ["customer_id", "first_name", "segment", "mrr"],
          "row_count": 50,
          "data": [
            {"customer_id": "CUST-001", "first_name": "John", "segment": "Enterprise", "mrr": 850},
            ...
          ],
          "query_executed": "SELECT ... FROM crm_customers WHERE segment = 'Enterprise' LIMIT 50"
        }
    """
    
    # ═══════════════════════════════════════════════════════════
    # STEP 1: Validate table exists
    # ═══════════════════════════════════════════════════════════
    
    available_tables = list_tables()
    
    if request.table_name not in available_tables:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Table '{request.table_name}' not found",
                "detail": f"Available tables: {', '.join(available_tables)}"
            }
        )
    
    # ═══════════════════════════════════════════════════════════
    # STEP 2: Validate columns exist in table
    # ═══════════════════════════════════════════════════════════
    
    table_schema = get_table_schema(request.table_name)
    available_columns = [col['name'] for col in table_schema['columns']]
    
    invalid_columns = [col for col in request.columns if col not in available_columns]
    
    if invalid_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Invalid columns: {', '.join(invalid_columns)}",
                "detail": f"Available columns: {', '.join(available_columns)}"
            }
        )
    
    # ═══════════════════════════════════════════════════════════
    # STEP 3: Generate report (execute SQL query)
    # ═══════════════════════════════════════════════════════════
    
    try:
        result = await generate_report(
            engine=engine,
            table_name=request.table_name,
            columns=request.columns,
            filters=request.filters,
            limit=request.limit or 100
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to execute query",
                "detail": str(e)
            }
        )
    
    # ═══════════════════════════════════════════════════════════
    # STEP 4: Return real data
    # ═══════════════════════════════════════════════════════════
    
    return GenerateReportResponse(**result)


# ══════════════════════════════════════════════════════════════════
# ADMIN REQUEST ENDPOINT - Register Non-Matched Queries
# ══════════════════════════════════════════════════════════════════

@router.post(
    "/admin/register-query",
    response_model=RegisterAdminQueryResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Failed to save request"}
    },
    summary="Register Non-Matched Query with Admin",
    description="""
    When AI cannot find all required columns for a query, user can register
    the query with admin for manual review and resolution.
    
    This endpoint saves the query details to the database for admin review.
    """
)
async def register_admin_query(request: RegisterAdminQueryRequest):
    """
    🔴 NEW ENDPOINT - Register Query with Admin
    
    When missing columns are detected, user can choose to register the query
    with admin instead of editing it. This saves all details for later review.
    
    Flow:
    1. Validate request data (automatic via Pydantic)
    2. Save to admin_report_requests table
    3. Return confirmation with request ID
    
    Example Request:
        POST /api/admin/register-query
        {
          "original_query": "give me date of birth of all customers",
          "technical_interpretation": "User wants date_of_birth column...",
          "table_name": "crm_customers",
          "required_columns": ["date_of_birth"],
          "missing_columns": ["date_of_birth"],
          "available_columns": []
        }
    
    Example Response:
        {
          "success": true,
          "request_id": 123,
          "message": "Your query has been registered with admin for review"
        }
    """
    
    # ═══════════════════════════════════════════════════════════
    # STEP 1: Save request to database
    # ═══════════════════════════════════════════════════════════
    
    try:
        request_id = await save_admin_request(
            engine=engine,
            original_query=request.original_query,
            technical_interpretation=request.technical_interpretation,
            table_name=request.table_name,
            required_columns=request.required_columns,
            missing_columns=request.missing_columns,
            available_columns=request.available_columns
        )
    except Exception as e:
        # If database insert fails, return error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to save admin request",
                "detail": str(e)
            }
        )
    
    # ═══════════════════════════════════════════════════════════
    # STEP 2: Return success response
    # ═══════════════════════════════════════════════════════════
    
    return RegisterAdminQueryResponse(
        success=True,
        request_id=request_id,
        message="Your query has been registered with admin for review. We'll notify you once it's resolved."
    )


# ══════════════════════════════════════════════════════════════════
# USAGE NOTES
# ══════════════════════════════════════════════════════════════════

"""
API Usage Flow:

1. List available tables:
   GET /api/tables
   
2. (Optional) View schema:
   GET /api/tables/crm_customers/schema
   
3. Analyze requirement:
   POST /api/analyze/columns
   {
     "table_name": "crm_customers",
     "requirement": "Show me average MRR by industry"
   }

All endpoints are automatically documented at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
"""

