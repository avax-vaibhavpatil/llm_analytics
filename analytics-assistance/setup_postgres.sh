#!/bin/bash

echo "=========================================="
echo "PostgreSQL Setup & Migration"
echo "=========================================="
echo ""

# Configuration
export PG_HOST="localhost"
export PG_PORT="5430"
export PG_DATABASE="analytics-llm"
export PG_USER="postgres"

echo "Configuration:"
echo "  Host: $PG_HOST"
echo "  Port: $PG_PORT"
echo "  Database: $PG_DATABASE"
echo "  User: $PG_USER"
echo ""

# Prompt for password
read -sp "Enter PostgreSQL password: " PG_PASSWORD
export PG_PASSWORD
echo ""
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "Checking dependencies..."
pip install -q psycopg2-binary asyncpg

# Run migration
echo ""
echo "Starting migration..."
python migrate_to_postgres.py

# Check if migration was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Migration successful!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Create/Update .env file with:"
    echo "   DATABASE_URL=postgresql+asyncpg://$PG_USER:YOUR_PASSWORD@$PG_HOST:$PG_PORT/$PG_DATABASE"
    echo ""
    echo "2. Restart your application:"
    echo "   uvicorn app.main:app --reload"
else
    echo ""
    echo "=========================================="
    echo "✗ Migration failed!"
    echo "=========================================="
    echo ""
    echo "Please check the error messages above."
fi

