# 🚀 Quick Start Guide

## Start Both Servers (2 Commands)

### 1. Start Backend API

```bash
cd /home/avaxpro16/Desktop/llm-analytics/analytics-assistance && ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

to kill process
# 1. Find the process using port 8000
lsof -ti:8000

# 2. Kill it (replace XXXX with the PID from step 1)
kill -9 XXXX

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

---

## ⚠️ Troubleshooting: "Address Already in Use"

### If Backend Port 8000 is Busy:
```bash
kill -9 $(lsof -ti:8000)
```

### If Frontend Port 3000 is Busy:
```bash
kill -9 $(lsof -ti:3000)
```

### Kill BOTH Ports at Once:
```bash
kill -9 $(lsof -ti:8000,3000)
```

Then restart the servers using the commands above!

