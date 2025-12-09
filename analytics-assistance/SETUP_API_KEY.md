# 🔑 Setting Up Your OpenAI API Key

## Step 1: Get Your API Key

1. Go to: https://platform.openai.com/api-keys
2. Log in (or create account)
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

## Step 2: Create `.env` File

```bash
# In the analytics-assistance/ directory, create .env file:
cp .env.example .env
```

## Step 3: Add Your API Key

Open `.env` and replace `sk-your-key-here` with your actual key:

```bash
# .env
OPENAI_API_KEY=sk-proj-abcd1234...  # ← Your actual key here
OPENAI_MODEL=gpt-4o-mini              # ← Keep this (cheapest!)
OPENAI_TEMPERATURE=0.1                # ← Keep this
OPENAI_MAX_TOKENS=200                 # ← Keep this
```

## Step 4: Verify Setup

Run this test:

```bash
python test_llm_setup.py
```

Should see: ✅ OpenAI API key found!

## 💰 Cost Info

With `gpt-4o-mini`:
- ~$0.0002 per analysis request
- 1,000 requests = $0.20
- Very cheap! 🎉

## 🔒 Security

- ✅ `.env` is in `.gitignore` (never committed)
- ✅ Keep your key private
- ✅ Don't share `.env` file

## ❓ Troubleshooting

**Error: "OPENAI_API_KEY not found"**
- Make sure `.env` file exists in `analytics-assistance/` directory
- Check the key starts with `sk-`
- No quotes needed around the key

**Error: "Invalid API key"**
- Check you copied the full key
- Make sure key is active at https://platform.openai.com/api-keys

