-- ========================================
-- Metadata Tables - Example Queries
-- ========================================

-- ========================================
-- 1. GENERATED REPORTS
-- ========================================

-- Log a new generated report
INSERT INTO metadata.generated_reports (
    report_name, report_type, user_id, user_email,
    query_text, data_source, table_name, 
    columns_used, row_count, execution_time_ms,
    status
) VALUES (
    'Monthly Sales Report',
    'sales_analysis',
    'user_123',
    'john@example.com',
    'Show me total sales by vendor for last month',
    'multivendor_orders',
    'multivendor_orders',
    ARRAY['vendor_name', 'total_price', 'order_date'],
    1500,
    2340,
    'completed'
);

-- Get all reports generated in last 7 days
SELECT 
    report_name,
    user_email,
    table_name,
    row_count,
    created_at
FROM metadata.generated_reports
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY created_at DESC;

-- Get top users by report count
SELECT 
    user_email,
    COUNT(*) as report_count,
    AVG(execution_time_ms) as avg_execution_time
FROM metadata.generated_reports
WHERE status = 'completed'
GROUP BY user_email
ORDER BY report_count DESC
LIMIT 10;


-- ========================================
-- 2. USER ACTIVITY LOGS
-- ========================================

-- Log user activity
INSERT INTO metadata.user_activity_logs (
    user_id, user_email, session_id,
    activity_type, activity_description,
    page_url, action, ip_address,
    device_type, browser, success
) VALUES (
    'user_123',
    'john@example.com',
    'session_abc123',
    'report_generation',
    'Generated sales analysis report',
    '/reports/create',
    'generate_report',
    '192.168.1.100',
    'desktop',
    'Chrome',
    true
);

-- Get user activity for specific user
SELECT 
    activity_type,
    activity_description,
    timestamp,
    success
FROM metadata.user_activity_logs
WHERE user_email = 'john@example.com'
ORDER BY timestamp DESC
LIMIT 50;

-- Get activity summary by type
SELECT 
    activity_type,
    COUNT(*) as total_activities,
    COUNT(*) FILTER (WHERE success = true) as successful,
    COUNT(*) FILTER (WHERE success = false) as failed
FROM metadata.user_activity_logs
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY activity_type
ORDER BY total_activities DESC;


-- ========================================
-- 3. QUERY MATCHING LOGS
-- ========================================

-- Log a matched query
INSERT INTO metadata.query_matching_logs (
    user_id, user_query, query_intent,
    required_columns, matched_table,
    match_status, match_confidence,
    llm_model, processing_time_ms, success
) VALUES (
    'user_123',
    'Show me customers by industry',
    'Customer segmentation analysis',
    ARRAY['industry', 'customer_id'],
    'crm_customers',
    'matched',
    95.5,
    'gpt-4o-mini',
    850,
    true
);

-- Log a non-matched query
INSERT INTO metadata.query_matching_logs (
    user_id, user_query, query_intent,
    required_columns, missing_columns,
    match_status, match_confidence,
    alternative_suggestions, success
) VALUES (
    'user_456',
    'Show me product inventory levels',
    'Inventory analysis',
    ARRAY['product_id', 'inventory_level'],
    ARRAY['inventory_level'],
    'not_matched',
    25.0,
    ARRAY['Try: Show me products by category', 'Available: Show me purchase orders'],
    false
);

-- Get matching success rate
SELECT 
    match_status,
    COUNT(*) as query_count,
    ROUND(AVG(match_confidence), 2) as avg_confidence,
    ROUND(AVG(processing_time_ms), 2) as avg_processing_ms
FROM metadata.query_matching_logs
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY match_status
ORDER BY query_count DESC;

-- Get most common non-matched queries
SELECT 
    user_query,
    COUNT(*) as attempt_count,
    MAX(created_at) as last_attempted
FROM metadata.query_matching_logs
WHERE match_status = 'not_matched'
GROUP BY user_query
ORDER BY attempt_count DESC
LIMIT 20;

-- Get missing columns analysis
SELECT 
    unnest(missing_columns) as missing_column,
    COUNT(*) as times_missing
FROM metadata.query_matching_logs
WHERE match_status = 'not_matched'
    AND missing_columns IS NOT NULL
GROUP BY missing_column
ORDER BY times_missing DESC;


-- ========================================
-- 4. ADMIN REPORT REQUESTS
-- ========================================

-- Submit a new report request
INSERT INTO metadata.admin_report_requests (
    requester_user_id, requester_email, requester_name,
    request_title, request_description,
    request_type, business_justification,
    required_data_sources, priority
) VALUES (
    'user_789',
    'manager@example.com',
    'Jane Manager',
    'Customer Lifetime Value Report',
    'Need a comprehensive report showing customer lifetime value analysis with cohort breakdowns',
    'analytics_report',
    'Critical for quarterly business review and customer retention strategy',
    ARRAY['crm_customers', 'multivendor_orders'],
    'high'
);

-- Get all pending requests
SELECT 
    request_id,
    requester_name,
    request_title,
    priority,
    created_at
FROM metadata.admin_report_requests
WHERE status = 'pending'
ORDER BY 
    CASE priority
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    created_at ASC;

-- Approve a request
UPDATE metadata.admin_report_requests
SET 
    status = 'approved',
    assigned_to = 'admin_john',
    approval_notes = 'Approved for Q1 implementation',
    approved_at = CURRENT_TIMESTAMP
WHERE request_id = 1;

-- Get request statistics
SELECT 
    status,
    priority,
    COUNT(*) as request_count
FROM metadata.admin_report_requests
GROUP BY status, priority
ORDER BY status, priority;


-- ========================================
-- COMBINED ANALYTICS QUERIES
-- ========================================

-- Get complete user analytics
SELECT 
    u.user_email,
    COUNT(DISTINCT u.activity_id) as total_activities,
    COUNT(DISTINCT r.report_id) as reports_generated,
    COUNT(DISTINCT q.query_log_id) as queries_made,
    COUNT(DISTINCT q.query_log_id) FILTER (WHERE q.match_status = 'matched') as successful_queries
FROM metadata.user_activity_logs u
LEFT JOIN metadata.generated_reports r ON u.user_email = r.user_email
LEFT JOIN metadata.query_matching_logs q ON u.user_id = q.user_id
WHERE u.timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY u.user_email
ORDER BY total_activities DESC;

-- Get system health metrics
SELECT 
    'Total Reports' as metric,
    COUNT(*) as value
FROM metadata.generated_reports
WHERE created_at >= CURRENT_DATE - INTERVAL '24 hours'

UNION ALL

SELECT 
    'Query Match Rate',
    ROUND(
        COUNT(*) FILTER (WHERE match_status = 'matched')::numeric / 
        NULLIF(COUNT(*), 0) * 100, 
        2
    )
FROM metadata.query_matching_logs
WHERE created_at >= CURRENT_DATE - INTERVAL '24 hours'

UNION ALL

SELECT 
    'Active Users',
    COUNT(DISTINCT user_id)
FROM metadata.user_activity_logs
WHERE timestamp >= CURRENT_DATE - INTERVAL '24 hours';

