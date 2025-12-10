# 🤖 Analytics Assistant API

AI-powered analytics column analyzer using LLM to understand natural language requirements and match them with database schemas.

## 🎯 What It Does

Analyzes natural language analytics requirements and determines:
- ✅ Technical interpretation of the requirement
- ✅ Required database columns
- ✅ Which columns exist in the table
- ✅ Which columns are missing
- ✅ Smart recommendations

## 🚀 Features

- 🧠 **LLM-Powered**: Uses OpenAI GPT-4o-mini for semantic understanding
- ⚡ **Fast**: Schema cached in memory, responses in 1-2 seconds
- 💰 **Cost-Efficient**: ~$0.0002 per request (0.02 cents)
- 🎯 **Smart Matching**: Handles fuzzy/imprecise requirements
- 📊 **Complete Output**: Technical summary, column analysis, recommendations

## 🏗️ Tech Stack

- **Framework**: FastAPI (Python)
- **LLM**: LangChain + OpenAI
- **Database**: PostgreSQL with async SQLAlchemy
- **Language**: Python 3.12+

## 📦 Project Structure

```
analytics-assistance/
├── app/
│   ├── main.py                     # FastAPI app
│   ├── db.py                       # Database engine
│   ├── models/
│   │   └── llm_models.py          # Pydantic models for LLM
│   ├── schemas/
│   │   └── schema_registry.py     # Database schema cache
│   ├── services/
│   │   ├── prompts.py             # LLM prompt templates
│   │   ├── column_planner.py      # LLM analysis logic
│   │   └── column_matcher.py      # Column comparison logic
│   └── routes/
│       ├── schema.py              # API request/response models
│       └── analytics.py           # API endpoints
├── data/
│   ├── backup/                    # SQLite backups (archived)
│   └── *.sql                      # Dataset SQL files
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd analytics-assistance
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

Required variables:
```bash
# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5430/analytics-llm

# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=200
```

### 5. Run the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server will start at: http://localhost:8000

## 📚 API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### List Tables
```http
GET /api/tables
```

Returns all available database tables.

### Get Table Schema
```http
GET /api/tables/{table_name}/schema
```

Returns detailed schema for a specific table.

### Analyze Requirement (Main Endpoint)
```http
POST /api/analyze/columns
Content-Type: application/json

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
  "optional_columns": ["country"],
  "recommendations": ["✅ All columns available"],
  "analysis_complete": true
}
```

## 💡 Usage Example

### Using cURL:

```bash
curl -X POST http://localhost:8000/api/analyze/columns \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "crm_customers",
    "requirement": "Show me average MRR by industry for customers created in last 6 months"
  }'
```

### Using Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/analyze/columns",
    json={
        "table_name": "crm_customers",
        "requirement": "Show me average MRR by industry"
    }
)

result = response.json()
print(f"Required columns: {result['required_columns']}")
print(f"Available: {result['available_columns']}")
print(f"Missing: {result['missing_columns']}")
```

## 🎯 Example Queries

| Query | Table | Result |
|-------|-------|--------|
| "Show average MRR by industry" | crm_customers | ✅ mrr, industry |
| "Orders in last 6 months" | orders | ⚠️ Needs created_at |
| "Revenue by vendor" | multivendor_orders | ✅ All available |

## 💰 Cost Information

- **Model**: gpt-4o-mini
- **Cost per request**: ~$0.0002 (0.02 cents)
- **Monthly estimates**:
  - 100 requests: $0.02
  - 1,000 requests: $0.20
  - 10,000 requests: $2.00

## 🔒 Security Notes

- ⚠️ **Never commit `.env` file** (contains API keys!)
- ✅ Use `.env.example` as a template
- ✅ Keep your OpenAI API key private
- ✅ Add rate limiting for production use

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Module Not Found
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Connection Error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Test connection
python -c "from app.db import engine; print(engine.url)"
```

## 🚀 Deployment

### Docker (Coming Soon)
```bash
docker build -t analytics-assistant .
docker run -p 8000:8000 analytics-assistant
```

### Cloud Platforms
- **AWS**: Elastic Beanstalk, ECS, or Lambda
- **GCP**: Cloud Run or App Engine
- **Heroku**: Direct deploy with Procfile

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- OpenAI for GPT-4o-mini
- LangChain for LLM orchestration
- FastAPI for the amazing framework

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Contact: your-email@example.com

---

**Built with ❤️ using FastAPI, LangChain, and OpenAI**


