# 🚀 Quick Start Guide

## Start Both Servers (2 Commands)

### 1. Start Backend API

```bash
cd /home/avaxpro16/Desktop/llm-analytics/analytics-assistance && ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**URL:** http://localhost:8000  
**Docs:** http://localhost:8000/docs

---

### 2. Start React UI (New Terminal)

```bash
cd /home/avaxpro16/Desktop/llm-analytics/analytics-ui && npm start
```

**URL:** http://localhost:3000

---

## ✅ That's It!

**Backend:** http://localhost:8000  
**Frontend:** http://localhost:3000

---

## 🛑 Stop Servers

Press `Ctrl + C` in each terminal window

---

## 🔄 Quick Restart

If servers stop, just run the 2 commands again!

