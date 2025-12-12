"""
LLM Output Models

This module defines Pydantic models that specify the EXACT structure
we expect from the LLM when it analyzes user requirements.

Why Pydantic?
- Automatic validation: If LLM returns wrong format, we catch it immediately
- Type safety: IDE autocomplete, no typos
- Self-documenting: Field descriptions help both developers and LLM

How LangChain uses this:
1. We pass this model to LangChain: llm.with_structured_output(ColumnPlanOutput)
2. LangChain tells the LLM: "Your response must match this JSON structure"
3. LLM returns JSON
4. LangChain validates and converts to Python object
5. We get type-safe access: result.required_columns (not result["required_columns"])
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional, Union


class ColumnPlanOutput(BaseModel):
    """
    Structured output from LLM when analyzing column requirements.
    
    This defines what we expect when user asks:
    "Show me average MRR by industry in last 6 months"
    
    Example output:
    {
        "technical_summary": "Calculate average MRR grouped by industry...",
        "required_columns": ["mrr", "industry", "created_at"],
        "optional_columns": ["country", "segment"],
        "assumptions": "Used created_at as date field for filtering"
    }
    """
    
    technical_summary: str = Field(
        description=(
            "A clear technical interpretation of the user's requirement. "
            "Explain WHAT analysis is needed in database terms."
        ),
        examples=[
            "Calculate average MRR, grouped by industry, filtered for customers created in last 6 months",
            "Count total orders per vendor, sorted by revenue",
        ]
    )
    
    required_columns: List[str] = Field(
        description=(
            "List of column names that are ABSOLUTELY NECESSARY for this analysis. "
            "Without these columns, the analysis cannot be performed. "
            "Only include actual column names (lowercase, no spaces)."
        ),
        examples=[
            ["mrr", "industry", "created_at"],
            ["order_id", "vendor_id", "total_amount"]
        ]
    )
    
    optional_columns: List[str] = Field(
        default_factory=list,  # If LLM doesn't provide this, use empty list []
        description=(
            "List of columns that would ENHANCE the analysis but aren't critical. "
            "These columns add context, enable better filtering, or provide additional insights."
        ),
        examples=[
            ["country", "segment", "plan_type"],
            ["customer_name", "city"]
        ]
    )
    
    assumptions: str = Field(
        description=(
            "Any assumptions made while interpreting the requirement. "
            "Mention if you assumed a specific column for date filtering, "
            "aggregation method, or interpretation of ambiguous terms."
        ),
        examples=[
            "Assumed 'created_at' is the date column for 'last 6 months' filtering",
            "Interpreted 'revenue' as 'total_amount' column",
        ]
    )
    
    sql_filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "SQL filter conditions extracted from the user's query as a dictionary. "
            "Format: {\"column_name\": \"value\"} for equality, or {\"column_name\": {\"operator\": value}} for comparisons. "
            "Operators: '>', '<', '>=', '<=', '=', '!='. "
            "Examples: "
            "{\"industry\": \"Healthcare\"} for exact match, "
            "{\"arr\": {\">\": 100000}} for ARR > 100k, "
            "{\"is_customer\": 1} for boolean flags. "
            "Leave as null if no specific filters are mentioned."
        ),
        examples=[
            {"industry": "Healthcare", "arr": {">": 100000}},
            {"segment": "Enterprise", "mrr": {">": 5000}},
            {"country": "USA", "is_active": 1}
        ]
    )
    
    # Optional: Add a custom method for easier debugging
    def __str__(self) -> str:
        """Pretty print for debugging"""
        return f"""
ColumnPlanOutput:
  Summary: {self.technical_summary}
  Required: {', '.join(self.required_columns)}
  Optional: {', '.join(self.optional_columns) if self.optional_columns else 'None'}
  Filters: {self.sql_filters if self.sql_filters else 'None'}
  Assumptions: {self.assumptions}
"""


# Future: You can add more models here as needed
# Example:
# class SQLGenerationOutput(BaseModel):
#     sql_query: str
#     explanation: str
#     warnings: List[str]

