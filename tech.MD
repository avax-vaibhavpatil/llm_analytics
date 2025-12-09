┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Startup                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              load_schema(engine)                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  metadata.reflect() → Reads actual DB structure        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              SCHEMA_CACHE (in memory)                       │
│  {                                                          │
│    "users": {columns: [...]},                               │
│    "orders": {columns: [...]},                              │
│    ...                                                      │
│  }                                                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│   API Endpoints can now use:                                │
│   • list_tables() → Get all table names                     │
│   • get_table_schema("users") → Get column details          │
└─────────────────────────────────────────────────────────────











┌─────────────────────────────────────────────────────────────────┐
│ 1. SERVER STARTUP (Happens ONCE when server starts)            │
└─────────────────────────────────────────────────────────────────┘
         │
         │  FastAPI starts → @app.on_event("startup")
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. LOAD DATABASE SCHEMA (Read structure, NOT data)             │
├─────────────────────────────────────────────────────────────────┤
│  load_schema(engine)                                            │
│    ↓                                                            │
│  SQLAlchemy connects to analytics.db                            │
│    ↓                                                            │
│  metadata.reflect() reads:                                      │
│    - Table names                                                │
│    - Column names                                               │
│    - Column types (VARCHAR, INT, DECIMAL, etc.)                 │
│    - Primary keys, nullable, etc.                               │
│    ↓                                                            │
│  SCHEMA_CACHE = {                                               │
│    "crm_customers": {                                           │
│      "columns": [                                               │
│        {"name": "customer_id", "type": "VARCHAR", ...},         │
│        {"name": "mrr", "type": "DECIMAL", ...},                 │
│        {"name": "industry", "type": "VARCHAR", ...}             │
│      ]                                                          │
│    }                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
         │
         │  ⚠️ IMPORTANT: Only reads STRUCTURE, not actual data!
         │  ⚠️ Database connection closes after this.
         │  ⚠️ Everything now in memory (SCHEMA_CACHE)
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. SERVER READY (Waiting for API requests)                     │
│    Database is NO LONGER accessed                               │
└─────────────────────────────────────────────────────────────────┘
         │
         │  User makes HTTP request
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. USER REQUEST                                                 │
├─────────────────────────────────────────────────────────────────┤
│  POST /analyze/columns                                          │
│  {                                                              │
│    "table_name": "crm_customers",                               │
│    "requirement": "Show me average MRR by industry"             │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
         │
         │  No database query! Get from memory cache
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. GET SCHEMA FROM MEMORY (Fast! No DB access)                 │
├─────────────────────────────────────────────────────────────────┤
│  schema = get_table_schema("crm_customers")                     │
│  # Returns from SCHEMA_CACHE (in memory)                        │
│                                                                 │
│  schema = {                                                     │
│    "table_name": "crm_customers",                               │
│    "columns": [                                                 │
│      {"name": "customer_id", ...},                              │
│      {"name": "mrr", ...},                                      │
│      {"name": "industry", ...},                                 │
│      ... 30 more columns ...                                    │
│    ]                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
         │
         │  ⚠️ LLM NEVER sees actual data!
         │  ⚠️ LLM only sees column names and types!
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. PREPARE DATA FOR LLM                                         │
├─────────────────────────────────────────────────────────────────┤
│  Format schema into human-readable text:                        │
│                                                                 │
│  Table: crm_customers                                           │
│  Columns:                                                       │
│    - customer_id (VARCHAR, PRIMARY KEY)                         │
│    - mrr (DECIMAL, NOT NULL)                                    │
│    - industry (VARCHAR)                                         │
│    - created_at (DATETIME)                                      │
│    ... etc ...                                                  │
└─────────────────────────────────────────────────────────────────┘
         │
         │  Send to OpenAI
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. LLM ANALYSIS (OpenAI gpt-4o-mini)                           │
├─────────────────────────────────────────────────────────────────┤
│  LLM receives:                                                  │
│    - Table structure (column names/types)                       │
│    - User requirement: "Show average MRR by industry"           │
│                                                                 │
│  LLM thinks:                                                    │
│    - To calculate average → need "mrr" column ✓                 │
│    - To group by industry → need "industry" column ✓            │
│                                                                 │
│  LLM returns JSON:                                              │
│  {                                                              │
│    "technical_summary": "Calculate avg MRR grouped by industry",│
│    "required_columns": ["mrr", "industry"],                     │
│    "optional_columns": [],                                      │
│    "assumptions": "..."                                         │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
         │
         │  ⚠️ No database query happened!
         │  ⚠️ LLM used AI to understand requirement!
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. COLUMN MATCHING (Pure logic, no DB)                         │
├─────────────────────────────────────────────────────────────────┤
│  Compare LLM output with cached schema:                         │
│                                                                 │
│  Required by LLM: ["mrr", "industry"]                           │
│  Available in table: ["customer_id", "mrr", "industry", ...]    │
│                                                                 │
│  Set operations:                                                │
│    available = {"mrr", "industry"} ✓                            │
│    missing = {} ✓                                               │
│                                                                 │
│  Result: All columns exist!                                     │
└─────────────────────────────────────────────────────────────────┘
         │
         │  Generate recommendations
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ 9. FINAL RESPONSE TO USER                                       │
├─────────────────────────────────────────────────────────────────┤
│  {                                                              │
│    "technical_summary": "Calculate avg MRR grouped by industry",│
│    "required_columns": ["mrr", "industry"],                     │
│    "available_columns": ["mrr", "industry"],  ← NEW!            │
│    "missing_columns": [],                     ← NEW!            │
│    "optional_columns": [],                                      │
│    "assumptions": "...",                                        │
│    "recommendations": [                                         │
│      "✅ All required columns available",                        │
│      "Analysis can proceed"                                     │
│    ]                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘