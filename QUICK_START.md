# Quick Start Guide - News Agent

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create `.env` file
```bash
# Copy this template and add your values
DATABASE_URL=sqlite:///./news_agent.db
PORT=5001
HOST=0.0.0.0
LOG_LEVEL=INFO
RATE_LIMIT=1440
RSS_SCRAPE_INTERVAL_MINUTES=1440
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Initialize Database
```bash
python -c "from src.db.session import init_db; init_db()"
```

### 4. Start the Server
```bash
uvicorn src.main:app --host 0.0.0.0 --port 5001 --reload
```

### 5. Test It
Visit: `http://localhost:5001/docs` for interactive API docs

Or run:
```bash
curl http://localhost:5001/health
```

## 📋 Testing Options

### Option 1: Postman Collection
1. Open Postman
2. Import `postman_collection.json`
3. All requests are pre-configured with examples

### Option 2: Bash Script (Linux/Mac)
```bash
chmod +x test_examples.sh
./test_examples.sh
```

### Option 3: PowerShell Script (Windows)
```powershell
.\test_examples.ps1
```

### Option 4: cURL Examples
See `LOCAL_TESTING.md` for detailed cURL examples

## 🎯 Quick Test Examples

### Health Check
```bash
curl http://localhost:5001/health
```

### Fetch Headlines
```bash
curl -X POST http://localhost:5001/a2a/news \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [{"kind": "text", "text": "fetch latest headlines"}],
        "messageId": "msg-1"
      }
    }
  }'
```

### Summarize News
```bash
curl -X POST http://localhost:5001/a2a/news \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [{"kind": "text", "text": "summarize the latest news"}],
        "messageId": "msg-2"
      }
    }
  }'
```

## 📚 Available Commands

- **"fetch latest"** or **"get headlines"** - Get latest news headlines
- **"summarize news"** - Summarize recent headlines
- **"analyze sentiment on [topic]"** - Analyze sentiment about a topic
- **"help"** - Show available commands
- Any question about current events

## 🔗 Key Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /a2a/news` - Main A2A endpoint for news agent
- `GET /docs` - Interactive API documentation (Swagger UI)

## 📖 Full Documentation

- See `LOCAL_TESTING.md` for comprehensive testing examples
- See `postman_collection.json` for Postman import
- See `README.md` for full project documentation

