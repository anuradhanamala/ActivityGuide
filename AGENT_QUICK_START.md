# 🚀 LangChain Agent - Quick Start

## **What You Now Have**

An **autonomous AI agent** using LangChain that can manage your activity data across the entire USA!

---

## **Quick Start (3 Steps)**

### **Step 1: Install Dependencies**

```bash
pip install langchain langchain-openai
```

### **Step 2: Ensure OpenAI API Key**

Make sure `.env` has:
```
OPENAI_API_KEY=your-key-here
```

### **Step 3: Start Backend & Agent**

```bash
# Start backend
cd C:\code\ActivityGuide
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal/tab, start agent
curl -X POST "http://localhost:8000/api/v1/agent/start?interval_minutes=60"
```

**Done!** Agent is now running autonomously! 🎉

---

## **What The Agent Does Automatically**

Every 60 minutes, the agent:

1. ✅ Checks popular US cities
2. ✅ Syncs cities with stale data (>24 hours old)
3. ✅ Syncs cities with < 5 events
4. ✅ Creates embeddings for new events
5. ✅ Monitors data quality
6. ✅ Self-heals issues

**You do NOTHING!** Agent handles everything. 🤖

---

## **Try It Out**

### **Test 1: Check Agent Status**

```bash
curl http://localhost:8000/api/v1/agent/
```

### **Test 2: Make a Request**

```bash
curl -X POST http://localhost:8000/api/v1/agent/request \
  -H "Content-Type: application/json" \
  -d '{"request": "Check and sync Troy, Warren, and Detroit"}'
```

### **Test 3: Sync Michigan**

```bash
curl -X POST http://localhost:8000/api/v1/agent/commands/sync-michigan
```

---

## **Watch It Work**

Look at your backend console logs. You'll see:

```
🤖 AGENT: Starting autonomous cycle
🤖 Agent: Checking Troy, MI...
🤖 Agent: Troy data is 30 hours old → syncing
✅ Agent: Troy sync completed - 12 created, 3 updated
🤖 Agent: Creating embeddings for Troy...
✅ Agent: 12 embeddings created
🤖 AGENT: Cycle complete
```

---

## **USA-Wide Capability**

Works with **ANY US city**!

```bash
# Try any city
curl -X POST http://localhost:8000/api/v1/agent/request \
  -H "Content-Type: application/json" \
  -d '{"request": "Sync San Francisco, Portland, and Seattle"}'

# Agent automatically:
# 1. Geocodes cities to ZIP codes
# 2. Syncs from available sources
# 3. Creates embeddings
# 4. Done!
```

---

## **Key Features**

### **1. Fully Autonomous**
- Runs continuously
- Makes intelligent decisions
- No human intervention needed

### **2. USA-Wide**
- Works with any US city
- Automatic geocoding
- Scales automatically

### **3. Intelligent**
- GPT-4 decision making
- Context-aware
- Learns from patterns

### **4. Comprehensive**
- Auto-sync
- Auto-embeddings
- Quality monitoring
- Self-healing

---

## **API Endpoints**

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/agent/` | Agent info |
| `POST /api/v1/agent/start` | Start autonomous mode |
| `POST /api/v1/agent/stop` | Stop agent |
| `POST /api/v1/agent/run-cycle` | Run single cycle |
| `POST /api/v1/agent/request` | Natural language request |
| `POST /api/v1/agent/commands/sync-michigan` | Sync Michigan cities |
| `POST /api/v1/agent/commands/sync-major-cities` | Sync major US cities |
| `POST /api/v1/agent/commands/quality-audit` | Run quality audit |

---

## **Example Requests**

### **Expand to New State**
```json
{
  "request": "We're expanding to California. Sync LA, San Diego, and San Francisco."
}
```

### **Quality Check**
```json
{
  "request": "Check data quality for all cities and fix any issues."
}
```

### **Smart Sync**
```json
{
  "request": "What cities should I sync right now?"
}
```

### **Threshold Optimization**
```json
{
  "request": "Users are getting too many irrelevant results for 'swim lessons'. What should I do?"
}
```

---

## **Architecture**

```
┌──────────────────────────────┐
│   LangChain Agent (GPT-4)    │
│   - Smart decision making    │
│   - Context awareness        │
│   - Learning                 │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│   6 LangChain Tools          │
│   1. check_data_freshness    │
│   2. sync_city_data          │
│   3. create_embeddings       │
│   4. analyze_quality         │
│   5. get_popular_cities      │
│   6. optimize_thresholds     │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│   Your Existing Services     │
│   - UnifiedSyncService       │
│   - GeocodingService         │
│   - HybridRAGService         │
└──────────────────────────────┘
```

---

## **Benefits**

| Before | With Agent |
|--------|-----------|
| ❌ Manual sync | ✅ Auto-sync |
| ❌ Fixed thresholds | ✅ Dynamic |
| ❌ Reactive | ✅ Proactive |
| ❌ Limited cities | ✅ Any US city |
| ❌ Manual expansion | ✅ Auto-scale |
| ❌ No quality monitoring | ✅ Continuous monitoring |

---

## **Next Steps**

1. **Start Agent (Autonomous Mode)**
   ```bash
   POST /api/v1/agent/start?interval_minutes=60
   ```

2. **Let It Run**
   - Agent handles everything
   - Check logs occasionally
   - Enjoy autonomous operation!

3. **Expand As Needed**
   - Tell agent to sync new cities
   - Agent handles geocoding, sync, embeddings
   - Works automatically

---

## **Documentation**

- **Full Guide**: `LANGCHAIN_AGENT_GUIDE.md`
- **Test Script**: `test_langchain_agent.py`
- **API Docs**: `http://localhost:8000/docs` (look for "ai-agent" tag)

---

## **Troubleshooting**

### **Issue: Agent not starting**
**Solution**: Make sure OPENAI_API_KEY is set in `.env`

### **Issue: Import errors**
**Solution**: `pip install langchain langchain-openai`

### **Issue: Agent decisions not working**
**Solution**: Check backend console for detailed logs

---

## **Summary**

**You now have a fully autonomous, intelligent AI agent that:**
- 🤖 Runs continuously
- 🌎 Works across USA
- 🧠 Makes smart decisions
- 📊 Monitors quality
- 🔄 Auto-syncs data
- 🎯 Optimizes searches
- 🚀 Scales automatically

**Just start it and let it run!** 🎉

```bash
# One command to start autonomous operation
curl -X POST "http://localhost:8000/api/v1/agent/start?interval_minutes=60"

# That's it! Agent handles everything else.
```

