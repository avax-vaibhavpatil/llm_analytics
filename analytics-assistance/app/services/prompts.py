"""
LLM Prompt Templates

This module contains carefully crafted prompts for the LLM.
Good prompts = Better results!

Prompt Engineering Principles Used:
1. Clear role definition - "You are an expert..."
2. Specific constraints - "Only use columns that exist..."
3. Output format definition - "Return JSON with these fields..."
4. Examples - Show what good output looks like
5. Step-by-step reasoning - Help LLM think through the problem

How this works with LangChain:
- ChatPromptTemplate creates a reusable template
- Placeholders like {table_name} get filled at runtime
- Template is passed to LLM chain
- LLM receives formatted prompt and responds
"""

from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict


# ══════════════════════════════════════════════════════════════════
# SYSTEM PROMPT - Defines the LLM's role and behavior
# ══════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are an expert database column analyzer specializing in business intelligence and analytics.

Your role is to analyze user requirements and determine:
1. What columns are REQUIRED (absolutely necessary)
2. What columns are OPTIONAL (would enhance analysis)
3. Any assumptions you made in your interpretation

Core Principles:
- Be precise: Only suggest columns that actually exist in the provided schema
- Be practical: Focus on what's needed, not what's nice-to-have
- Be explicit: State your assumptions clearly
- Be technical: Use proper database terminology

Column Selection Rules:
- REQUIRED columns: Without these, the analysis cannot be performed
- OPTIONAL columns: These add context, enable filtering, or provide insights
- Only return column names that exist in the provided table schema
- Use exact column names (case-sensitive, no modifications)

Output Format:
- Return valid JSON matching the specified structure
- Ensure all column names are spelled exactly as they appear in the schema
- Be concise but informative in explanations
"""


# ══════════════════════════════════════════════════════════════════
# USER PROMPT TEMPLATE - The actual analysis request
# ══════════════════════════════════════════════════════════════════

USER_PROMPT_TEMPLATE = """Analyze the following analytics requirement and determine what database columns are needed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TABLE INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Table Name: {table_name}

Available Columns:
{columns_formatted}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USER'S ANALYTICS REQUIREMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"{user_requirement}"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Understand what the user wants to accomplish
Step 2: Identify which columns are absolutely required
Step 3: Identify which columns would enhance the analysis (optional)
Step 4: Note any assumptions you made in your interpretation

Return your analysis in this exact JSON format:
{{
  "technical_summary": "A clear technical interpretation of what analysis is needed",
  "required_columns": ["list", "of", "required", "column", "names"],
  "optional_columns": ["list", "of", "optional", "column", "names"],
  "assumptions": "Any assumptions you made about the requirement"
}}

Remember:
- Only use columns from the "Available Columns" list above
- Use exact column names as shown
- Be specific in your technical summary
- Clearly explain your assumptions
"""


# ══════════════════════════════════════════════════════════════════
# LANGCHAIN CHAT PROMPT TEMPLATE
# ══════════════════════════════════════════════════════════════════

COLUMN_PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", USER_PROMPT_TEMPLATE)
])

"""
This ChatPromptTemplate object will be used like this:

    prompt = COLUMN_PLANNER_PROMPT.invoke({
        "table_name": "crm_customers",
        "columns_formatted": "- customer_id (VARCHAR)\n- mrr (DECIMAL)\n...",
        "user_requirement": "Show me average MRR by industry"
    })
    
    # prompt is now ready to send to LLM!
"""


# ══════════════════════════════════════════════════════════════════
# HELPER FUNCTION - Format columns nicely for the prompt
# ══════════════════════════════════════════════════════════════════

def format_columns_for_prompt(columns: List[Dict]) -> str:
    """
    Convert column list from schema registry into human-readable format.
    
    Input format (from schema_registry.get_table_schema()):
    [
        {"name": "customer_id", "type": "VARCHAR", "nullable": True, "primary_key": True},
        {"name": "mrr", "type": "DECIMAL(10,2)", "nullable": False, "primary_key": False},
        ...
    ]
    
    Output format (for LLM prompt):
    - customer_id (VARCHAR, PRIMARY KEY)
    - mrr (DECIMAL(10,2), NOT NULL)
    - industry (VARCHAR)
    
    Args:
        columns: List of column dictionaries from schema registry
        
    Returns:
        Formatted string with one column per line
        
    Example:
        >>> cols = [{"name": "id", "type": "INT", "nullable": False, "primary_key": True}]
        >>> format_columns_for_prompt(cols)
        '- id (INT, PRIMARY KEY, NOT NULL)'
    """
    formatted_lines = []
    
    for col in columns:
        # Start with basic format: "- name (type"
        line = f"- {col['name']} ({col['type']}"
        
        # Add tags for special properties
        tags = []
        
        if col.get('primary_key'):
            tags.append("PRIMARY KEY")
        
        if not col.get('nullable', True):
            tags.append("NOT NULL")
        
        # Add tags if any exist
        if tags:
            line += ", " + ", ".join(tags)
        
        line += ")"
        formatted_lines.append(line)
    
    return "\n".join(formatted_lines)


# ══════════════════════════════════════════════════════════════════
# EXAMPLE USAGE (for documentation)
# ══════════════════════════════════════════════════════════════════

"""
How to use this in your code:

    from app.services.prompts import COLUMN_PLANNER_PROMPT, format_columns_for_prompt
    from app.schemas.schema_registry import get_table_schema
    
    # 1. Get table schema
    schema = get_table_schema("crm_customers")
    
    # 2. Format columns for prompt
    columns_text = format_columns_for_prompt(schema["columns"])
    
    # 3. Create the prompt
    prompt = COLUMN_PLANNER_PROMPT.invoke({
        "table_name": "crm_customers",
        "columns_formatted": columns_text,
        "user_requirement": "Show me average MRR by industry"
    })
    
    # 4. Send to LLM (next step - column_planner.py)
    # result = llm.invoke(prompt)
"""

