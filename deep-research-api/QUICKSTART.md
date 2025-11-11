# Quick Start Guide

Get the Deep Research API and MCP server running in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- pip or uv package manager
- OpenAI API key
- (Optional) Tavily API key for better search results

## Installation Steps

### 1. Install Package

```bash
cd deep-research-api
pip install -e .
```

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env

# Add your API keys
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
echo "TAVILY_API_KEY=tvly-your-key-here" >> .env
```

### 3. Start API Server

```bash
python -m api.main
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### 4. Test the API

In a new terminal:

```bash
# Health check
curl http://localhost:8080/health

# Simple research
curl -X POST http://localhost:8080/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is LangGraph?", "max_step_num": 2}'
```

### 5. Install MCP Server (for Claude Code)

```bash
./install-mcp.sh
```

Restart Claude Code, and you'll see two new tools:
- `deep_research`
- `quick_research`

## Usage Examples

### Example 1: Simple Research

**Query:** "What are the main features of Python 3.13?"

```bash
curl -X POST http://localhost:8080/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main features of Python 3.13?",
    "max_step_num": 2,
    "report_style": "academic"
  }' | jq '.final_report'
```

### Example 2: Market Analysis

**Query:** "Analyze the current state of the EV battery market"

```bash
curl -X POST http://localhost:8080/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze the current state of the EV battery market",
    "max_step_num": 5,
    "report_style": "investment",
    "enable_background_investigation": true
  }' | jq '.'
```

### Example 3: Using in Claude Code

Once the MCP server is installed, just ask Claude:

```
Use the deep_research tool to investigate recent advances
in quantum computing error correction, focusing on papers
from 2024.
```

Claude will automatically:
1. Call the deep_research tool
2. Wait for the API to complete research
3. Present the findings in a readable format

### Example 4: Quick Facts

For quick lookups, use the quick_research tool:

```
Use quick_research to find out what version of Node.js
is currently LTS and when it was released.
```

## Tips for Best Results

### 1. Be Specific in Queries
❌ "Tell me about AI"
✅ "What are the current limitations of large language models in reasoning tasks?"

### 2. Choose the Right Tool
- **deep_research**: Complex topics, comprehensive analysis (5+ steps)
- **quick_research**: Simple facts, quick lookups (2 steps)

### 3. Select Appropriate Report Style
- **academic**: Technical depth, citations, formal tone
- **news**: Current events, journalistic style
- **social**: Casual, digestible, social media format
- **investment**: Business focus, financial implications

### 4. Adjust Steps Based on Complexity
- **2 steps**: Quick facts, simple questions
- **3-5 steps**: Standard research (recommended)
- **6-8 steps**: Comprehensive deep dives
- **9+ steps**: Extremely thorough (may be slow)

## Common Issues

### Issue: "Connection refused"
**Solution:** Make sure the API server is running:
```bash
python -m api.main
```

### Issue: "Authentication error"
**Solution:** Check your API keys in `.env`:
```bash
cat .env | grep API_KEY
```

### Issue: "Tools not showing in Claude Code"
**Solution:**
1. Restart Claude Code
2. Check MCP config: `cat ~/.config/claude-code/mcp.json`
3. Verify the path in mcp-config.json is correct

### Issue: "Request timeout"
**Solution:** Reduce complexity:
```bash
# Use fewer steps
{"query": "...", "max_step_num": 2}

# Or use quick_research tool
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [API documentation](API.md)
- Customize agent prompts in `research-core/prompts/`
- Add custom tools in `research-core/tools/`

## Support

For issues or questions:
1. Check the troubleshooting section in README.md
2. Review API server logs
3. Check MCP server logs in Claude Code

Enjoy researching! 🔬
