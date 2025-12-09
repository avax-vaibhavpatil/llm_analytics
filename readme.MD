✅ Final Scope (as you defined)
Input:

User selects a table

User types analytics requirement in natural language

Output:

System returns:

What is the technical interpretation of the requirement

What columns are required

Which of them exist in table

Which are missing

Optional recommendations

No SQL. No DB execution. Only requirement → column mapping.

✅ System Architecture for Stage-1 Only
User → FastAPI → LLM (OpenAI) → Column Planner → Matches Schema → Return result

✅ Step-by-Step Development Plan (Stage-1 Only)
Step 1 — Build a schema registry

Your backend needs to know what columns exist in each table.

Tasks:

Load table schemas from your SQLite DB using SQLAlchemy.

Store them in memory at startup.

Provide a function: get_table_schema(table_name).

Output example:
{
  "table_name": "crm_customers",
  "columns": [
    {"name": "customer_id", "type": "VARCHAR"},
    {"name": "industry", "type": "VARCHAR"},
    {"name": "mrr", "type": "DECIMAL"},
    ...
  ]
}

Step 2 — Build an LLM-powered Column Planner

This module converts the user requirement into:

Technical interpretation

Required column list

Optional column list

Example Input:

"Show me average MRR by industry in last 6 months."

Example Output:
{
  "technical_summary": "Calculate average MRR, grouped by industry, filtered for customers created in the last 6 months.",
  "required_columns": ["mrr", "industry", "created_at"],
  "optional_columns": ["country", "segment"],
  "assumptions": "Used created_at as date field for filtering."
}

How it works:

You send:

The table schema

User requirement

Very strict JSON-schema instructions

to the LLM.

Step 3 — Column Matching Module

You compare:

Required columns

vs.

Actual columns in table
Tasks:

existing = {col["name"] for col in schema["columns"]}

required = set(plan["required_columns"])

Compute:

missing = required - existing

available = required ∩ existing

Output:
{
  "available_columns": ["mrr", "industry"],
  "missing_columns": ["created_at"], 
  "technical_summary": "...",
  "assumptions": "..."
}


This is the final output the user sees.

Step 4 — Build FastAPI Endpoint

Endpoint: /analyze/columns

Request:
{
  "table_name": "crm_customers",
  "requirement": "What is the average MRR by industry in the last 6 months?"
}

Response example:
{
  "technical_summary": "Calculate average MRR grouped by industry filtered for last 6 months.",
  "required_columns": ["mrr", "industry", "created_at"],
  "available_columns": ["mrr", "industry", "created_at"],
  "missing_columns": [],
  "optional_columns": ["country"],
  "assumptions": "Used created_at as the timeline filter column."
}

✅ You Now Have a Clear System Flow
1) User enters natural language
2) LLM converts to technical requirement
3) Required columns extracted
4) Compare with table schema
5) Send final column assessment to user
🔧 Technical Implementation Summary (Minimal)
Modules you'll need:
1. schema_registry.py

Load DB schema

Store table → columns

2. openai_client.py

Wrapper to call ChatGPT

3. column_planner.py

LLM logic

Parse JSON output

4. column_matcher.py

Compare required vs existing columns

5. analytics_route.py

FastAPI endpoint tying everything together

⭐ Why This Architecture Is Perfect

✔ Extremely modular
✔ Easy to build in Cursor
✔ Easy to test
✔ Scales later when you add SQL generation
✔ Full LLM explainability
✔ Safe — no SQL execution yet

🎁 If you want, next I can give you:
Option A — Full ready-to-paste codebase for Stage-1

(complete project structure in FastAPI)

Option B — Prompt engineering for highest accuracy

(good prompt = best results)

Option C — Frontend UI flow

(React/HTML)

Option D — ER Diagram + Table Summaries for each dataset

Tell me which one you want next.


# When user asks: "Show me all orders above $100"

# Step 1: LLM needs to know what tables/columns exist
available_tables = list_tables()  # ["users", "orders", ...]

# Step 2: LLM checks the schema to write correct SQL
orders_schema = get_table_schema("orders")
# LLM sees: columns are "id", "user_id", "amount", "created_at"

# Step 3: LLM generates valid SQL
sql = "SELECT * FROM orders WHERE amount > 100"


crm table

1. Show me average MRR by industry

2. Show customers by country

3. Show me customer revenue

4. Count customers by industry

5. Show me customer details

6. List all customers created this year

multivendor_orders

1. Show total sales by vendor

2. Show me all orders

3. Count orders by status

4. Show revenue by vendor

erp_purchase_orders

1. Show purchase orders by supplier

2. Count orders by status

3. Show total order amounts