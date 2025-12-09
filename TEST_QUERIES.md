# 🧪 Test Queries for LLM Analytics Assistant

> **Comprehensive list of analytics questions to test the system**  
> Use these queries to validate column mapping, LLM understanding, and data availability checks.

---

## 📋 Table of Contents

- [CRM Customers](#1️⃣-crm-customers-crm_customers)
- [E-Commerce Orders](#2️⃣-e-commerce-orders-multivendor_ecom_dataset)
- [ERP Purchase Orders](#3️⃣-erp-purchase-orders-erp_purchase_orders)
- [Social Media Analytics](#4️⃣-social-media-analytics-social_media_analytics_dataset)
- [Testing Strategy](#🎯-testing-strategy)
- [Edge Cases](#💡-edge-cases-to-test)

---

## 1️⃣ **CRM Customers** (`crm_customers`)

### ✅ Simple Queries (Level 1-2)

```
"Show me all customers"
```

```
"What is the total number of customers?"
```

```
"Count customers by country"
```

```
"List all customers in the USA"
```

```
"Show me customer names and their email addresses"
```

### ✅ Medium Queries (Level 3-4)

```
"What is the average monthly recurring revenue by industry?"
```

```
"Show me customer count by country sorted by highest to lowest"
```

```
"List all enterprise segment customers with MRR above $5000"
```

```
"Total ARR grouped by industry vertical"
```

```
"Count customers by industry and segment"
```

```
"Show customers who joined in 2024"
```

```
"Average MRR for technology industry customers"
```

```
"List top 10 customers by annual recurring revenue"
```

### 🔥 Complex Queries (Level 5)

```
"Calculate the average ARR for enterprise customers in the technology industry who joined in the last 12 months"
```

```
"Compare the total MRR between North American and European customers, grouped by industry vertical"
```

```
"Identify high-value customers (ARR > $100k) in the healthcare industry who have been with us for more than 2 years"
```

```
"What is the average customer lifetime value by signup channel and industry, filtered for active customers only?"
```

```
"Show me revenue concentration: which industries contribute to the top 80% of total ARR?"
```

```
"Calculate customer acquisition efficiency: average ARR per customer by signup source"
```

```
"Identify expansion revenue opportunities: customers with MRR growth above 20% in the last quarter"
```

```
"What percentage of total revenue comes from enterprise vs SMB vs startup segments?"
```

```
"Show customer distribution by ARR bands: 0-10k, 10k-50k, 50k-100k, 100k+"
```

```
"Calculate average revenue per employee for B2B customers in the technology sector"
```

---

## 2️⃣ **E-Commerce Orders** (`multivendor_ecom_dataset`)

### ✅ Simple Queries (Level 1-2)

```
"Show all orders"
```

```
"Count total number of orders"
```

```
"List orders by status"
```

```
"Show me all pending orders"
```

```
"Total sales amount"
```

### ✅ Medium Queries (Level 3-4)

```
"Show total sales by vendor"
```

```
"Count number of orders by status"
```

```
"List top 10 products by revenue"
```

```
"Average order value by vendor"
```

```
"Total revenue by product category"
```

```
"Count completed orders in the last 30 days"
```

```
"Show orders above $1000"
```

```
"Revenue by payment method"
```

### 🔥 Complex Queries (Level 5)

```
"Calculate average order value by vendor, excluding cancelled orders, for Q4 2024"
```

```
"Identify vendors with declining sales: compare their revenue from last month vs this month"
```

```
"What is the order fulfillment rate (completed vs total orders) by vendor and product category?"
```

```
"Show revenue breakdown by payment method, grouped by customer segment, for orders above $500"
```

```
"Calculate the average time between order placement and delivery for each vendor, filtered by region"
```

```
"Which products have the highest return rate, and what's their impact on total revenue?"
```

```
"Identify top-performing vendors: those with highest revenue, lowest cancellation rate, and best delivery time"
```

```
"Calculate vendor commission: total sales by vendor with 15% commission rate"
```

```
"Show seasonal trends: monthly revenue by product category for the last 12 months"
```

```
"What is the cart abandonment rate by customer segment and device type?"
```

---

## 3️⃣ **ERP Purchase Orders** (`erp_purchase_orders`)

### ✅ Simple Queries (Level 1-2)

```
"Show all purchase orders"
```

```
"Count total purchase orders"
```

```
"List orders by status"
```

```
"Show pending purchase orders"
```

```
"Total purchase amount"
```

### ✅ Medium Queries (Level 3-4)

```
"Show total purchase amount by supplier"
```

```
"Count orders by approval status"
```

```
"List all pending purchase orders above $10,000"
```

```
"Average order value by department"
```

```
"Total spend by cost center"
```

```
"Count approved orders in 2024"
```

```
"Show orders by priority level"
```

```
"Revenue by supplier category"
```

### 🔥 Complex Queries (Level 5)

```
"Calculate the average procurement cycle time (from requisition to delivery) by department and supplier"
```

```
"Identify suppliers with the best on-time delivery rate and compare their pricing against company average"
```

```
"What is the total spend by cost center, broken down by quarter, for IT and Operations departments?"
```

```
"Show budget utilization rate: actual spend vs approved budget by department and month"
```

```
"Which suppliers have price increases above 10% compared to last year, and what's the financial impact?"
```

```
"Calculate working capital efficiency: average payment terms by supplier category and order volume"
```

```
"Identify maverick spending: purchase orders that bypassed approval workflow or exceeded budget"
```

```
"Show supplier concentration risk: percentage of total spend by top 5 suppliers"
```

```
"Calculate cost savings: compare actual purchase price vs budgeted price by supplier and category"
```

```
"What is the average requisition-to-PO conversion time by department and urgency level?"
```

---

## 4️⃣ **Social Media Analytics** (`social_media_analytics_dataset`)

### ✅ Simple Queries (Level 1-2)

```
"Show all posts"
```

```
"Count total posts"
```

```
"List posts by platform"
```

```
"Show posts from last week"
```

```
"Total impressions"
```

### ✅ Medium Queries (Level 3-4)

```
"Show total engagement by platform"
```

```
"Count posts by content type"
```

```
"List top 10 posts by reach"
```

```
"Average engagement per post by platform"
```

```
"Total clicks by content type"
```

```
"Show video posts with over 10k views"
```

```
"Count posts by day of week"
```

```
"Revenue from paid campaigns"
```

### 🔥 Complex Queries (Level 5)

```
"Calculate engagement rate (interactions/impressions) by content type and platform, for posts published in the last 30 days"
```

```
"Identify best performing time slots: which hours generate highest engagement, grouped by platform and day of week?"
```

```
"Compare video vs image content performance: average engagement, reach, and conversion rate by platform"
```

```
"What is the ROI of paid vs organic posts? Calculate cost per engagement and reach by campaign type"
```

```
"Show audience growth velocity: new followers per day by platform, with month-over-month percentage change"
```

```
"Which influencer partnerships drive the highest engagement-to-follower ratio, and what's their content mix?"
```

```
"Calculate viral coefficient: posts with engagement rate above 10% and their content characteristics"
```

```
"Show content optimization insights: which hashtags, posting times, and formats drive highest reach?"
```

```
"What is the customer acquisition cost from social media by platform and campaign type?"
```

```
"Identify underperforming content: posts with below-average engagement despite high reach"
```

---

## 🎯 Testing Strategy

### **Phase 1: Basic Validation** (Should work 100%)

Test with simple queries first to ensure core functionality:

1. Table listing works
2. Schema detection works
3. Basic column mapping works
4. Single-column queries work

**Test with:**
- `"Show me all customers"`
- `"Count total orders"`
- `"List suppliers"`

---

### **Phase 2: Aggregation Testing** (Should work 90%+)

Test aggregation and grouping:

**Test with:**
- `"Average MRR by industry"`
- `"Total sales by vendor"`
- `"Count orders by status"`

---

### **Phase 3: Filter Testing** (Should work 85%+)

Test filtering capabilities:

**Test with:**
- `"Customers in the USA"`
- `"Orders above $1000"`
- `"Enterprise segment customers"`

---

### **Phase 4: Time-based Testing** (Should work 80%+)

Test date/time filtering:

**Test with:**
- `"Customers who joined in 2024"`
- `"Orders in the last 30 days"`
- `"Revenue in Q4 2023"`

---

### **Phase 5: Complex Logic Testing** (Should work 70%+)

Test multi-condition and complex queries:

**Test with:**
- `"Enterprise customers with MRR > $5000 in North America"`
- `"Completed orders from top 5 vendors in the last quarter"`
- `"High-value customers in technology industry who joined recently"`

---

### **Phase 6: Business Intelligence Testing** (Should work 60%+)

Test queries requiring business logic understanding:

**Test with:**
- `"Calculate customer acquisition cost by channel"`
- `"Identify churn risk customers with declining revenue"`
- `"Show supplier performance score based on delivery and pricing"`

---

## 💡 Edge Cases to Test

### **Ambiguous Queries** (Tests LLM inference)

```
"Show me revenue"
```
**Expected:** Should identify MRR, ARR, or both; might ask for clarification

```
"Best performing customers"
```
**Expected:** Should infer "best" means highest MRR or ARR

```
"Recent customers"
```
**Expected:** Should infer "recent" means last 30/60/90 days

```
"High-value accounts"
```
**Expected:** Should infer high-value based on ARR threshold or top percentile

```
"Popular products"
```
**Expected:** Should infer popular means highest sales volume or revenue

---

### **Missing Column Queries** (Tests error handling)

```
"Show me customer churn rate"
```
**Expected:** Should identify missing churn_date or status column

```
"Calculate customer lifetime value"
```
**Expected:** Might need additional columns not in table

```
"Show profit margin by product"
```
**Expected:** Needs cost column if only revenue exists

```
"Customer retention rate over time"
```
**Expected:** Needs historical or time-series data

---

### **Fuzzy Column Matching** (Tests semantic understanding)

```
"Show monthly revenue" 
```
**Expected:** Should map to MRR column

```
"List companies by sector"
```
**Expected:** Should map to "industry" column

```
"Customer email addresses"
```
**Expected:** Should map to "email" or "contact_email" column

```
"When did customers sign up?"
```
**Expected:** Should map to "created_at" or "signup_date" column

---

## 🚀 Recommended Test Flow

### **Start Here** (CRM Table - Simple)

```
1. "Show me customer count"
2. "Average MRR by industry"
3. "List customers by country"
```

### **Then Move To** (CRM Table - Medium)

```
4. "Total ARR for enterprise segment customers"
5. "Count customers who joined in 2024"
6. "Average revenue by industry and country"
```

### **Finally Try** (CRM Table - Advanced)

```
7. "Calculate customer acquisition cost efficiency by signup source"
8. "Identify expansion revenue opportunities with growing MRR trend"
9. "What percentage of total revenue comes from top 20% of customers?"
```

---

## 📊 Success Metrics

Track these metrics while testing:

- ✅ **Column Mapping Accuracy:** % of correct column identifications
- ✅ **Query Understanding:** % of queries where intent was correctly interpreted
- ✅ **Missing Column Detection:** % of accurate "column not available" responses
- ✅ **Recommendation Quality:** Usefulness of LLM suggestions for missing data
- ✅ **Response Time:** Average time from query to result
- ✅ **Cost per Query:** OpenAI API cost per request

---

## 🎯 Expected Results by Difficulty

| Level | Description | Expected Success Rate |
|-------|-------------|----------------------|
| **Level 1** | Single table, single column | **95-100%** |
| **Level 2** | Aggregation + grouping | **90-95%** |
| **Level 3** | Filters + aggregation | **85-90%** |
| **Level 4** | Multi-condition filters | **80-85%** |
| **Level 5** | Complex business logic | **70-80%** |
| **Level 6** | Advanced BI queries | **60-70%** |

---

## 📝 Testing Checklist

- [ ] Test all 4 tables with simple queries
- [ ] Test aggregation functions (COUNT, AVG, SUM)
- [ ] Test grouping by single column
- [ ] Test grouping by multiple columns
- [ ] Test filtering with comparison operators (>, <, =)
- [ ] Test date/time filtering
- [ ] Test text filtering (industry, country, etc.)
- [ ] Test queries with missing columns
- [ ] Test ambiguous queries
- [ ] Test fuzzy column name matching
- [ ] Verify recommendations for missing data
- [ ] Check LLM response consistency (run same query 3x)
- [ ] Measure API cost per query type
- [ ] Validate response times

---

## 💰 Cost Estimation

Based on `gpt-4o-mini` pricing ($0.150 per 1M input tokens):

| Query Type | Avg Tokens | Cost per Query | 1000 Queries |
|------------|-----------|----------------|--------------|
| Simple | ~500 | $0.0004 | $0.40 |
| Medium | ~800 | $0.0006 | $0.60 |
| Complex | ~1200 | $0.0009 | $0.90 |

**Total Monthly Cost Estimate (10K queries/month):** **~$6-8**

---

## 🎉 Happy Testing!

Start with simple queries and gradually increase complexity. Document which queries work well and which need improvement for future prompt engineering optimization.

**Pro Tip:** Keep track of queries where the LLM:
- ✅ Correctly identifies all columns
- ⚠️ Misses some optional columns
- ❌ Misidentifies columns
- 💡 Provides excellent recommendations

This feedback will help fine-tune the system! 🚀

