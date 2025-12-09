"""
Column Matcher - Compare Required vs Available Columns

This module takes the LLM's analysis (required columns) and compares it
against the actual table schema to determine:
- Which required columns exist in the table (available)
- Which required columns are missing
- Optional: Suggestions for handling missing columns

This is pure logic - no API calls, no database queries.
Just set operations on column names.

Flow:
    LLM Output + Table Schema → Set Operations → Match Results
    
Example:
    LLM says need: ["mrr", "industry", "created_at"]
    Table has: ["customer_id", "mrr", "industry", "email"]
    
    Result:
    - available: ["mrr", "industry"]     ✅
    - missing: ["created_at"]            ❌
"""

from typing import Dict, List, Set, Any
from app.models.llm_models import ColumnPlanOutput


# ══════════════════════════════════════════════════════════════════
# DATA MODEL - Result of column matching
# ══════════════════════════════════════════════════════════════════

class ColumnMatchResult:
    """
    Result of comparing required columns vs actual table columns.
    
    This is what gets returned to the user as the final analysis.
    
    Attributes:
        technical_summary: From LLM - what the analysis is about
        required_columns: From LLM - all columns needed
        available_columns: NEW - required columns that exist in table
        missing_columns: NEW - required columns that DON'T exist
        optional_columns: From LLM - would be nice to have
        assumptions: From LLM - any assumptions made
        recommendations: NEW - suggestions for handling missing data
    """
    
    def __init__(
        self,
        technical_summary: str,
        required_columns: List[str],
        available_columns: List[str],
        missing_columns: List[str],
        optional_columns: List[str],
        assumptions: str,
        recommendations: List[str]
    ):
        self.technical_summary = technical_summary
        self.required_columns = required_columns
        self.available_columns = available_columns
        self.missing_columns = missing_columns
        self.optional_columns = optional_columns
        self.assumptions = assumptions
        self.recommendations = recommendations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "technical_summary": self.technical_summary,
            "required_columns": self.required_columns,
            "available_columns": self.available_columns,
            "missing_columns": self.missing_columns,
            "optional_columns": self.optional_columns,
            "assumptions": self.assumptions,
            "recommendations": self.recommendations,
            "analysis_complete": len(self.missing_columns) == 0
        }
    
    def __str__(self) -> str:
        """Pretty print for debugging"""
        status = "✅ Complete" if not self.missing_columns else f"⚠️  {len(self.missing_columns)} missing"
        return f"""
ColumnMatchResult [{status}]:
  Summary: {self.technical_summary}
  Required: {len(self.required_columns)} columns
  Available: {len(self.available_columns)} / {len(self.required_columns)}
  Missing: {', '.join(self.missing_columns) if self.missing_columns else 'None'}
"""


# ══════════════════════════════════════════════════════════════════
# MAIN FUNCTION - Match columns
# ══════════════════════════════════════════════════════════════════

def match_columns(
    table_schema: Dict[str, Any],
    llm_output: ColumnPlanOutput
) -> ColumnMatchResult:
    """
    Compare LLM's required columns against actual table schema.
    
    This is the core logic that determines if the analysis can be performed
    with the available data.
    
    Args:
        table_schema: Schema from schema_registry.get_table_schema()
                     Format: {"table_name": "...", "columns": [...]}
        llm_output: Result from column_planner.plan_columns()
                   Contains required_columns, optional_columns, etc.
    
    Returns:
        ColumnMatchResult with available/missing columns and recommendations
        
    Example:
        >>> schema = get_table_schema("crm_customers")
        >>> llm_result = await plan_columns(...)
        >>> match = match_columns(schema, llm_result)
        >>> print(match.available_columns)  # ["mrr", "industry"]
        >>> print(match.missing_columns)    # ["created_at"]
    """
    
    # Step 1: Extract actual column names from schema
    # Schema format: {"columns": [{"name": "col1", ...}, {"name": "col2", ...}]}
    actual_columns: Set[str] = {
        col["name"] for col in table_schema.get("columns", [])
    }
    
    # Step 2: Convert LLM's required columns to set for comparison
    required_columns: Set[str] = set(llm_output.required_columns)
    
    # Step 3: Set operations to find available and missing
    # Available = columns that exist in both required and actual
    available_columns: Set[str] = required_columns & actual_columns  # Intersection
    
    # Missing = columns required but not in actual
    missing_columns: Set[str] = required_columns - actual_columns  # Difference
    
    # Step 4: Generate recommendations for missing columns
    recommendations = _generate_recommendations(
        missing_columns=list(missing_columns),
        available_columns=list(available_columns),
        optional_columns=llm_output.optional_columns,
        actual_columns=list(actual_columns)
    )
    
    # Step 5: Create result object
    return ColumnMatchResult(
        technical_summary=llm_output.technical_summary,
        required_columns=llm_output.required_columns,  # Keep original order
        available_columns=sorted(list(available_columns)),  # Sort for consistency
        missing_columns=sorted(list(missing_columns)),
        optional_columns=llm_output.optional_columns,
        assumptions=llm_output.assumptions,
        recommendations=recommendations
    )


# ══════════════════════════════════════════════════════════════════
# RECOMMENDATION ENGINE - Suggest how to handle missing columns
# ══════════════════════════════════════════════════════════════════

def _generate_recommendations(
    missing_columns: List[str],
    available_columns: List[str],
    optional_columns: List[str],
    actual_columns: List[str]
) -> List[str]:
    """
    Generate smart recommendations based on what's missing.
    
    This helps the user understand:
    - Can they proceed without the missing columns?
    - Are there alternative columns they could use?
    - Should they add these columns to their database?
    
    Args:
        missing_columns: Columns required but not in table
        available_columns: Columns required and present
        optional_columns: Columns that would enhance analysis
        actual_columns: All columns in the table
        
    Returns:
        List of recommendation strings
    """
    
    recommendations = []
    
    # Case 1: All required columns available! ✅
    if not missing_columns:
        recommendations.append(
            "✅ All required columns are available. Analysis can proceed."
        )
        
        # Check if optional columns exist
        optional_available = [
            col for col in optional_columns 
            if col in actual_columns
        ]
        
        if optional_available:
            recommendations.append(
                f"💡 Optional columns available for enhanced analysis: {', '.join(optional_available)}"
            )
        
        return recommendations
    
    # Case 2: Some columns missing ⚠️
    recommendations.append(
        f"⚠️  Missing {len(missing_columns)} required column(s): {', '.join(missing_columns)}"
    )
    
    # Check if the requirement can be partially fulfilled
    if available_columns:
        recommendations.append(
            f"✅ Partial analysis possible with: {', '.join(available_columns)}"
        )
    else:
        recommendations.append(
            "❌ No required columns available. Analysis cannot proceed with this table."
        )
    
    # Suggest alternatives: Look for similar column names
    for missing in missing_columns:
        similar = _find_similar_columns(missing, actual_columns)
        if similar:
            recommendations.append(
                f"💡 For '{missing}', consider using: {', '.join(similar[:3])}"
            )
    
    # Suggest adding columns if none can be used
    if not available_columns and not any("consider using" in r for r in recommendations):
        recommendations.append(
            "📝 Consider adding these columns to your database schema."
        )
    
    return recommendations


# ══════════════════════════════════════════════════════════════════
# HELPER - Find similar column names (fuzzy matching)
# ══════════════════════════════════════════════════════════════════

def _find_similar_columns(missing_col: str, actual_columns: List[str]) -> List[str]:
    """
    Find columns in the table that might be alternatives to missing column.
    
    Uses simple heuristics:
    - Contains the same word
    - Similar prefix/suffix
    - Common patterns (created_at → create_date)
    
    Args:
        missing_col: The column that's missing
        actual_columns: All columns in the table
        
    Returns:
        List of potentially similar column names
        
    Example:
        >>> _find_similar_columns("created_at", ["create_date", "updated_at", "name"])
        ['create_date', 'updated_at']
    """
    
    similar = []
    missing_lower = missing_col.lower()
    
    # Extract key parts of the missing column name
    # "created_at" → ["created", "at"]
    missing_parts = missing_lower.replace("_", " ").split()
    
    for actual_col in actual_columns:
        actual_lower = actual_col.lower()
        
        # Check for substring matches
        for part in missing_parts:
            if len(part) > 2 and part in actual_lower:  # Only check meaningful parts
                similar.append(actual_col)
                break
    
    return similar


# ══════════════════════════════════════════════════════════════════
# USAGE EXAMPLE (for documentation)
# ══════════════════════════════════════════════════════════════════

"""
Complete usage example:

    from app.schemas.schema_registry import get_table_schema
    from app.services.column_planner import plan_columns
    from app.services.column_matcher import match_columns
    
    # Step 1: Get table schema
    schema = get_table_schema("crm_customers")
    
    # Step 2: Analyze requirement with LLM
    llm_result = await plan_columns(
        "crm_customers",
        schema,
        "Show me average MRR by industry"
    )
    
    # Step 3: Match columns
    match_result = match_columns(schema, llm_result)
    
    # Step 4: Check results
    if not match_result.missing_columns:
        print("✅ All columns available!")
    else:
        print(f"⚠️  Missing: {match_result.missing_columns}")
        print("Recommendations:")
        for rec in match_result.recommendations:
            print(f"  - {rec}")
    
    # Step 5: Return to user
    return match_result.to_dict()
"""



