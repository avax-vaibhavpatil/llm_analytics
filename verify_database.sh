#!/bin/bash
# Verify admin requests were saved to database

echo "🔍 Checking admin_report_requests table..."
echo "=========================================="
echo ""

PGPASSWORD=root psql -h localhost -p 5430 -U postgres -d analytics-llm -c "
SELECT 
    request_id,
    request_title,
    request_type,
    status,
    created_at
FROM metadata.admin_report_requests
ORDER BY request_id DESC
LIMIT 10;
"

echo ""
echo "To see full details of a specific request:"
echo "PGPASSWORD=root psql -h localhost -p 5430 -U postgres -d analytics-llm -c \"SELECT * FROM metadata.admin_report_requests WHERE request_id = <ID>;\""

