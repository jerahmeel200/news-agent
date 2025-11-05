#!/bin/bash

# News Agent API Testing Script
# This script provides examples for testing the News Agent API locally

BASE_URL="http://localhost:5001"

echo "=========================================="
echo "News Agent API Testing Examples"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Health Check
echo -e "${BLUE}1. Health Check${NC}"
curl -s "$BASE_URL/health" | python -m json.tool
echo ""
echo ""

# 2. Root Endpoint
echo -e "${BLUE}2. Root Endpoint (API Info)${NC}"
curl -s "$BASE_URL/" | python -m json.tool
echo ""
echo ""

# 3. Fetch Latest Headlines
echo -e "${BLUE}3. Fetch Latest Headlines${NC}"
curl -s -X POST "$BASE_URL/a2a/news" \
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
  }' | python -m json.tool
echo ""
echo ""

# 4. Summarize News
echo -e "${BLUE}4. Summarize Latest News${NC}"
curl -s -X POST "$BASE_URL/a2a/news" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-002",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "summarize the latest news"
          }
        ],
        "messageId": "msg-002"
      }
    }
  }' | python -m json.tool
echo ""
echo ""

# 5. Analyze Sentiment
echo -e "${BLUE}5. Analyze Sentiment on AI${NC}"
curl -s -X POST "$BASE_URL/a2a/news" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-003",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "analyze sentiment on artificial intelligence"
          }
        ],
        "messageId": "msg-003"
      }
    }
  }' | python -m json.tool
echo ""
echo ""

# 6. Ask a Question
echo -e "${BLUE}6. Ask a Question${NC}"
curl -s -X POST "$BASE_URL/a2a/news" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-004",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "What are the latest developments in technology?"
          }
        ],
        "messageId": "msg-004"
      }
    }
  }' | python -m json.tool
echo ""
echo ""

# 7. Get Help
echo -e "${BLUE}7. Get Help${NC}"
curl -s -X POST "$BASE_URL/a2a/news" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-005",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "help"
          }
        ],
        "messageId": "msg-005"
      }
    }
  }' | python -m json.tool
echo ""
echo ""

# 8. Execute Method (Multi-turn)
echo -e "${BLUE}8. Execute Method (Multi-turn Conversation)${NC}"
curl -s -X POST "$BASE_URL/a2a/news" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-006",
    "method": "execute",
    "params": {
      "contextId": "ctx-001",
      "taskId": "task-001",
      "messages": [
        {
          "kind": "message",
          "role": "user",
          "parts": [
            {
              "kind": "text",
              "text": "fetch latest headlines"
            }
          ],
          "messageId": "msg-006"
        }
      ]
    }
  }' | python -m json.tool
echo ""
echo ""

echo -e "${GREEN}=========================================="
echo "All tests completed!"
echo "==========================================${NC}"

