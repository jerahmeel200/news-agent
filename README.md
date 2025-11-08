

# News Agent 🚀

An AI agent that fetches, summarizes, and analyzes news headlines using RSS feeds and the A2A (Agent-to-Agent) protocol. Get real-time news insights, sentiment analysis, and summaries powered by Google Gemini.

## Features 

- **RSS Feed Integration**: Continuously fetches news from configured RSS feeds
- **Headline Summarization**: AI-powered summaries of latest news headlines
- **Sentiment Analysis**: Analyze sentiment on topics across recent news
- **A2A Protocol Support**: Full JSON-RPC 2.0 A2A protocol implementation
- **Natural Language Interface**: Chat with the agent to get news insights
- **Background Scraping**: Automatically updates news feeds on schedule
- **Interactive API Docs**: Swagger UI for easy testing

## Architecture 

```
src/
├── db/                    # Database layer
│   ├── session.py         # SQLAlchemy session management
│   └── repository.py      # Data access repositories
├── models/                # Data models
│   ├── job.py            # SQLAlchemy models
│   └── a2a.py            # A2A protocol models
├── routers/               # API endpoints
│   ├── admin.py          # Admin operations
│   └── ai.py             # AI-related endpoints
├── schemas/               # Pydantic schemas
│   └── job.py            # Request/response schemas
├── services/              # Business logic
│   ├── rss_scraper.py    # RSS feed scraping
│   ├── news_agent.py      # News agent A2A implementation
│   └── ai.py             # AI service (Google Gemini)
├── tests/                 # Test suite
└── main.py               # FastAPI application
```

## Installation 📦

### Prerequisites

- Python 3.13+
- SQLite (for local development) or PostgreSQL (for production)
- Google Gemini API Key ([Get one here](https://ai.google.dev/))

### Quick Start

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd telex-ai-agent-main
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
Create a `.env` file in the root directory:
```bash
# Database
DATABASE_URL=sqlite:///./news_agent.db

# Server
PORT=5001
HOST=0.0.0.0
LOG_LEVEL=INFO

# RSS Scraping
RATE_LIMIT=1440
RSS_SCRAPE_INTERVAL_MINUTES=1440

# AI Service (Google Gemini)
API_KEY=your_gemini_api_key_here
```

5. **Initialize database**
```bash
python -c "from src.db.session import init_db; init_db()"
```

## Usage 🚀

### Start the Server

```bash
uvicorn src.main:app --host 0.0.0.0 --port 5001 --reload
```

The server will start on `http://localhost:5001`

**Alternative:** For development with auto-reload:
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 5001 --reload
```

### A2A Protocol Usage

Send A2A requests to `/a2a/news`:

```bash
curl -X POST http://localhost:5001/a2a/news \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-001",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "fetch latest headlines"
          }
        ],
        "messageId": "msg-001"
      }
    }
  }'
```

### Available Commands

**News Fetching**
- "fetch latest" or "get headlines" - Display latest news headlines
- "fetch latest headlines" - Get recent news from RSS feeds

**Summarization**
- "summarize news" - Get a summary of recent headlines
- "summarize the latest news" - AI-powered summary of recent news

**Sentiment Analysis**
- "analyze sentiment on [topic]" - Analyze sentiment about a specific topic
- "analyze sentiment on artificial intelligence" - Example with topic

**General**
- "help" - Show available commands
- Any question about current events - AI will answer based on recent news

### API Endpoints

**Main Endpoints**
- `GET /` - API information and capabilities
- `GET /health` - Health check endpoint
- `POST /a2a/news` - Main A2A endpoint for news agent
- `GET /docs` - Interactive API documentation (Swagger UI)

**Admin Endpoints**
- `POST /api/admin/scrape` - Manually trigger RSS scraping
- `GET /api/admin/status` - Get system status

**Documentation**
- Visit `http://localhost:5001/docs` for interactive API documentation

## Configuration 

Key environment variables:

```bash
# Server
PORT=5001
HOST=0.0.0.0
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./news_agent.db
# For PostgreSQL: DATABASE_URL=postgresql://user:pass@localhost:5432/news_agent

# RSS Scraping
RATE_LIMIT=1440                    # Requests per day
RSS_SCRAPE_INTERVAL_MINUTES=1440   # How often to scrape (default: 24 hours)

# AI Service (Google Gemini)
API_KEY=your_gemini_api_key_here   # Required: Get from https://ai.google.dev/
```

## Development

### Run Tests

```bash
pytest src/tests/ -v
```

### Code Formatting

```bash
black src/
ruff check src/
```

### Testing the API

**Option 1: Postman Collection**
- Import `postman_collection.json` into Postman
- All requests are pre-configured

**Option 2: Test Scripts**
- Windows: `.\test_examples.ps1`
- Linux/Mac: `chmod +x test_examples.sh && ./test_examples.sh`

**Option 3: Manual Testing**
- See `LOCAL_TESTING.md` for detailed examples
- Use interactive docs at `http://localhost:5001/docs`

## Background Jobs 📅

The agent automatically:
1. **Scrapes RSS feeds** on a schedule (configurable via `RSS_SCRAPE_INTERVAL_MINUTES`)
2. **Stores headlines** in the database for analysis
3. **Updates news data** continuously in the background

## A2A Protocol 🤖

This agent implements the A2A (Agent-to-Agent) protocol for standardized AI agent communication:

- **JSON-RPC 2.0** based
- **Message/Send** method for single interactions
- **Execute** method for multi-turn conversations
- **Task management** with status tracking
- **Artifact support** for structured data

## Example Responses

**Fetch Headlines Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "result": {
    "id": "task-123",
    "contextId": "ctx-456",
    "status": {
      "state": "completed",
      "message": {
        "role": "agent",
        "parts": [{
          "kind": "text",
          "text": "Latest headlines:\n- Headline 1\n- Headline 2..."
        }]
      }
    },
    "artifacts": [{
      "name": "headlines.json",
      "parts": [{
        "kind": "data",
        "data": [{
          "title": "Headline 1"
        }]
      }]
    }],
    "kind": "task"
  }
}
```

**Sentiment Analysis Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "req-002",
  "result": {
    "id": "task-124",
    "contextId": "ctx-457",
    "status": {
      "state": "completed",
      "message": {
        "role": "agent",
        "parts": [{
          "kind": "text",
          "text": "Sentiment analysis on 'artificial intelligence':\n\nOverall sentiment: Positive\nKey themes: AI development, ethical concerns, innovation\nNotable trends: Increased discussion about AI safety..."
        }]
      }
    },
    "artifacts": [],
    "kind": "task"
  }
}
```

## Quick Links

- **Start Guide**: See `START_HERE.md` for step-by-step setup
- **Testing Guide**: See `LOCAL_TESTING.md` for detailed examples
- **Quick Reference**: See `QUICK_START.md` for quick commands

## License

[Add your license here]

---

**Need help?** Check the documentation files or open an issue on GitHub.
