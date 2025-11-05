import logging
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4

from src.models.a2a import (
    A2AMessage,
    TaskResult,
    TaskStatus,
    Artifact,
    MessagePart,
    MessageConfiguration,
)
from src.services.ai import AIService
from src.services.rss_scraper import RSSFeedScraper


logger = logging.getLogger(__name__)


class NewsAgent:
    """Lightweight news insights agent using existing A2A architecture.

    Capabilities:
    - Fetch latest headlines from configured RSS feeds
    - Summarize headlines
    - Analyze sentiment/topics for a user-provided query or fetched headlines
    """

    def __init__(self, rss_scraper: RSSFeedScraper):
        self.rss_scraper = rss_scraper
        self.ai_service = AIService()
        self.conversations: Dict[str, List[A2AMessage]] = {}

    async def process_messages(
        self,
        messages: List[A2AMessage],
        context_id: Optional[str] = None,
        task_id: Optional[str] = None,
        config: Optional[MessageConfiguration] = None,
    ) -> TaskResult:
        try:
            if not messages:
                return self._create_error_result(
                    context_id, task_id, "No messages provided", messages
                )

            context_id = context_id or str(uuid4())
            task_id = task_id or str(uuid4())
            self.conversations.setdefault(context_id, []).extend(messages)

            user_text = self._extract_user_text(messages)
            reply_text, artifacts, state = await self._handle_intent(user_text, context_id)

            reply_message = A2AMessage(
                role="agent",
                parts=[MessagePart(kind="text", text=reply_text)],
                messageId=messages[0].messageId,
            )

            status = TaskStatus(state=state, message=reply_message)

            result = TaskResult(
                id=task_id,
                contextId=context_id,
                status=status,
                artifacts=artifacts,
                history=self.conversations.get(context_id, []),
            )
            return result
        except Exception as e:
            logger.error(f"NewsAgent error: {e}", exc_info=True)
            return self._create_error_result(context_id, task_id, str(e), messages)

    def _extract_user_text(self, messages: List[A2AMessage]) -> str:
        for msg in reversed(messages):
            if msg.role == "user":
                for part in msg.parts:
                    if part.kind == "text" and part.text:
                        return part.text
        return ""

    async def _handle_intent(self, user_text: str, context_id: str) -> Tuple[str, List[Artifact], str]:
        intent_data = await self.ai_service.classify_intent(user_text)
        intent = (intent_data or {}).get("intent") or "answer_question"
        entities = (intent_data or {}).get("entities", {})

        logger.info(f"[NewsAgent] Intent: {intent}, Entities: {entities}")

        handlers = {
            "fetch_latest": self._fetch_latest_headlines,
            "summarize_news": self._summarize_latest,
            "analyze_sentiment": lambda: self._analyze_sentiment(
                entities.get("topic", user_text)
            ),
            "answer_question": lambda: self._answer_question(user_text, context_id),
            "get_help": self._get_help,
        }

        handler = handlers.get(intent, lambda: self._answer_question(user_text, context_id))
        return await handler()

    async def _fetch_latest_headlines(self) -> Tuple[str, List[Artifact], str]:
        # Reuse RSSFeedScraper to fetch entries; we only surface titles/links
        # Check if RSS feeds are configured
        if not self.rss_scraper.rss_feeds:
            return (
                "No RSS feeds are configured. Please add RSS_FEEDS to your .env file.\n\n"
                "Example:\n"
                "RSS_FEEDS=https://feeds.bbci.co.uk/news/rss.xml,https://rss.cnn.com/rss/edition.rss\n\n"
                "After adding RSS feeds, restart the server and try again.",
                [],
                "completed"
            )
        
        logger.info(f"[NewsAgent] Fetching from {len(self.rss_scraper.rss_feeds)} RSS feeds")
        entries = await self.rss_scraper.fetch_all_feeds()
        
        if not entries:
            return (
                f"No headlines found. Checked {len(self.rss_scraper.rss_feeds)} RSS feed(s).\n\n"
                "Possible issues:\n"
                "- RSS feed URLs might be incorrect or inaccessible\n"
                "- Feeds might be empty or require authentication\n"
                "- Check server logs for detailed error messages\n\n"
                "You can check configured feeds at: GET /api/admin/feeds",
                [],
                "completed"
            )

        headlines = []
        headlines_data = []
        for e in entries[:15]:
            # Try multiple possible field names for title
            title = (
                e.get("position") 
                or e.get("title") 
                or e.get("raw_data", {}).get("title") 
                or e.get("raw_data", {}).get("position")
                or "Untitled"
            )
            # Try multiple possible field names for link
            link = (
                e.get("url") 
                or e.get("apply_url") 
                or e.get("link")
                or e.get("raw_data", {}).get("url")
                or ""
            )
            if title and title != "Untitled":
                headline_text = f"- {title}"
                if link:
                    headline_text += f" — {link}"
                headlines.append(headline_text)
                headlines_data.append({"title": title, "link": link})

        if not headlines:
            return ("No valid headlines found. The RSS feeds may not contain news data yet.", [], "completed")

        text = "Latest headlines:\n\n" + "\n".join(headlines)
        artifacts = [
            Artifact(
                name="headlines.json",
                parts=[MessagePart(kind="data", data=headlines_data)],
            )
        ]
        return (text, artifacts, "completed")

    async def _summarize_latest(self) -> Tuple[str, List[Artifact], str]:
        entries = await self.rss_scraper.fetch_all_feeds()
        if not entries:
            return ("No content to summarize. The RSS feeds may not have been scraped yet. Try fetching latest headlines first.", [], "completed")

        docs = []
        for e in entries[:20]:
            title = e.get("position") or e.get("raw_data", {}).get("title") or e.get("title", "")
            desc = e.get("description") or e.get("raw_data", {}).get("summary") or e.get("summary", "")
            if title:  # Only add entries with titles
                docs.append({"title": title, "summary": desc, "description": desc})

        if not docs:
            return ("No valid news content found to summarize.", [], "completed")

        summary = await self.ai_service.summarize_news(docs)
        return (summary, [], "completed")

    async def _analyze_sentiment(self, topic: str) -> Tuple[str, List[Artifact], str]:
        if not topic or topic.strip() == "":
            return ("Please specify a topic to analyze. Example: 'analyze sentiment on artificial intelligence'", [], "completed")

        entries = await self.rss_scraper.fetch_all_feeds()
        if not entries:
            return ("No news data available to analyze. The RSS feeds may need to be scraped first.", [], "completed")

        corpus = []
        for e in entries:
            # Try multiple possible field names
            title = (
                e.get("position") 
                or e.get("title") 
                or e.get("raw_data", {}).get("title") 
                or e.get("raw_data", {}).get("position")
                or ""
            )
            desc = (
                e.get("description") 
                or e.get("summary") 
                or e.get("raw_data", {}).get("summary")
                or e.get("raw_data", {}).get("description")
                or ""
            )
            text = f"{title}. {desc}".strip()
            if text and topic.lower() in text.lower():
                corpus.append(text)

        if not corpus:
            return (f"No recent headlines found about '{topic}'. Try a different topic or check if the RSS feeds contain relevant news.", [], "completed")

        # Use AIService free-form QA to get a sentiment/theme analysis
        prompt = (
            "Given the following news headlines and descriptions, provide a concise sentiment and theme "
            f"analysis about '{topic}'. Be specific and include notable subtopics. Focus on news sentiment, not job market data.\n\n"
            + "\n\n".join(corpus[:25])
        )
        answer = await self.ai_service.answer_question(prompt, {"topic": topic, "agent": "news"})
        return (answer, [], "completed")

    async def _answer_question(self, user_text: str, context_id: str) -> Tuple[str, List[Artifact], str]:
        # Generic fallback QA
        answer = await self.ai_service.answer_question(user_text, {"agent": "news"})
        return (answer, [], "completed")

    async def _get_help(self) -> Tuple[str, List[Artifact], str]:
        text = (
            "I can fetch latest headlines, summarize news, and analyze sentiment by topic.\n"
            "Examples: 'fetch latest', 'summarize news', 'analyze sentiment on AI'"
        )
        return (text, [], "completed")

    def _create_error_result(
        self,
        context_id: Optional[str],
        task_id: Optional[str],
        error_message: str,
        incoming: List[A2AMessage],
    ) -> TaskResult:
        context_id = context_id or str(uuid4())
        task_id = task_id or str(uuid4())
        error_reply = A2AMessage(
            role="agent",
            parts=[MessagePart(kind="text", text=f"Error: {error_message}")],
            messageId=incoming[0].messageId if incoming else str(uuid4()),
        )
        status = TaskStatus(state="failed", message=error_reply)
        return TaskResult(
            id=task_id,
            contextId=context_id,
            status=status,
            artifacts=[],
            history=incoming or [],
        )


