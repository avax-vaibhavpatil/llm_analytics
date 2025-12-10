"""
API Request/Response Models

These Pydantic models define the structure of HTTP requests and responses
for the FastAPI endpoints.

Why separate from LLM models?
- API models = External contract with users (HTTP)
- LLM models = Internal structure for LLM communication
- Separation of concerns
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ══════════════════════════════════════════════════════════════════
# REQUEST MODELS - What users send to the API
# ══════════════════════════════════════════════════════════════════

class AnalyzeColumnsRequest(BaseModel):
    """
    Request body for POST /analyze/columns endpoint.
    
    This is what the user sends when they want to analyze a requirement.
    
    Example:
        {
          "table_name": "crm_customers",
          "requirement": "Show me average MRR by industry"
        }
    """
    
    table_name: str = Field(
        description="Name of the table to analyze",
        min_length=1,
        examples=["crm_customers", "orders", "users"]
    )
    
    requirement: str = Field(
        description="Natural language analytics requirement from user",
        min_length=1,
        examples=[
            "Show me average MRR by industry",
            "Count customers who joined last month",
            "Total revenue by country"
        ]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "table_name": "crm_customers",
                "requirement": "Show me average MRR by industry for customers created in last 6 months"
            }
        }


# ══════════════════════════════════════════════════════════════════
# RESPONSE MODELS - What API returns to users
# ══════════════════════════════════════════════════════════════════

class AnalyzeColumnsResponse(BaseModel):
    """
    Response body for POST /analyze/columns endpoint.
    
    This is the complete analysis result sent back to the user.
    Contains everything from the user story requirements.
    
    Example:
        {
          "technical_summary": "Calculate average MRR grouped by industry",
          "required_columns": ["mrr", "industry"],
          "available_columns": ["mrr", "industry"],
          "missing_columns": [],
          "optional_columns": ["country"],
          "sql_filters": {"industry": "Healthcare", "arr": {">": 100000}},
          "assumptions": "...",
          "recommendations": ["✅ All columns available"],
          "analysis_complete": true
        }
    """
    
    technical_summary: str = Field(
        description="Technical interpretation of the user's requirement"
    )
    
    required_columns: List[str] = Field(
        description="List of columns absolutely needed for this analysis"
    )
    
    available_columns: List[str] = Field(
        description="Required columns that exist in the table (ready to use)"
    )
    
    missing_columns: List[str] = Field(
        description="Required columns that don't exist in the table (need attention)"
    )
    
    optional_columns: List[str] = Field(
        description="Columns that would enhance the analysis but aren't critical",
        default_factory=list
    )
    
    sql_filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="SQL filter conditions extracted from the user's query"
    )
    
    assumptions: str = Field(
        description="Any assumptions made during analysis"
    )
    
    recommendations: List[str] = Field(
        description="Smart suggestions for handling the analysis",
        default_factory=list
    )
    
    analysis_complete: bool = Field(
        description="True if all required columns are available, False if some are missing"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "technical_summary": "Calculate average MRR grouped by industry",
                "required_columns": ["mrr", "industry"],
                "available_columns": ["mrr", "industry"],
                "missing_columns": [],
                "optional_columns": ["country", "segment"],
                "assumptions": "Assumed MRR represents monthly recurring revenue",
                "recommendations": [
                    "✅ All required columns are available",
                    "💡 Optional columns available for enhanced analysis: country, segment"
                ],
                "analysis_complete": True
            }
        }


# ══════════════════════════════════════════════════════════════════
# ERROR RESPONSE - For error cases
# ══════════════════════════════════════════════════════════════════

class ErrorResponse(BaseModel):
    """
    Standard error response format.
    
    Example:
        {
          "error": "Table 'invalid_table' not found",
          "detail": "Available tables: crm_customers, orders, users"
        }
    """
    
    error: str = Field(
        description="Error message"
    )
    
    detail: str = Field(
        description="Additional details about the error",
        default=""
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Table not found",
                "detail": "Table 'xyz' does not exist. Available tables: crm_customers, orders"
            }
        }


# ══════════════════════════════════════════════════════════════════
# HELPER MODELS - For other endpoints
# ══════════════════════════════════════════════════════════════════

class TableInfo(BaseModel):
    """Information about a single table"""
    
    table_name: str = Field(description="Name of the table")
    column_count: int = Field(description="Number of columns in the table")


class ListTablesResponse(BaseModel):
    """
    Response for GET /tables endpoint.
    
    Lists all available tables in the database.
    
    Example:
        {
          "tables": [
            {"table_name": "crm_customers", "column_count": 33},
            {"table_name": "orders", "column_count": 25}
          ],
          "total_tables": 2
        }
    """
    
    tables: List[TableInfo] = Field(
        description="List of available tables"
    )
    
    total_tables: int = Field(
        description="Total number of tables"
    )


class TableSchemaResponse(BaseModel):
    """
    Response for GET /tables/{table_name}/schema endpoint.
    
    Returns detailed schema for a specific table.
    """
    
    table_name: str
    columns: List[dict]
    total_columns: int


class GenerateReportRequest(BaseModel):
    """
    Request body for POST /reports/generate endpoint.
    
    This is what the user sends to fetch REAL DATA from the database.
    
    Example:
        {
          "table_name": "crm_customers",
          "columns": ["customer_id", "first_name", "segment", "mrr"],
          "filters": {"segment": "Enterprise", "mrr": {">": 500}},
          "limit": 100
        }
    """
    
    table_name: str = Field(
        description="Name of the table to query"
    )
    
    columns: List[str] = Field(
        description="List of columns to include in the report"
    )
    
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional filters to apply (e.g., {'segment': 'Enterprise', 'mrr': {'>': 500}})"
    )
    
    limit: Optional[int] = Field(
        default=100,
        description="Maximum number of rows to return (default: 100, max: 1000)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "table_name": "crm_customers",
                "columns": ["customer_id", "first_name", "last_name", "segment", "mrr"],
                "filters": {"segment": "Enterprise"},
                "limit": 50
            }
        }


class GenerateReportResponse(BaseModel):
    """
    Response body for POST /reports/generate endpoint.
    
    Contains the REAL DATA from the database.
    
    Example:
        {
          "table_name": "crm_customers",
          "columns": ["customer_id", "first_name", "segment", "mrr"],
          "row_count": 292,
          "data": [
            {"customer_id": "CUST-001", "first_name": "John", "segment": "Enterprise", "mrr": 850},
            ...
          ],
          "query_executed": "SELECT customer_id, first_name, segment, mrr FROM crm_customers WHERE segment = 'Enterprise' LIMIT 100"
        }
    """
    
    table_name: str = Field(
        description="Name of the table queried"
    )
    
    columns: List[str] = Field(
        description="List of columns included in the results"
    )
    
    row_count: int = Field(
        description="Number of rows returned"
    )
    
    data: List[Dict[str, Any]] = Field(
        description="Actual data rows from the database"
    )
    
    query_executed: str = Field(
        description="SQL query that was executed (for debugging)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "table_name": "crm_customers",
                "columns": ["customer_id", "first_name", "segment", "mrr"],
                "row_count": 2,
                "data": [
                    {"customer_id": "CUST-001", "first_name": "John", "segment": "Enterprise", "mrr": 850},
                    {"customer_id": "CUST-002", "first_name": "Jane", "segment": "Enterprise", "mrr": 920}
                ],
                "query_executed": "SELECT customer_id, first_name, segment, mrr FROM crm_customers WHERE segment = 'Enterprise' LIMIT 100"
            }
        }


# ══════════════════════════════════════════════════════════════════
# USAGE EXAMPLE (for documentation)
# ══════════════════════════════════════════════════════════════════

"""
How these models are used in FastAPI:

    from fastapi import FastAPI
    from app.routes.schema import AnalyzeColumnsRequest, AnalyzeColumnsResponse
    
    app = FastAPI()
    
    @app.post("/analyze/columns", response_model=AnalyzeColumnsResponse)
    async def analyze_columns(request: AnalyzeColumnsRequest):
        # FastAPI automatically validates request against AnalyzeColumnsRequest
        # Returns response that matches AnalyzeColumnsResponse
        return {...}
    
    Benefits:
    - Automatic validation
    - Auto-generated API docs (Swagger/OpenAPI)
    - Type safety
    - Clear contract with API users
"""

