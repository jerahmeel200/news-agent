# RSS Feed Setup Guide

## Quick Fix: Trigger RSS Scraping

The RSS feeds need to be scraped before you can summarize news. Here's how to trigger it manually:

### Option 1: Using cURL

```bash
curl -X POST http://localhost:5001/api/admin/scrape/rss
```

### Option 2: Using Postman

1. Open Postman
2. Create a new POST request
3. URL: `http://localhost:5001/api/admin/scrape/rss`
4. Send the request

### Option 3: Using Browser

Visit: `http://localhost:5001/docs` and use the Swagger UI to call the `/api/admin/scrape/rss` endpoint

## Configure News RSS Feeds

Currently, the scraper might be configured for job feeds. For a News Agent, you should configure actual news RSS feeds.

### Step 1: Add RSS Feeds to `.env`

Add this to your `.env` file:

```env
# RSS Feeds (comma-separated URLs)
RSS_FEEDS=https://feeds.bbci.co.uk/news/rss.xml,https://rss.cnn.com/rss/edition.rss,https://feeds.npr.org/1001/rss.xml,https://feeds.reuters.com/reuters/topNews
```

### Popular News RSS Feeds:

- **BBC News**: `https://feeds.bbci.co.uk/news/rss.xml`
- **CNN**: `https://rss.cnn.com/rss/edition.rss`
- **Reuters**: `https://feeds.reuters.com/reuters/topNews`
- **NPR**: `https://feeds.npr.org/1001/rss.xml`
- **TechCrunch**: `https://techcrunch.com/feed/`
- **The Guardian**: `https://www.theguardian.com/world/rss`
- **Associated Press**: `https://apnews.com/apf-topnews`

### Step 2: Restart the Server

After updating `.env`, restart your server:

```bash
# Stop the server (Ctrl+C)
# Then start again
uvicorn src.main:app --host 0.0.0.0 --port 5001 --reload
```

### Step 3: Trigger Scraping

```bash
curl -X POST http://localhost:5001/api/admin/scrape/rss
```

## Check RSS Feed Status

### View Configured Feeds

```bash
curl http://localhost:5001/api/admin/feeds
```

### Check System Status

```bash
curl http://localhost:5001/api/admin/status
```

## Test News Summarization

After scraping, test again:

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
        "parts": [{"kind": "text", "text": "summarize the latest news"}],
        "messageId": "msg-1"
      }
    }
  }'
```

## Troubleshooting

### No RSS Feeds Configured

If `RSS_FEEDS` is empty in your `.env`, the scraper won't have any feeds to scrape. Add at least one RSS feed URL.

### Scraping Fails

- Check internet connection
- Verify RSS feed URLs are accessible
- Check server logs for errors
- Try accessing a feed URL directly in your browser

### Still No Data After Scraping

- Check database: `curl http://localhost:5001/api/admin/status`
- Verify feeds were scraped: Check the `jobs_added` count in the scrape response
- Try fetching headlines first: `"fetch latest headlines"` before summarizing

