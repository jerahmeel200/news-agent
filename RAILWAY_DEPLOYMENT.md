# Railway Deployment Guide 🚂

This guide will help you deploy the News Agent to Railway.

## Prerequisites

1. A [Railway account](https://railway.app)
2. Your Google Gemini API key ([Get one here](https://ai.google.dev/))
3. Your project pushed to a Git repository (GitHub, GitLab, or Bitbucket)

**Note:** This project requires Python 3.12+. Railway supports Python 3.12, which is specified in `runtime.txt`. If you need Python 3.13, Railway may not support it yet - check Railway's documentation for the latest supported versions.

## Quick Deployment Steps

### 1. Connect Your Repository

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"** (or your Git provider)
4. Choose your `news-agent` repository
5. Railway will automatically detect it's a Python project

### 2. Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will create a PostgreSQL database and set the `DATABASE_URL` environment variable automatically

### 3. Configure Environment Variables

Go to your service settings → **Variables** tab and add:

```bash
# AI Service (REQUIRED)
API_KEY=your_gemini_api_key_here

# RSS Scraping Configuration
RATE_LIMIT=1440
RSS_SCRAPE_INTERVAL_MINUTES=1440

# RSS Feeds (comma-separated URLs)
RSS_FEEDS=https://feeds.bbci.co.uk/news/rss.xml,https://rss.cnn.com/rss/edition.rss,https://feeds.reuters.com/reuters/topNews,https://feeds.npr.org/1001/rss.xml

# Logging
LOG_LEVEL=INFO

# Database (Automatically set by Railway PostgreSQL service)
# DATABASE_URL is set automatically - don't override it!
```

**Important Notes:**
- `DATABASE_URL` is automatically set by Railway when you add a PostgreSQL database
- `PORT` is automatically set by Railway - don't override it
- `HOST` defaults to `0.0.0.0` in the Procfile - no need to set it

### 4. Initialize the Database

After the first deployment, you need to initialize the database:

1. Go to your service → **Deployments** tab
2. Click on the latest deployment
3. Click **"View Logs"**
4. In the logs, you'll see database initialization messages

Alternatively, you can run the initialization command manually:

1. Go to your service → **Settings** → **Service Settings**
2. Scroll to **"Run Command"** section
3. Temporarily set it to: `python -c "from src.db.session import init_db; init_db()"`
4. Deploy, then change it back to the default (or leave it empty to use Procfile)

### 5. Deploy

Railway will automatically:
- Detect Python from `requirements.txt`
- Install dependencies
- Use the `Procfile` to start the server
- Set up the database connection

## Configuration Files

### Procfile
```
web: uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-5001}
```

This tells Railway how to start your application. Railway automatically sets the `PORT` environment variable.

### railway.json
This file contains Railway-specific deployment configuration. It's optional but recommended.

## Verification

After deployment:

1. **Check Health Endpoint:**
   ```bash
   curl https://your-app-name.up.railway.app/health
   ```

2. **Check Root Endpoint:**
   ```bash
   curl https://your-app-name.up.railway.app/
   ```

3. **Test A2A Endpoint:**
   ```bash
   curl -X POST https://your-app-name.up.railway.app/a2a/news \
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

## Troubleshooting

### Database Connection Issues

If you see database errors:
1. Ensure PostgreSQL is added as a service
2. Check that `DATABASE_URL` is set (it should be automatic)
3. Verify the database is running (Railway dashboard)

### Port Issues

- Railway sets `PORT` automatically - don't override it
- The Procfile uses `${PORT:-5001}` as a fallback
- Make sure your Procfile is in the root directory

### API Key Issues

- Ensure `API_KEY` is set in Railway environment variables
- Check logs for "API_KEY environment variable is required" errors
- Verify the API key is valid at [Google AI Studio](https://aistudio.google.com/)

### Build Failures

- Check Python version: This project uses Python 3.12 (specified in `runtime.txt`). Railway supports Python 3.12, but if you need 3.13, verify Railway compatibility first
- Review `requirements.txt` for any missing dependencies
- Check build logs in Railway dashboard
- If build fails, try removing `runtime.txt` and let Railway auto-detect the Python version

### Application Not Starting

1. Check Railway logs for errors
2. Verify `Procfile` is in the root directory
3. Ensure `src/main.py` exists and is valid
4. Check that all environment variables are set correctly

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | ✅ Yes | - | Google Gemini API key |
| `DATABASE_URL` | ✅ Yes* | - | PostgreSQL connection string (auto-set by Railway) |
| `PORT` | ✅ Yes* | - | Server port (auto-set by Railway) |
| `RATE_LIMIT` | No | 1440 | RSS requests per day |
| `RSS_SCRAPE_INTERVAL_MINUTES` | No | 1440 | Scraping interval in minutes |
| `RSS_FEEDS` | No | - | Comma-separated RSS feed URLs |
| `LOG_LEVEL` | No | INFO | Logging level |
| `DATABASE_ECHO` | No | False | SQL query logging |

*Automatically set by Railway

## Custom Domain

1. Go to your service → **Settings** → **Networking**
2. Click **"Generate Domain"** or **"Custom Domain"**
3. Follow the DNS configuration instructions

## Monitoring

Railway provides:
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: Deployment history and status

Access these from your service dashboard.

## Cost Considerations

Railway offers:
- Free tier: $5 credit/month
- Pay-as-you-go pricing
- PostgreSQL database: ~$5/month for starter plan

Monitor your usage in the Railway dashboard.

## Support

- [Railway Documentation](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- Check application logs in Railway dashboard for errors

---

**Ready to deploy?** Push your code to GitHub and connect it to Railway! 🚀

