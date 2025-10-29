# ActivityGuide 🎯

A city-first event discovery platform for parents, powered by AI personalization and real-time data from multiple sources.

## 📖 What is ActivityGuide? (For Everyone)

**ActivityGuide helps parents find the perfect activities for their kids using smart AI technology.**

### How It Works (Simple View)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     🎯 ACTIVITYGUIDE FLOW                           │
└─────────────────────────────────────────────────────────────────────┘

  👨‍👩‍👧‍👦 PARENT SEARCHES
     ↓
     "Find confidence building activities for my shy 8-year-old"
     ↓
┌────────────────────────────────────────────────────────────────────┐
│  ① DATA COLLECTION (AI Agent 🤖 Works Behind the Scenes)          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  The AI Agent automatically:                                       │
│  • Keeps activity data fresh and up-to-date                       │
│  • Collects from 6+ sources: Yelp, Google, Eventbrite, etc.      │
│  • Runs every hour to check for new activities                    │
│  • Covers ANY city in the USA 🇺🇸                                 │
│  • No human effort needed - it's autonomous!                       │
│                                                                    │
│  📊 Data Sources:                                                  │
│  Yelp → Google Places → Eventbrite → Community Submissions        │
│         ↓                                                          │
│    💾 Database: 1,000+ Activities Ready to Search                 │
└────────────────────────────────────────────────────────────────────┘
     ↓
┌────────────────────────────────────────────────────────────────────┐
│  ② SMART SEARCH (RAG 🧠 Understands What You Mean)                │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  RAG (Retrieval-Augmented Generation) means:                       │
│  • Understands concepts, not just keywords                         │
│  • Knows "confidence building" = martial arts, drama, sports      │
│  • Understands "shy" needs small group settings                    │
│  • Considers age, location, price automatically                    │
│                                                                    │
│  How RAG Works:                                                    │
│  ┌────────────────┐     ┌────────────────┐    ┌────────────────┐ │
│  │ Your Question  │ →   │ AI Understands │ →  │ Smart Database │ │
│  │ (Natural       │     │ Your Intent &  │    │ Search Finds   │ │
│  │  Language)     │     │ Emotions       │    │ Best Matches   │ │
│  └────────────────┘     └────────────────┘    └────────────────┘ │
│                                                                    │
│  Instead of simple keyword matching like "confidence",             │
│  RAG finds activities that ACTUALLY help build confidence!         │
└────────────────────────────────────────────────────────────────────┘
     ↓
┌────────────────────────────────────────────────────────────────────┐
│  ③ AI ANALYSIS (AI Explains WHY Each Activity is Perfect) 💡      │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  AI reads each activity and explains:                              │
│  • Why it's good for YOUR specific child                          │
│  • How it addresses their needs (e.g., "shy")                     │
│  • What makes it age-appropriate                                   │
│  • Special considerations (price, location, schedule)              │
└────────────────────────────────────────────────────────────────────┘
     ↓
┌────────────────────────────────────────────────────────────────────┐
│  ④ RESULTS YOU SEE 🎉                                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  🥋 Kids Martial Arts - Beginner                                   │
│     Age: 6-12 | Troy, MI | $80/month                              │
│     ⭐ 95% Match                                                   │
│     💡 "Builds confidence through structured discipline and        │
│         achievement. Small class sizes perfect for shy children."  │
│                                                                    │
│  🎭 Youth Drama Workshop                                           │
│     Age: 7-14 | Birmingham, MI | Free                             │
│     ⭐ 92% Match                                                   │
│     💡 "Public performance in supportive environment helps         │
│         overcome shyness and build self-assurance."                │
│                                                                    │
│  🏀 Basketball Fundamentals                                        │
│     Age: 7-10 | Detroit, MI | $50/month                           │
│     ⭐ 88% Match                                                   │
│     💡 "Team sports build social skills and confidence             │
│         through group achievement."                                │
└────────────────────────────────────────────────────────────────────┘

```

### 🔑 Key Benefits

| What You Get | How It Helps |
|-------------|--------------|
| **🤖 AI Agent** | Automatically keeps all activity data fresh - you always see current information |
| **🧠 Smart Search (RAG)** | Understands what you mean, not just what you say - finds activities that truly fit |
| **💡 AI Explanations** | Know WHY each activity is recommended for YOUR child's specific needs |
| **⚡ Fast Results** | Get personalized recommendations in seconds, not hours of research |
| **🌎 USA-Wide Coverage** | Works for ANY city in the United States |
| **💰 All Budgets** | Free and paid activities, with clear pricing |

### 🎯 Real Example

**Parent Types:** "My 8-year-old is really shy and needs help making friends"

**Without ActivityGuide:**
- 😫 Google for 2 hours
- 📞 Call 10+ places
- ❓ Wonder if they're appropriate
- ⏰ Spend your whole evening

**With ActivityGuide:**
- ⚡ 3 seconds to get results
- 🎯 8 activities specifically chosen for shy kids
- 💡 Clear explanations why each helps
- ✅ Age-appropriate, local, and current

---

## 🚀 Features

### MVP Features
- **Multi-Source Event Ingestion**: Eventbrite, Yelp, Google Places, Ticketmaster APIs
- **AI-Powered Personalization**: LangChain + OpenAI for smart recommendations
- **Fast Cache Layer**: Redis for sub-second event retrieval
- **ZIP Code Search**: Find activities by location with smart filtering
- **User Profiles**: Personalized recommendations based on child ages and preferences
- **Community Submissions**: Self-serve event posting system
- **Background Sync**: Automated data synchronization every 6 hours

### Tech Stack
- **Backend**: FastAPI (Python) with async processing
- **Frontend**: React + TypeScript + Tailwind CSS
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for high-performance data retrieval
- **AI**: LangChain + OpenAI for personalization and summarization
- **Background Jobs**: Celery for API synchronization
- **Deployment**: Railway-ready with Docker support

## 🛠️ Setup & Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Backend Setup

1. **Activate virtual environment**:
   ```bash
   # Windows (PowerShell)
   .\venv\Scripts\Activate.ps1
   
   # Windows (Command Prompt)
   venv\Scripts\activate.bat
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database settings
   ```

4. **Run the backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm start
   ```

### Database Setup

1. **Start PostgreSQL and Redis**:
   ```bash
   # Using Docker Compose
   docker-compose up postgres redis -d
   
   # Or start services manually
   ```

2. **Run database migrations**:
   ```bash
   # Database tables are created automatically on first run
   ```

### API Keys Required

Configure these in your `.env` file:
- `EVENTBRITE_API_KEY` - Eventbrite API access
- `YELP_API_KEY` - Yelp Fusion API
- `GOOGLE_PLACES_API_KEY` - Google Places API
- `TICKETMASTER_API_KEY` - Ticketmaster Discovery API
- `ANTHROPIC_API_KEY` - Anthropic API (primary choice for AI features)
- `OPENAI_API_KEY` - OpenAI API (fallback for AI features)

## 🚀 Deployment

### Railway Deployment

1. **Connect to Railway**:
   ```bash
   railway login
   railway init
   ```

2. **Set environment variables**:
   ```bash
   railway variables set DATABASE_URL=your_postgres_url
   railway variables set REDIS_URL=your_redis_url
   # ... set other required variables
   ```

3. **Deploy**:
   ```bash
   railway up
   ```

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

## 📱 Usage

### Example Workflow

1. **User searches**: "Find kid activities near 48104"
2. **AI Agent queries**: Eventbrite & Yelp APIs with ZIP=48104, categories=family,kids
3. **Collects results**: title, date/time, description, URL
4. **Returns personalized recommendations**:
   - Storytime at Ann Arbor Library – Sat 10am 📍 [Link]
   - Hands-on Kids Museum Day – Sun 12pm 📍 [Link]
   - Family Hike at County Park – Sun 2pm 📍 [Link]

### API Endpoints

- `GET /api/v1/events/search` - Search events with AI personalization
- `GET /api/v1/events/{id}` - Get event details
- `POST /api/v1/users/profiles` - Create user profile
- `POST /api/v1/providers/submissions` - Submit community event
- `GET /health` - Health check

## 🔧 Development

### Project Structure
```
ActivityGuide/
├── app/                    # FastAPI backend
│   ├── api/               # API routes
│   ├── core/              # Configuration & database
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic & API clients
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   └── ...
├── requirements.txt       # Python dependencies
└── docker-compose.yml     # Local development setup
```

### Adding New Event Sources

1. Create API client in `app/services/api_clients.py`
2. Add normalization method to convert to standard event format
3. Integrate with sync service in `app/services/sync.py`

### Customizing AI Recommendations

Modify prompts and logic in `app/services/ai_agent.py`:
- Personalization prompts
- Event scoring algorithms
- Summary generation

## 📊 Monitoring

- Health check: `GET /health`
- Background sync status: Check logs
- Cache performance: Redis monitoring
- API rate limits: Monitor external API usage

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

All rights reserved. This is proprietary software.
