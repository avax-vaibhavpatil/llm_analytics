# 🎓 FastAPI Integration Explained - Step by Step

## What We Did: Complete Learning Guide

This document explains **HOW** we integrated the Factory Pattern with FastAPI.
Every step is explained so you understand the process!

---

## 📚 Part 1: The Problem

### Before Integration:

```python
# analytics-assistance/app/services/column_planner.py (OLD)

from langchain_openai import ChatOpenAI  # ← Hardcoded OpenAI!

def get_llm():
    return ChatOpenAI(  # ← Always returns OpenAI
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.1
    )

async def plan_columns(table_name, table_schema, user_requirement):
    llm = get_llm()  # ← Always OpenAI
    structured_llm = llm.with_structured_output(ColumnPlanOutput)
    chain = COLUMN_PLANNER_PROMPT | structured_llm
    result = await chain.ainvoke({...})
    return result
```

**Problems:**
1. ❌ Tightly coupled to OpenAI
2. ❌ Uses LangChain's specific methods (`with_structured_output`)
3. ❌ Can't switch providers without rewriting code
4. ❌ Expensive (OpenAI costs money)

**User Story:** "I want to switch providers by just changing config, not code!"

---

## 🎯 Part 2: The Solution

We replaced the hardcoded OpenAI implementation with the Factory Pattern:

### Architecture Overview:

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│  (app/main.py, app/routes/analytics.py)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    column_planner.py                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  get_llm() → ModelProvider_from_yaml("config.yaml")   │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    model_factory.py                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Reads config.yaml                                     │ │
│  │  provider = config["llm"]["provider"]  # "groq"       │ │
│  │  return _PROVIDERS[provider](...)  # GroqProvider     │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    llm/providers/                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ OpenAI       │  │ Groq         │  │ Future...    │      │
│  │ Provider     │  │ Provider     │  │ Providers    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
                    LLM APIs
```

---

## 🔧 Part 3: What We Changed (Step by Step)

### Step 1: Removed Hardcoded OpenAI Import

**Before:**
```python
from langchain_openai import ChatOpenAI  # ← OpenAI-specific
```

**After:**
```python
from llm.model_factory import ModelProvider_from_yaml  # ← Provider-agnostic
```

**Why:** We don't want to import any specific provider. We import the factory that creates providers!

---

### Step 2: Replaced get_llm() Function

**Before:**
```python
def get_llm() -> ChatOpenAI:  # ← Returns only OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=api_key,
        temperature=0.1
    )
```

**After:**
```python
def get_llm():  # ← Returns ANY provider!
    CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"
    return ModelProvider_from_yaml(str(CONFIG_PATH))
```

**What Changed:**
1. No hardcoded model name
2. No hardcoded API key retrieval
3. Factory reads config.yaml and decides which provider to create
4. Returns a provider that implements `BaseProvider` interface

**Why:** Now when we call `get_llm()`, it could return OpenAI, Groq, or any provider based on config!

---

### Step 3: Replaced LangChain Chain with Manual Prompt + Parse

**Before (LangChain-specific):**
```python
# This only works with LangChain wrappers!
llm = get_llm()
structured_llm = llm.with_structured_output(ColumnPlanOutput)
chain = COLUMN_PLANNER_PROMPT | structured_llm
result = await chain.ainvoke({...})
```

**After (Provider-agnostic):**
```python
# This works with ANY provider!
llm = get_llm()  # Could be OpenAI, Groq, etc.

# Create parser for structured output
parser = PydanticOutputParser(pydantic_object=ColumnPlanOutput)

# Format prompt manually
prompt_text = COLUMN_PLANNER_PROMPT.format(
    table_name=table_name,
    columns_formatted=columns_formatted,
    user_requirement=user_requirement,
    format_instructions=parser.get_format_instructions()
)

# Call provider's generate() method
response = await asyncio.to_thread(llm.generate, prompt_text)

# Parse response manually
result = parser.parse(response)
```

**What Changed:**
1. **Before:** Used LangChain's `with_structured_output()` magic
2. **After:** Manually format prompt and parse response
3. **Before:** Used LangChain's `|` (pipe) operator to chain operations
4. **After:** Explicit steps: format → generate → parse

**Why This Works:**
- All our providers have `generate(prompt: str) -> str` method
- This is provider-agnostic! Whether it's OpenAI, Groq, or Anthropic, they all have this method
- We handle the parsing ourselves, so we're not dependent on LangChain

---

### Step 4: Added Async Support

**Problem:** Our providers use `generate()` which is synchronous (blocking).
But `plan_columns()` is async (non-blocking).

**Solution:**
```python
# Run sync function in thread pool to avoid blocking event loop
response = await asyncio.to_thread(llm.generate, prompt_text)
```

**What `asyncio.to_thread()` does:**
1. Takes a sync function (`llm.generate`)
2. Runs it in a separate thread from the thread pool
3. Awaits completion without blocking the async event loop
4. Returns the result

**Why:** FastAPI is async. We don't want to block the entire server waiting for LLM response.

---

## 🧪 Part 4: How It Works End-to-End

Let's trace a real API call:

### User Makes Request:

```bash
curl -X POST http://localhost:8000/api/analyze/columns \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "crm_customers",
    "requirement": "Show me average MRR by industry"
  }'
```

### Execution Flow:

#### 1. FastAPI receives request
```python
# app/routes/analytics.py
@router.post("/analyze/columns")
async def analyze_columns(request: AnalyzeColumnsRequest):
    # Validate table exists
    table_name = request.table_name  # "crm_customers"
    requirement = request.requirement  # "Show me average MRR by industry"
    
    # Get table schema from cache
    schema = get_table_schema(table_name)
    
    # Call column planner (this is where the magic happens!)
    analysis = await plan_columns(table_name, schema, requirement)
    ...
```

#### 2. column_planner calls get_llm()
```python
# app/services/column_planner.py
async def plan_columns(table_name, table_schema, user_requirement):
    # Get LLM instance from factory
    llm = get_llm()  # ← THIS IS THE KEY LINE!
    ...
```

#### 3. get_llm() calls the factory
```python
def get_llm():
    CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"
    return ModelProvider_from_yaml(str(CONFIG_PATH))
    # ↑ This reads config.yaml and creates the right provider
```

#### 4. Factory reads config.yaml
```python
# llm/model_factory.py
def ModelProvider_from_yaml(config_path: str):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    provider_name = config["llm"]["provider"]  # "groq"
    model = config["llm"]["model"]  # "llama-3.3-70b-versatile"
    temperature = config["llm"]["temperature"]  # 0.1
    max_tokens = config["llm"]["max_tokens"]  # 500
    
    # Get provider class from registry
    provider_class = _PROVIDERS[provider_name]  # GroqProvider
    
    # Create and return instance
    return provider_class(
        model=model,
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=temperature,
        max_tokens=max_tokens
    )
```

#### 5. Factory returns GroqProvider instance
```python
# llm = GroqProvider(model="llama-3.3-70b-versatile", ...)
# llm has generate() and generate_stream() methods
```

#### 6. column_planner formats prompt and calls generate()
```python
# Format the prompt
prompt_text = """
You are analyzing a table called 'crm_customers' with these columns:
- customer_id (string): Unique identifier
- company_name (string): Company name
- industry (string): Industry sector
- mrr (number): Monthly Recurring Revenue
...

User requirement: Show me average MRR by industry

Return a JSON object with required_columns, optional_columns, etc.
"""

# Call provider
response = await asyncio.to_thread(llm.generate, prompt_text)
# ↑ Runs in thread pool, doesn't block FastAPI
```

#### 7. GroqProvider calls Groq API
```python
# Inside groq_provider.py
def generate(self, prompt: str) -> str:
    response = self.client.chat.completions.create(
        model=self.model,  # "llama-3.3-70b-versatile"
        messages=[
            {"role": "system", "content": "You are a helpful AI..."},
            {"role": "user", "content": prompt}
        ],
        temperature=self.temperature,
        max_tokens=self.max_tokens
    )
    return response.choices[0].message.content
```

#### 8. Groq returns response
```json
{
  "technical_summary": "Calculate average MRR grouped by industry",
  "required_columns": ["mrr", "industry"],
  "optional_columns": ["company_name", "segment"],
  ...
}
```

#### 9. column_planner parses response
```python
# Parse JSON string into Pydantic model
result = parser.parse(response)
# result is now a ColumnPlanOutput instance
```

#### 10. FastAPI returns to user
```python
# app/routes/analytics.py
return {
    "technical_summary": result.technical_summary,
    "required_columns": result.required_columns,
    ...
}
```

---

## 🎯 Part 5: Key Concepts Explained

### 1. Abstraction
**What it is:** Hiding implementation details behind a common interface.

**In our code:**
```python
# BaseProvider defines the interface:
class BaseProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

# All providers implement this interface:
class OpenAIProvider(BaseProvider):
    def generate(self, prompt: str) -> str:
        # OpenAI-specific implementation
        ...

class GroqProvider(BaseProvider):
    def generate(self, prompt: str) -> str:
        # Groq-specific implementation
        ...
```

**Benefit:** `column_planner.py` doesn't care which provider is used. It just calls `llm.generate(prompt)` and it works!

---

### 2. Dependency Injection
**What it is:** Passing dependencies into a class/function instead of creating them inside.

**In our code:**
```python
# BAD (tight coupling):
def plan_columns(...):
    llm = OpenAI(...)  # ← Hardcoded dependency

# GOOD (dependency injection):
def plan_columns(...):
    llm = get_llm()  # ← get_llm() decides which provider
```

**Benefit:** Easy to test, easy to change providers.

---

### 3. Factory Pattern
**What it is:** A function/class that creates objects without specifying their exact class.

**In our code:**
```python
# Factory decides which class to create:
def ModelProvider(name: str):
    if name == "openai":
        return OpenAIProvider(...)
    elif name == "groq":
        return GroqProvider(...)
```

**Benefit:** Add new providers without changing existing code!

---

### 4. Config-Driven Design
**What it is:** Using configuration files to control behavior instead of code.

**In our code:**
```yaml
# config.yaml
llm:
  provider: groq  # ← Change this to switch providers!
```

**Benefit:** Change behavior without code changes or redeployment!

---

## 🧪 Part 6: Testing the Integration

### Test 1: Direct Function Call
```python
# test_column_planner_integration.py
result = await plan_columns(
    table_name="crm_customers",
    table_schema=SAMPLE_SCHEMA,
    user_requirement="Show me average MRR by industry"
)

print(result.required_columns)  # ["mrr", "industry"]
```

**Result:** ✅ Works! Uses Groq from config.yaml

---

### Test 2: API Endpoint
```bash
curl -X POST http://localhost:8000/api/analyze/columns \
  -H "Content-Type: application/json" \
  -d '{"table_name": "crm_customers", "requirement": "Show me average MRR"}'
```

**Result:** ✅ Works! FastAPI → column_planner → Factory → Groq API → Response

---

### Test 3: Provider Switch
```yaml
# Change config.yaml
llm:
  provider: openai  # ← Changed from "groq"
```

```bash
# Restart FastAPI and test again
curl -X POST http://localhost:8000/api/analyze/columns ...
```

**Result:** ✅ Now uses OpenAI! No code changes!

---

## 📊 Part 7: Before vs After Comparison

### Switching from OpenAI to Groq:

#### Before (Hardcoded):
```bash
# Files to change:
1. column_planner.py - Change imports
2. column_planner.py - Change API client initialization
3. column_planner.py - Update error handling
4. column_planner.py - Handle different response format
5. .env - Add new API key
6. requirements.txt - Add new package
7. Test everything
8. Deploy

# Time: 2-4 hours
# Risk: HIGH (breaking changes)
# Code changes: 50+ lines across multiple files
```

#### After (Factory):
```bash
# Files to change:
1. config.yaml - Change provider: "groq"

# Time: 30 seconds
# Risk: ZERO (interface is identical)
# Code changes: 1 line
```

---

## 🎓 Part 8: Learning Takeaways

### What You Learned:

1. **Abstraction:** Creating common interfaces that hide implementation details
2. **Factory Pattern:** Using a factory to create objects dynamically
3. **Dependency Injection:** Passing dependencies instead of hardcoding them
4. **Config-Driven Design:** Using YAML to control behavior
5. **Loose Coupling:** Making components independent and interchangeable
6. **Async Programming:** Using `asyncio.to_thread()` to run sync code in async context
7. **Provider-Agnostic Architecture:** Building systems that work with any provider

### Why This Matters:

- **Production-Ready:** This is how real-world applications are built
- **Scalable:** Easy to add new providers as they emerge
- **Maintainable:** Changes are isolated and easy to make
- **Testable:** Can mock providers for unit tests
- **Cost-Effective:** Switch to cheaper providers without code changes

---

## 🎉 Conclusion

**You now understand:**

1. How FastAPI integrates with your LLM abstraction layer
2. How the Factory Pattern works in practice
3. How config-driven architecture makes systems flexible
4. How to build provider-agnostic systems

**This is professional-grade software architecture!** 🚀

---

## 📚 Next Steps

Want to learn more? Try:

1. Add a new provider (Anthropic Claude)
2. Implement caching to reduce API calls
3. Add request/response logging
4. Implement fallback logic (if OpenAI fails, use Groq)
5. Add rate limiting
6. Create unit tests for each provider

**You have the foundation - build on it!** 💪

