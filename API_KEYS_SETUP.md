# 🔑 API Keys Setup Guide

This guide shows you exactly where to store API keys and how to get them for all data sources.

## 📁 Storage Location

**Primary File**: `.env` (in project root: `C:\code\ActivityGuide\.env`)

## 🔑 Complete API Keys List

### ✅ Currently Configured
```env
# Event Data Sources
EVENTBRITE_API_KEY=your_eventbrite_key_here

# AI Services  
ANTHROPIC_API_KEY=your_anthropic_key_here
PARALLEL_AI_API_KEY=your_parallel_ai_key_here
```

### ❌ Missing API Keys (Need to be added)

#### 🎪 Event Data Sources
```env
# Yelp Fusion API - Family businesses, restaurants, activities
YELP_API_KEY=your_yelp_api_key_here

# Google Places API - Parks, gyms, museums, venues
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here

# Ticketmaster Discovery API - Family shows, entertainment
TICKETMASTER_API_KEY=your_ticketmaster_api_key_here

# Meetup API - Community events and groups
MEETUP_API_KEY=your_meetup_api_key_here

# Recreation.gov RIDB API - National park programs
RECREATION_GOV_API_KEY=your_recreation_gov_api_key_here
```

#### 🤖 AI Services
```env
# OpenAI API - For LLM features and AI personalization
OPENAI_API_KEY=your_openai_api_key_here
```

#### 🏢 Organization APIs (Optional - for web scraping)
```env
# YMCA - Programs and activities (may not have public API)
YMCA_API_KEY=your_ymca_api_key_here

# Boys & Girls Clubs - Activities (may not have public API)
BOYS_GIRLS_CLUB_API_KEY=your_boys_girls_club_api_key_here
```

## 🚀 How to Get API Keys

### 1. **Yelp Fusion API**
- Go to: https://www.yelp.com/developers
- Create account → Create App
- Copy API Key
- **Free tier**: 500 requests/day

### 2. **Google Places API**
- Go to: https://developers.google.com/maps/documentation/places/web-service
- Enable Google Cloud Console
- Create API Key
- Enable Places API
- **Pricing**: $0.017 per request

### 3. **Ticketmaster Discovery API**
- Go to: https://developer.ticketmaster.com/
- Create account → Get API Key
- **Free tier**: 5,000 requests/day

### 4. **Meetup API**
- Go to: https://www.meetup.com/meetup_api/
- Create account → Get API Key
- **Free tier**: 200 requests/hour

### 5. **Recreation.gov RIDB API**
- Go to: https://ridb.recreation.gov/
- Create account → Get API Key
- **Free**: No cost

### 6. **OpenAI API**
- Go to: https://platform.openai.com/api-keys
- Create account → Create API Key
- **Pricing**: Pay per token

## 📝 Complete .env Template

Copy this into your `.env` file and fill in the missing keys:

```env
# Database - Using SQLite for local development
DATABASE_URL=sqlite:///./activityguide.db

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# ==============================================
# EVENT DATA SOURCES
# ==============================================

# Eventbrite API - Events and classes
EVENTBRITE_API_KEY=your_eventbrite_key_here

# Yelp Fusion API - Family businesses
YELP_API_KEY=your_yelp_api_key_here

# Google Places API - Parks, gyms, museums
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here

# Ticketmaster Discovery API - Family shows
TICKETMASTER_API_KEY=your_ticketmaster_api_key_here

# Meetup API - Community events
MEETUP_API_KEY=your_meetup_api_key_here

# Recreation.gov RIDB API - National parks
RECREATION_GOV_API_KEY=your_recreation_gov_api_key_here

# YMCA API (optional - may not exist)
YMCA_API_KEY=your_ymca_api_key_here

# Boys & Girls Clubs API (optional - may not exist)
BOYS_GIRLS_CLUB_API_KEY=your_boys_girls_club_api_key_here

# OpenStreetMap (no API key required)
OSM_USER_AGENT=ActivityGuide/1.0 (Family Event Discovery)

# ==============================================
# AI SERVICES
# ==============================================

# OpenAI API - For LLM features
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API - Primary AI service
ANTHROPIC_API_KEY=your_anthropic_key_here

# Parallel AI API
PARALLEL_AI_API_KEY=your_parallel_ai_key_here

# ==============================================
# EMAIL SETTINGS
# ==============================================

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# ==============================================
# APP SETTINGS
# ==============================================

SECRET_KEY=your_secret_key_here_change_in_production
DEBUG=True
ENVIRONMENT=development

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Sync Settings
SYNC_INTERVAL_HOURS=6
```

## 🔒 Security Best Practices

### ✅ DO:
- Keep `.env` file in `.gitignore` (already configured)
- Use environment variables in production
- Rotate API keys regularly
- Monitor API usage and costs

### ❌ DON'T:
- Commit API keys to git
- Share API keys in code
- Use production keys in development
- Leave API keys in public repositories

## 🧪 Testing API Keys

After adding keys, test them:

```bash
# Run the test script
python test_unified_integration.py

# Or test individual APIs
python -c "
from app.services.unified_api_clients import unified_api_manager
import asyncio

async def test():
    results = await unified_api_manager.search_all_sources()
    print('Available sources:', len(results))

asyncio.run(test())
"
```

## 📊 API Usage Monitoring

Monitor your API usage in:
- **Yelp**: https://www.yelp.com/developers
- **Google Cloud**: https://console.cloud.google.com/
- **Ticketmaster**: https://developer.ticketmaster.com/
- **Meetup**: https://www.meetup.com/meetup_api/
- **OpenAI**: https://platform.openai.com/usage

## 💰 Cost Estimation

### Free Tiers Available:
- **Yelp**: 500 requests/day (FREE)
- **Ticketmaster**: 5,000 requests/day (FREE)
- **Meetup**: 200 requests/hour (FREE)
- **Recreation.gov**: Unlimited (FREE)

### Paid Services:
- **Google Places**: ~$0.017 per request
- **OpenAI**: Pay per token (~$0.002 per 1K tokens)

### Estimated Monthly Cost:
- **Small scale** (1,000 searches/day): ~$20-50/month
- **Medium scale** (10,000 searches/day): ~$200-500/month

## 🚨 Troubleshooting

### Common Issues:

1. **"API key not configured" warnings**
   - Check `.env` file exists and has correct variable names
   - Restart your application after adding keys

2. **Rate limit exceeded**
   - Implement request throttling
   - Use caching to reduce API calls

3. **Invalid API key errors**
   - Verify key is correct and active
   - Check API key permissions

4. **Missing environment variables**
   - Ensure `.env` file is in project root
   - Check variable names match exactly (case-sensitive)
