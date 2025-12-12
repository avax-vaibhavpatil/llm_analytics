#!/bin/bash

echo "======================================================================"
echo "🧪 Testing FastAPI Endpoint with Factory Integration"
echo "======================================================================"
echo ""
echo "📋 Test Details:"
echo "   Endpoint: POST /api/analyze/columns"
echo "   Table: crm_customers"
echo "   Query: Show me average MRR by industry"
echo "   Provider: Determined by config.yaml"
echo ""
echo "🚀 Sending request..."
echo ""

curl -X POST http://localhost:8000/api/analyze/columns \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "crm_customers",
    "requirement": "Show me average MRR by industry"
  }' \
  -w "\n\nHTTP Status: %{http_code}\n" \
  2>&1

echo ""
echo "======================================================================"
echo "💡 Key Points:"
echo "======================================================================"
echo "✅ FastAPI now uses factory pattern"
echo "✅ Provider determined by config.yaml (currently: Groq)"
echo "✅ No hardcoded OpenAI dependency"
echo ""
echo "📝 To switch providers:"
echo "   1. Edit: analytics-assistance/config.yaml"
echo "   2. Change: llm.provider to 'openai' or 'groq'"
echo "   3. Restart: FastAPI server"
echo "   4. Run: this test again"
echo "======================================================================"

