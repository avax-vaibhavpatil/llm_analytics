"""
Column Planner - LLM-Powered Requirement Analysis

This module uses LangChain + OpenAI to analyze user requirements and determine
what database columns are needed.

Cost Optimization Features:
1. Uses gpt-4o-mini by default (~$0.0002 per request)
2. Token limits to prevent runaway costs
3. Low temperature for focused, concise responses
4. Configurable via environment variables
5. Token usage logging to monitor spending

Flow:
    User Requirement → Prompt Template → LLM → Structured Output → Validation
    
Example:
    Input: "Show me average MRR by industry"
    Output: ColumnPlanOutput(
        technical_summary="Calculate average MRR grouped by industry",
        required_columns=["mrr", "industry"],
        optional_columns=["country"],
        assumptions="..."
    )
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser

from app.models.llm_models import ColumnPlanOutput
from app.services.prompts import COLUMN_PLANNER_PROMPT, format_columns_for_prompt


# Load environment variables from .env file
load_dotenv()


# ══════════════════════════════════════════════════════════════════
# CONFIGURATION - All cost optimization settings
# ══════════════════════════════════════════════════════════════════

# Model selection (default: cheapest model)
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Temperature (0.0 = focused, 1.0 = creative)
# Low temperature = less tokens used, more consistent
DEFAULT_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))

# Max tokens for response (limits cost per request)
# Our JSON needs ~100-150 tokens, so 200 is safe
DEFAULT_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "200"))

# Timeout (don't wait forever for response)
DEFAULT_TIMEOUT = 30  # seconds


# ══════════════════════════════════════════════════════════════════
# LLM CLIENT - Configured for cost efficiency
# ══════════════════════════════════════════════════════════════════

def get_llm(
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> ChatOpenAI:
    """
    Create and configure OpenAI LLM client with cost optimization.
    
    Args:
        model: OpenAI model name (default: gpt-4o-mini for low cost)
        temperature: Randomness (0.0-1.0, lower = cheaper)
        max_tokens: Maximum response length (limits cost)
        
    Returns:
        Configured ChatOpenAI instance
        
    Cost Optimization:
        - gpt-4o-mini: ~$0.0002 per request (RECOMMENDED)
        - Low temperature: Focused responses = fewer tokens
        - Token limit: Prevents expensive long responses
        
    Example:
        >>> llm = get_llm()
        >>> # Uses gpt-4o-mini with temp=0.1, max_tokens=200
    """
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please create a .env file with your API key. "
            "See .env.example for template."
        )
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=DEFAULT_TIMEOUT,
        api_key=api_key,
    )


# ══════════════════════════════════════════════════════════════════
# MAIN FUNCTION - Analyze columns needed for requirement
# ══════════════════════════════════════════════════════════════════

async def plan_columns(
    table_name: str,
    table_schema: Dict[str, Any],
    user_requirement: str,
    verbose: bool = False
) -> ColumnPlanOutput:
    """
    Analyze user requirement and determine what columns are needed.
    
    This is the main function that:
    1. Formats the table schema for LLM
    2. Creates the prompt with user requirement
    3. Calls LLM with structured output
    4. Returns validated Pydantic model
    
    Args:
        table_name: Name of the table being analyzed
        table_schema: Schema dict from schema_registry.get_table_schema()
                     Format: {"table_name": "...", "columns": [...]}
        user_requirement: Natural language requirement from user
                         Example: "Show me average MRR by industry"
        verbose: If True, print token usage and cost estimates
        
    Returns:
        ColumnPlanOutput: Structured analysis with required/optional columns
        
    Raises:
        ValueError: If API key missing or invalid input
        Exception: If LLM call fails
        
    Example:
        >>> from app.schemas.schema_registry import get_table_schema
        >>> schema = get_table_schema("crm_customers")
        >>> result = await plan_columns(
        ...     "crm_customers",
        ...     schema,
        ...     "Show me average MRR by industry"
        ... )
        >>> print(result.required_columns)
        ['mrr', 'industry']
    """
    
    # Validate inputs
    if not table_name:
        raise ValueError("table_name cannot be empty")
    
    if not user_requirement or user_requirement.strip() == "":
        raise ValueError("user_requirement cannot be empty")
    
    if not table_schema or "columns" not in table_schema:
        raise ValueError("table_schema must contain 'columns' key")
    
    # Step 1: Format columns for prompt
    columns_formatted = format_columns_for_prompt(table_schema["columns"])
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"ANALYZING REQUIREMENT")
        print(f"{'='*60}")
        print(f"Table: {table_name}")
        print(f"Columns: {len(table_schema['columns'])}")
        print(f"Requirement: {user_requirement}")
        print(f"Model: {DEFAULT_MODEL}")
        print(f"{'='*60}\n")
    
    # Step 2: Create LLM with structured output
    llm = get_llm()
    
    # with_structured_output() tells LangChain:
    # "Parse the response and validate against ColumnPlanOutput model"
    structured_llm = llm.with_structured_output(ColumnPlanOutput)
    
    # Step 3: Create the chain (prompt → llm → validation)
    chain = COLUMN_PLANNER_PROMPT | structured_llm
    
    # Step 4: Invoke the chain
    try:
        result = await chain.ainvoke({
            "table_name": table_name,
            "columns_formatted": columns_formatted,
            "user_requirement": user_requirement
        })
        
        # Step 5: Log token usage if verbose
        if verbose:
            # Note: In production, you'd track this from the response
            # For now, we estimate based on typical usage
            estimated_input_tokens = 500 + (len(table_schema["columns"]) * 10)
            estimated_output_tokens = 150
            
            # Calculate cost (gpt-4o-mini pricing)
            input_cost = (estimated_input_tokens / 1_000_000) * 0.15
            output_cost = (estimated_output_tokens / 1_000_000) * 0.60
            total_cost = input_cost + output_cost
            
            print(f"\n{'='*60}")
            print(f"TOKEN USAGE (Estimated)")
            print(f"{'='*60}")
            print(f"Input tokens:  ~{estimated_input_tokens}")
            print(f"Output tokens: ~{estimated_output_tokens}")
            print(f"Total cost:    ~${total_cost:.6f} (${total_cost*1000:.4f} per 1000 requests)")
            print(f"{'='*60}\n")
        
        return result
        
    except Exception as e:
        # Better error messages
        if "api_key" in str(e).lower():
            raise ValueError(
                "Invalid OpenAI API key. Please check your .env file."
            ) from e
        
        raise Exception(f"LLM call failed: {str(e)}") from e


# ══════════════════════════════════════════════════════════════════
# SYNCHRONOUS WRAPPER - For non-async contexts
# ══════════════════════════════════════════════════════════════════

def plan_columns_sync(
    table_name: str,
    table_schema: Dict[str, Any],
    user_requirement: str,
    verbose: bool = False
) -> ColumnPlanOutput:
    """
    Synchronous wrapper for plan_columns().
    
    Use this if you're not in an async context.
    
    Example:
        >>> result = plan_columns_sync(
        ...     "crm_customers",
        ...     schema,
        ...     "Show me average MRR"
        ... )
    """
    import asyncio
    
    # Run the async function in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            plan_columns(table_name, table_schema, user_requirement, verbose)
        )
    finally:
        loop.close()


# ══════════════════════════════════════════════════════════════════
# USAGE EXAMPLE (for documentation)
# ══════════════════════════════════════════════════════════════════

"""
Complete usage example:

    from app.schemas.schema_registry import get_table_schema
    from app.services.column_planner import plan_columns
    
    # Get table schema
    schema = get_table_schema("crm_customers")
    
    # Analyze requirement
    result = await plan_columns(
        table_name="crm_customers",
        table_schema=schema,
        user_requirement="Show me average MRR by industry in last 6 months",
        verbose=True  # Shows token usage and cost
    )
    
    # Access structured results
    print(f"Summary: {result.technical_summary}")
    print(f"Required: {result.required_columns}")
    print(f"Optional: {result.optional_columns}")
    print(f"Assumptions: {result.assumptions}")
    
    # Cost: ~$0.0002 per request with gpt-4o-mini
"""

