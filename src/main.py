from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
import asyncio
import httpx

from src.models.a2a import JSONRPCRequest, JSONRPCResponse, A2AMessage, MessagePart
from src.services.news_agent import NewsAgent
from src.services.rss_scraper import RSSFeedScraper, run_scheduled_rss_scraping
from src.db.session import init_db, get_db
from src.routers import admin, ai
from sqlalchemy.orm import Session

load_dotenv()


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

news_agent = None
rss_scraper_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global news_agent, rss_scraper_task

    logger.info("Starting News Agent...")

    init_db()
    logger.info("Database initialized")

    rss_scraper = RSSFeedScraper(rate_limit=int(os.getenv("RATE_LIMIT", 1440)))
    news_agent = NewsAgent(rss_scraper=rss_scraper)
    logger.info("Agent initialized: news")

    logger.info("Performing initial job scrape...")
    try:
        initial_result = await rss_scraper.scrape_and_store()
        logger.info(f"Initial job scrape completed: {initial_result}")
    except Exception as e:
        logger.error(f"Initial job scrape failed: {e}")

    rss_scrape_interval = int(os.getenv("RSS_SCRAPE_INTERVAL_MINUTES", 1440))
    rss_scraper_task = asyncio.create_task(
        run_scheduled_rss_scraping(
            rss_scraper, interval_minutes=rss_scrape_interval, skip_first=True
        )
    )
    logger.info(
        f"RSS background scraping started (interval: {rss_scrape_interval} minutes)"
    )

    yield

    if rss_scraper_task:
        rss_scraper_task.cancel()
        try:
            await rss_scraper_task
        except asyncio.CancelledError:
            pass

    logger.info("Agents shut down")


app = FastAPI(
    title="News Agent",
    description="AI agent for news: headlines, summaries, and sentiment via A2A",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(ai.router)


@app.post("/a2a/news")
async def a2a_news_endpoint(request: Request):
    """A2A endpoint for the NewsAgent"""
    try:
        body = await request.json()
        logger.info(
            f"[NEWS] Received A2A request: method={body.get('method')}, id={body.get('id')}"
        )

        if body.get("jsonrpc") != "2.0" or "id" not in body:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: jsonrpc must be '2.0' and id is required",
                    },
                },
            )

        rpc_request = JSONRPCRequest(**body)

        messages = []
        context_id = None
        task_id = None
        config = None

        if rpc_request.method == "message/send":
            msg = rpc_request.params.message
            user_text = ""
            for part in msg.parts:
                if part.kind == "text" and part.text:
                    user_text = part.text
                    break
            messages = [
                A2AMessage(
                    kind=msg.kind,
                    role=msg.role,
                    parts=[MessagePart(kind="text", text=user_text)],
                    messageId=msg.messageId,
                )
            ]
            config = rpc_request.params.configuration
        elif rpc_request.method == "execute":
            messages = rpc_request.params.messages or []
            context_id = rpc_request.params.contextId
            task_id = rpc_request.params.taskId

        result = await news_agent.process_messages(
            messages=messages, context_id=context_id, task_id=task_id, config=config
        )

        if messages and messages[0].messageId:
            incoming_message_id = messages[0].messageId
            if hasattr(result, "id"):
                result.id = incoming_message_id
            if hasattr(result, "status") and hasattr(result.status, "message"):
                result.status.message.messageId = incoming_message_id

        response = JSONRPCResponse(id=rpc_request.id, result=result)
        return response.model_dump()
    except Exception as e:
        logger.error(f"[NEWS] Error in A2A endpoint: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": body.get("id") if "body" in locals() else None,
                "error": {"code": -32603, "message": "Internal error", "data": {"details": str(e)}},
            },
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from src.db.repository import JobRepository
    from src.db.session import get_db_context

    try:
        with get_db_context() as db:
            total_jobs = JobRepository.get_total_jobs(db)
            jobs_24h = JobRepository.get_jobs_count_by_period(db, hours=24)
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        total_jobs = -1
        jobs_24h = -1

    return {
        "status": "healthy",
        "agent": "news-agent",
        "version": "1.0.0",
        "database": {
            "connected": total_jobs >= 0,
            "total_jobs": total_jobs,
            "jobs_last_24h": jobs_24h,
        },
        "scrapers": {
            "rss_enabled": True,
            "api_enabled": False,
        },
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "News Agent",
        "version": "1.0.0",
        "description": "AI agent: news headlines, summaries, and sentiment",
        "endpoints": {"a2a_news": "/a2a/news", "health": "/health", "docs": "/docs"},
        "capabilities": [
            "Fetch and summarize latest headlines",
            "Analyze sentiment on topics across recent news",
            "A2A protocol support for AI agents",
        ],
    }
