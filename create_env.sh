#!/bin/bash

# Bash script to create .env file for News Agent

echo "Creating .env file for News Agent..."

if [ -f ".env" ]; then
    echo ".env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " response
    if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
        echo "Cancelled. Exiting."
        exit 1
    fi
fi

cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=sqlite:///./news_agent.db

# Server Configuration
PORT=5001
HOST=0.0.0.0
LOG_LEVEL=INFO

# RSS Scraping Configuration
RATE_LIMIT=1440
RSS_SCRAPE_INTERVAL_MINUTES=1440

# RSS Feeds (comma-separated URLs)
# Add your news RSS feed URLs here
RSS_FEEDS=https://feeds.bbci.co.uk/news/rss.xml,https://rss.cnn.com/rss/edition.rss,https://feeds.reuters.com/reuters/topNews,https://feeds.npr.org/1001/rss.xml

# AI Service - Google Gemini API Key (REQUIRED)
# Get your API key from: https://ai.google.dev/
# Replace 'your_gemini_api_key_here' with your actual API key
API_KEY=your_gemini_api_key_here
EOF

echo ""
echo "✅ .env file created successfully!"
echo ""
echo "⚠️  IMPORTANT: Edit .env file and add your Gemini API key!"
echo "   Get your API key from: https://ai.google.dev/"
echo ""
echo "After updating API_KEY, restart your server with:"
echo "   uvicorn src.main:app --host 0.0.0.0 --port 5001 --reload"

