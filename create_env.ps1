# PowerShell script to create .env file for News Agent

Write-Host "Creating .env file for News Agent..." -ForegroundColor Cyan

$envContent = @"
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
"@

$envPath = ".env"

if (Test-Path $envPath) {
    Write-Host ".env file already exists!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to overwrite it? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Cancelled. Exiting." -ForegroundColor Red
        exit
    }
}

$envContent | Out-File -FilePath $envPath -Encoding utf8

Write-Host ""
Write-Host "✅ .env file created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  IMPORTANT: Edit .env file and add your Gemini API key!" -ForegroundColor Yellow
Write-Host "   Get your API key from: https://ai.google.dev/" -ForegroundColor Yellow
Write-Host ""
Write-Host "After updating API_KEY, restart your server with:" -ForegroundColor Cyan
Write-Host "   uvicorn src.main:app --host 0.0.0.0 --port 5001 --reload" -ForegroundColor Cyan

