# 🤖 LLM Setup Guide for ActivityGuide

## Quick Setup

### 1. Get API Keys

**OpenAI (Recommended):**
- Go to: https://platform.openai.com/api-keys
- Sign up/Login
- Create new API key
- Copy the key (starts with `sk-`)

**Anthropic (Alternative):**
- Go to: https://console.anthropic.com/
- Sign up for Anthropic account
- Get your API key

### 2. Configure Environment

Edit your `.env` file and replace the placeholder values:

```env
# AI Services - Anthropic is the primary choice, OpenAI is fallback
ANTHROPIC_API_KEY=your-actual-anthropic-key-here
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

### 3. Test LLM Parsing

Once configured, test with these example queries:

```bash
# Test via API
curl -X POST "http://localhost:8000/api/v1/nlp/parse" \
  -H "Content-Type: application/json" \
  -d '{"query": "Basketball classes for 8-10 near me this Saturday"}'
```

## LLM Priority & Fallback

The app uses **Anthropic Claude** as the primary LLM for all AI features, with **OpenAI GPT** as a fallback:

1. **Primary**: Anthropic Claude (claude-3-haiku-20240307) - faster, more cost-effective
2. **Fallback**: OpenAI GPT (gpt-3.5-turbo) - if Anthropic fails or isn't configured
3. **Pattern Matching**: Regex-based parsing if both LLMs fail

This ensures reliability and cost optimization while maintaining high-quality AI parsing.

## LLM Features

### **Smart Query Parsing**
- **Input**: "Basketball classes for 8-10 near me this Saturday"
- **Output**: 
  ```json
  {
    "parsed_params": {
      "age_min": 8,
      "age_max": 10,
      "category": "sports",
      "location": "near me",
      "day": "saturday",
      "start_date": "2024-01-06"
    },
    "confidence": 0.9,
    "suggestions": [],
    "llm_used": "openai"
  }
  ```

### **Intelligent Suggestions**
- **Input**: "Art activities for kids"
- **Output**: 
  ```json
  {
    "suggestions": [
      "What ZIP code would you like to search in?",
      "When would you like to do this activity?",
      "What age range are you looking for?"
    ]
  }
  ```

## Configuration Options

### **OpenAI Models**
- `gpt-3.5-turbo` (default, fast & cheap)
- `gpt-4` (more accurate, expensive)
- `gpt-4-turbo` (balanced)

### **Anthropic Models**
- `claude-3-haiku-20240307` (default, fast)
- `claude-3-sonnet-20240229` (balanced)
- `claude-3-opus-20240229` (most accurate)

### **Customize Parsing**

Edit `app/services/llm_parser.py`:

```python
# Change OpenAI model
response = await self.openai_client.chat.completions.create(
    model="gpt-4",  # Change this
    # ... rest of config
)

# Change Anthropic model
response = await self.anthropic_client.messages.create(
    model="claude-3-sonnet-20240229",  # Change this
    # ... rest of config
)
```

## Cost Optimization

### **OpenAI Pricing (GPT-3.5-turbo)**
- ~$0.001 per query
- Very cost-effective for MVP

### **Anthropic Pricing (Claude Haiku)**
- ~$0.00025 per query
- Cheapest option

### **Fallback Strategy**
If LLM fails, the system automatically falls back to pattern matching, so your app always works!

## Testing

### **Test Different Queries**
```python
test_queries = [
    "Basketball classes for 8-10 near me this Saturday",
    "Free art activities for my 5 year old this weekend",
    "Indoor activities near 48104 for toddlers",
    "Swimming lessons for kids aged 6-8",
    "Music classes this Tuesday near me"
]
```

### **Monitor Performance**
- Check logs for LLM usage
- Monitor API costs
- Test fallback behavior

## Troubleshooting

### **No API Key**
- System falls back to pattern matching
- Still functional but less intelligent

### **Rate Limits**
- LLM parsing may fail occasionally
- Automatic fallback to patterns

### **Invalid Responses**
- JSON parsing errors are handled gracefully
- Fallback to pattern matching

## Advanced Features

### **Custom Prompts**
Modify the system prompts in `llm_parser.py` for:
- Different parsing strategies
- Domain-specific knowledge
- Custom suggestion generation

### **Multiple LLM Providers**
The system tries OpenAI first, then Anthropic, then patterns:
1. OpenAI GPT
2. Anthropic Claude  
3. Pattern matching (always works)

This ensures maximum reliability!
