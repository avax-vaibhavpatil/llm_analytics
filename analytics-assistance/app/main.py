"""
FastAPI Application - Analytics Assistant

Main application entry point that wires everything together.

Startup Flow:
1. FastAPI app initializes
2. Lifespan event loads database schemas into memory
3. App is ready to handle requests
4. Routes process user requirements with LLM
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine
from app.schemas.schema_registry import load_schema, list_tables
from app.routes import analytics


# ══════════════════════════════════════════════════════════════════
# LIFESPAN MANAGEMENT - Startup and Shutdown Events
# ══════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    
    This runs:
    - BEFORE: Server starts accepting requests (startup)
    - AFTER: Server stops (shutdown)
    
    Startup tasks:
    - Load all database schemas into memory (SCHEMA_CACHE)
    - This happens ONCE when server starts
    - Makes subsequent requests fast (no repeated DB queries)
    
    Shutdown tasks:
    - Close database connections
    - Cleanup resources
    """
    
    # ═══════════════════════════════════════════════════════════
    # STARTUP
    # ═══════════════════════════════════════════════════════════
    print("=" * 70)
    print("🚀 Starting Analytics Assistant API...")
    print("=" * 70)
    
    # Load database schemas into memory
    print("\n📦 Loading database schemas...")
    await load_schema(engine)
    
    tables = list_tables()
    print(f"✅ Loaded {len(tables)} tables into cache:")
    for table in tables:
        print(f"   - {table}")
    
    print("\n" + "=" * 70)
    print("✅ Server ready to accept requests!")
    print("=" * 70)
    print("\n📚 API Documentation:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\n💰 Cost per analysis: ~$0.0002 (0.02 cents)")
    print("=" * 70 + "\n")
    
    yield  # Server runs and handles requests here
    
    # ═══════════════════════════════════════════════════════════
    # SHUTDOWN
    # ═══════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("🛑 Shutting down Analytics Assistant API...")
    print("=" * 70)
    
    # Close database connection
    await engine.dispose()
    print("✅ Database connection closed")
    
    print("=" * 70)
    print("👋 Goodbye!")
    print("=" * 70 + "\n")


# ══════════════════════════════════════════════════════════════════
# CREATE FASTAPI APP
# ══════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Analytics Assistant API",
    description="""
    🤖 AI-Powered Analytics Column Analyzer
    
    This API helps you understand what database columns are needed for analytics requirements.
    
    ## Features
    
    * 🧠 **LLM-Powered Analysis**: Uses GPT-4o-mini to understand natural language
    * ⚡ **Fast**: Schemas cached in memory, responses in 1-2 seconds
    * 💰 **Cheap**: ~$0.0002 per analysis (0.02 cents)
    * ✅ **Smart Matching**: Fuzzy matching handles imprecise requirements
    * 📊 **Complete Output**: Technical summary, required/missing columns, recommendations
    
    ## Usage
    
    1. **List Tables**: `GET /tables`
    2. **Get Schema**: `GET /tables/{table_name}/schema`
    3. **Analyze Requirement**: `POST /analyze/columns`
    
    ## Example
    
    ```json
    POST /analyze/columns
    {
      "table_name": "crm_customers",
      "requirement": "Show me average MRR by industry"
    }
    ```
    
    Returns:
    ```json
    {
      "technical_summary": "Calculate average MRR grouped by industry",
      "required_columns": ["mrr", "industry"],
      "available_columns": ["mrr", "industry"],
      "missing_columns": [],
      "recommendations": ["✅ All columns available"]
    }
    ```
    """,
    version="1.0.0",
    lifespan=lifespan,  # ← Startup/shutdown events
    docs_url="/docs",
    redoc_url="/redoc"
)


# ══════════════════════════════════════════════════════════════════
# MIDDLEWARE - CORS for frontend integration
# ══════════════════════════════════════════════════════════════════

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════════
# INCLUDE ROUTERS - Wire up endpoints
# ══════════════════════════════════════════════════════════════════

app.include_router(
    analytics.router,
    prefix="/api",
    tags=["Analytics"]
)


# ══════════════════════════════════════════════════════════════════
# ROOT ENDPOINT - Health check
# ══════════════════════════════════════════════════════════════════

@app.get("/", tags=["Health"])
async def root():
    """
    Health check endpoint.
    
    Returns basic info about the API.
    """
    return {
        "service": "Analytics Assistant API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "list_tables": "GET /api/tables",
            "get_schema": "GET /api/tables/{table_name}/schema",
            "analyze": "POST /api/analyze/columns"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Detailed health check.
    
    Checks if schemas are loaded and system is ready.
    """
    tables = list_tables()
    
    return {
        "status": "healthy",
        "schemas_loaded": len(tables) > 0,
        "tables_count": len(tables),
        "tables": tables
    }


# ══════════════════════════════════════════════════════════════════
# RUN SERVER (for development)
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (dev only)
        log_level="info"
    )

