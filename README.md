# 🤖 LLM Analytics Assistant

> **Natural Language → Analytics Reports**  
> A full-stack application that converts user queries into data insights using LLM-powered column analysis.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Cost Optimization](#cost-optimization)

---

## 🎯 Overview

This project enables **non-technical users** to generate analytics reports by simply describing what they want in plain English.

**User Input:**  
> "Show me average MRR by industry for customers created in the last 6 months"

**System Output:**
- ✅ Technical interpretation
- ✅ Required columns identified
- ✅ Data availability check
- ✅ Missing columns flagged
- ✅ Recommendations provided
- ✅ Interactive report preview
- ✅ CSV export

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                     (React + Material-UI)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Schema     │  │     LLM      │  │   Column     │         │
│  │   Registry   │─→│   Planner    │─→│   Matcher    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ SQLAlchemy
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    SQLite Database                              │
│   (CRM, ERP, E-commerce, Social Media datasets)                │
└─────────────────────────────────────────────────────────────────┘
```

**Flow:**
1. User selects a table and enters a natural language query
2. FastAPI routes the request to the LLM Planner
3. LLM analyzes the query and identifies required columns
4. Column Matcher compares required vs. available columns
5. Results returned to frontend with recommendations
6. User can preview data, adjust columns, and generate reports

---

## 📁 Project Structure

```
llm-analytics/                      # MONOREPO ROOT
│
├── analytics-assistance/           # BACKEND (FastAPI)
│   ├── app/
│   │   ├── db.py                   # Database connection
│   │   ├── main.py                 # FastAPI app & startup
│   │   ├── models/
│   │   │   └── llm_models.py       # Pydantic models for LLM I/O
│   │   ├── routes/
│   │   │   ├── analytics.py        # API endpoints
│   │   │   └── schema.py           # Request/Response models
│   │   ├── schemas/
│   │   │   └── schema_registry.py  # DB schema caching
│   │   └── services/
│   │       ├── column_matcher.py   # Column comparison logic
│   │       ├── column_planner.py   # LLM integration
│   │       └── prompts.py          # LangChain prompts
│   ├── data/
│   │   ├── analytics.db            # SQLite database
│   │   └── *.sql                   # Sample datasets
│   ├── .env.example                # Environment variable template
│   ├── requirements.txt            # Python dependencies
│   ├── README.md                   # Backend-specific docs
│   └── SETUP_API_KEY.md            # OpenAI setup guide
│
├── analytics-ui/                   # FRONTEND (React)
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js                  # Main app with routing
│   │   ├── index.js                # React entry point
│   │   ├── components/
│   │   │   └── Sidebar.js          # Navigation sidebar
│   │   ├── pages/
│   │   │   ├── HomePage.js         # Dashboard & query input
│   │   │   ├── ProcessingPage.js   # Loading & LLM analysis
│   │   │   ├── AvailabilityPage.js # Data availability check
│   │   │   ├── PreviewPage.js      # Report preview & editing
│   │   │   └── ReportPage.js       # Final report & CSV export
│   │   ├── services/
│   │   │   └── api.js              # Axios API client
│   │   ├── utils/
│   │   │   ├── mockData.js         # Mock data generator
│   │   │   └── csvExport.js        # CSV export utility
│   │   └── styles/
│   │       └── theme.js            # Material-UI theme
│   └── package.json                # Node dependencies
│
├── .gitignore                      # Git ignore rules
├── QUICKSTART.md                   # Quick start commands
└── README.md                       # This file
```

---

## ✨ Features

### ✅ MVP Features (Implemented)

**Backend:**
- 🔌 FastAPI REST API with async SQLAlchemy
- 🧠 LangChain + OpenAI GPT-4o-mini integration
- 📊 Automatic database schema discovery
- 🎯 Natural language → column mapping
- ✔️ Data availability verification
- 💡 Smart recommendations for missing data
- 💰 Cost-optimized LLM usage (< $0.01 per request)

**Frontend:**
- 🏠 Dashboard with stats and recent reports
- 📝 Natural language query input
- ⏳ Real-time processing feedback
- 🔍 Data availability visualization
- 📋 Interactive report preview
- ✏️ Column selection/deselection
- 📥 CSV export functionality
- 🎨 Material-UI modern design

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI 0.123+
- **Database:** SQLite with SQLAlchemy (async)
- **LLM:** LangChain + OpenAI (gpt-4o-mini)
- **Validation:** Pydantic
- **Server:** Uvicorn

### Frontend
- **Framework:** React 18+
- **UI Library:** Material-UI (MUI) v5
- **HTTP Client:** Axios
- **Routing:** React Router v6
- **State Management:** React Hooks (useState, useEffect)

### DevOps
- **Version Control:** Git (Monorepo)
- **Package Management:** pip (backend), npm (frontend)
- **Environment:** Python 3.12+, Node.js 16+

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.12+ (`python --version`)
- Node.js 16+ (`node --version`)
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### 1. Clone Repository

```bash
git clone git@github.com:avax-vaibhavpatil/llm_analytics.git
cd llm-analytics
```

### 2. Backend Setup

```bash
cd analytics-assistance

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY

# Load database (if needed)
python data/load_sql_file.py
```

### 3. Frontend Setup

```bash
cd ../analytics-ui

# Install dependencies
npm install
```

---

## ⚡ Quick Start

See [`QUICKSTART.md`](./QUICKSTART.md) for simple commands.

### Start Backend

```bash
cd analytics-assistance
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **URL:** http://localhost:8000
- **Docs:** http://localhost:8000/docs

### Start Frontend

```bash
cd analytics-ui
npm start
```

- **URL:** http://localhost:3000

### Access Application

Open browser: **http://localhost:3000**

---

## 📚 API Documentation

### Base URL: `http://localhost:8000/api`

#### 1. **List Tables**
```http
GET /tables
```

**Response:**
```json
{
  "tables": [
    {"name": "crm_customers", "columns_count": 11},
    {"name": "erp_purchase_orders", "columns_count": 9}
  ]
}
```

#### 2. **Get Table Schema**
```http
GET /tables/{table_name}/schema
```

**Response:**
```json
{
  "table_name": "crm_customers",
  "columns": [
    {"name": "customer_id", "type": "VARCHAR", "nullable": false, "primary_key": true},
    {"name": "mrr", "type": "DECIMAL", "nullable": true, "primary_key": false}
  ]
}
```

#### 3. **Analyze Columns (Main Endpoint)**
```http
POST /analyze/columns
Content-Type: application/json

{
  "table_name": "crm_customers",
  "requirement": "Show me average MRR by industry"
}
```

**Response:**
```json
{
  "technical_summary": "Calculate average monthly recurring revenue grouped by industry sector",
  "required_columns": ["mrr", "industry"],
  "available_columns": ["mrr", "industry"],
  "missing_columns": [],
  "optional_columns": ["country", "segment"],
  "assumptions": "Used 'industry' as the grouping dimension",
  "recommendations": [],
  "analysis_complete": true
}
```

---

## 💰 Cost Optimization

### Current Settings (in `.env`)

```bash
OPENAI_MODEL=gpt-4o-mini          # Cheapest model ($0.150 per 1M input tokens)
OPENAI_TEMPERATURE=0.1            # Low randomness for consistency
OPENAI_MAX_TOKENS=200             # Limit response length
```

### Cost Analysis

| Model | Input Cost | Output Cost | Avg Request Cost |
|-------|------------|-------------|------------------|
| **gpt-4o-mini** | $0.150 / 1M tokens | $0.600 / 1M tokens | **< $0.01** |
| gpt-4o | $2.50 / 1M tokens | $10.00 / 1M tokens | ~$0.05 |
| gpt-3.5-turbo | $0.50 / 1M tokens | $1.50 / 1M tokens | ~$0.02 |

**Estimated Monthly Cost (1000 queries):** **< $5**

---

## 🧪 Testing

### Backend Health Check

```bash
curl http://localhost:8000/health
```

### Test API Endpoint

```bash
curl -X POST http://localhost:8000/api/analyze/columns \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "crm_customers",
    "requirement": "Show me customer count by country"
  }'
```

### Frontend Flow Test

1. Open http://localhost:3000
2. Select `crm_customers` table
3. Enter: `"Show me average MRR by industry"`
4. Click **Analyze**
5. Navigate through all screens
6. Download CSV on final report

---

## 📝 Contributing

This is a private project. For questions, contact: **avax-vaibhavpatil**

---

## 📄 License

Proprietary - All rights reserved.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT models
- **LangChain** for LLM orchestration
- **FastAPI** for backend framework
- **Material-UI** for React components

---

## 🆘 Support

For issues or questions:
1. Check `SETUP_API_KEY.md` for API key setup
2. Check `QUICKSTART.md` for running the app
3. Check backend logs in terminal
4. Check frontend browser console

---

**🎉 Happy Analyzing! 📊**

