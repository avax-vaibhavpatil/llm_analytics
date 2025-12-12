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
import asyncio
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.output_parsers import PydanticOutputParser

from app.models.llm_models import ColumnPlanOutput
from app.services.prompts import COLUMN_PLANNER_PROMPT, format_columns_for_prompt

# Import our factory (NEW!)
from llm.model_factory import ModelProvider_from_yaml

# Load environment variables from .env file
load_dotenv()


# ══════════════════════════════════════════════════════════════════
# CONFIGURATION - Provider-agnostic LLM setup
# ══════════════════════════════════════════════════════════════════

# Path to config file
CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"

def get_llm():
    """
    Get LLM instance from configuration.
    
    This function now uses the Model Factory to create providers!
    The provider is determined by config.yaml, not hardcoded.
    
    Returns:
        BaseProvider instance (OpenAI, Groq, or any configured provider)
    
    Example:
        >>> llm = get_llm()
        >>> # Uses provider from config.yaml
        >>> # Could be OpenAI, Groq, Anthropic, etc.!
    
    To switch providers:
        1. Edit config.yaml
        2. Change 'provider' field
        3. Restart app
        4. Done! (no code changes)
    
    Current provider is determined by config.yaml:
        llm:
          provider: groq  ← Change this to switch!
          model: llama-3.3-70b-versatile
    """
    try:
        # Load provider from config.yaml
        # This automatically:
        # 1. Reads config.yaml
        # 2. Gets provider name (e.g., "groq")
        # 3. Creates the right provider class
        # 4. Returns initialized instance
        return ModelProvider_from_yaml(str(CONFIG_PATH))
    
    except FileNotFoundError:
        # Fallback if config.yaml missing
        print("⚠️  config.yaml not found, using environment variables")
        from llm.model_factory import ModelProvider
        provider = os.getenv("LLM_PROVIDER", "groq")
        return ModelProvider(provider)
    
    except Exception as e:
        raise Exception(f"Failed to initialize LLM provider: {str(e)}") from e


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
    
    # Step 2: Get LLM instance from factory
    llm = get_llm()
    
    if verbose:
        config = llm.get_config()
        print(f"\n{'='*60}")
        print(f"ANALYZING REQUIREMENT")
        print(f"{'='*60}")
        print(f"Table: {table_name}")
        print(f"Columns: {len(table_schema['columns'])}")
        print(f"Requirement: {user_requirement}")
        print(f"Provider: {config['provider']}")  # ← Now shows actual provider!
        print(f"Model: {config['model']}")
        print(f"{'='*60}\n")
    
    # Step 3: Create the prompt with Pydantic parser instructions
    parser = PydanticOutputParser(pydantic_object=ColumnPlanOutput)
    
    # Format the prompt with all inputs
    prompt_text = COLUMN_PLANNER_PROMPT.format(
        table_name=table_name,
        columns_formatted=columns_formatted,
        user_requirement=user_requirement,
        format_instructions=parser.get_format_instructions()
    )
    
    # Step 4: Call LLM (works with ANY provider!)
    try:
        # Our providers use sync generate() method
        # Run it in a thread pool to avoid blocking the event loop
        response = await asyncio.to_thread(llm.generate, prompt_text)
        
        # Step 5: Parse and validate the response
        result = parser.parse(response)
        
        # Step 6: Log provider info if verbose
        if verbose:
            print(f"\n{'='*60}")
            print(f"RESPONSE RECEIVED")
            print(f"{'='*60}")
            print(f"Provider: {config['provider']}")
            print(f"Model: {config['model']}")
            print(f"Response length: {len(response)} chars")
            print(f"{'='*60}\n")
        
        return result
        
    except Exception as e:
        # Better error messages (provider-agnostic!)
        if "api_key" in str(e).lower() or "invalid" in str(e).lower():
            raise ValueError(
                f"API authentication failed: {str(e)}"
            ) from e
        
        if "rate_limit" in str(e).lower():
            raise ValueError(
                f"Rate limit exceeded. Please wait or upgrade your plan."
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

