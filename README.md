# ActivityGuide 🎯

A city-first event discovery platform for parents, powered by AI personalization and real-time data from multiple sources.

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
