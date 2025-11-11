# Deep Research API Documentation

Complete API reference for the Deep Research REST API.

## Base URL

```
http://localhost:8080
```

## Authentication

Currently no authentication is required. For production use, consider adding API key authentication.

## Endpoints

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "models_available": [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4o-mini",
    "gpt-4o"
  ]
}
```

### POST /research

Synchronous research endpoint. Performs complete research and returns final results.

**Request Body:**
```json
{
  "query": "string (required)",
  "max_step_num": "integer (optional, default: 5)",
  "max_plan_iterations": "integer (optional, default: 1)",
  "enable_clarification": "boolean (optional, default: true)",
  "enable_background_investigation": "boolean (optional, default: true)",
  "auto_accept_plan": "boolean (optional, default: true)",
  "report_style": "string (optional, default: 'academic')",
  "locale": "string (optional, default: 'en-US')"
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | Yes | - | The research question or topic to investigate |
| max_step_num | integer | No | 5 | Maximum number of research steps to execute (1-10 recommended) |
| max_plan_iterations | integer | No | 1 | Maximum times to regenerate the research plan |
| enable_clarification | boolean | No | true | Enable multi-turn clarification for vague queries |
| enable_background_investigation | boolean | No | true | Enable pre-planning background web search |
| auto_accept_plan | boolean | No | true | Automatically accept the research plan without human review |
| report_style | string | No | "academic" | Style of the final report: "academic", "news", "social", "investment" |
| locale | string | No | "en-US" | Locale for research (affects language and regional sources) |

**Response:**
```json
{
  "research_id": "uuid",
  "query": "string",
  "plan": {
    "title": "string",
    "thought": "string",
    "steps": [
      {
        "title": "string",
        "description": "string",
        "step_type": "research|processing",
        "need_search": "boolean",
        "status": "completed",
        "execution_result": "string|null"
      }
    ],
    "has_enough_context": "boolean",
    "locale": "string"
  },
  "final_report": "string",
  "observations": ["string"],
  "resources": [
    {
      "url": "string",
      "title": "string"
    }
  ],
  "locale": "string",
  "metadata": {}
}
```

**Status Codes:**
- `200 OK`: Research completed successfully
- `500 Internal Server Error`: Research workflow failed

**Example:**
```bash
curl -X POST http://localhost:8080/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest developments in quantum computing?",
    "max_step_num": 5,
    "report_style": "academic",
    "enable_clarification": false
  }'
```

### POST /research/stream

Streaming research endpoint. Returns progress updates as Server-Sent Events (SSE).

**Request Body:**
Same as `/research` endpoint.

**Response:**
Stream of Server-Sent Events (SSE) with progress updates.

**Event Format:**
```
data: {"stage": "coordinator", "message": "Processing: coordinator", ...}

data: {"stage": "planner", "message": "Processing: planner", ...}

data: {"stage": "researcher", "message": "Processing: researcher", ...}
```

**Progress Event Schema:**
```json
{
  "stage": "string",
  "message": "string",
  "plan": "object|null",
  "current_step": "integer|null",
  "total_steps": "integer|null",
  "observations": ["string"]|null
}
```

**Example:**
```bash
curl -X POST http://localhost:8080/research/stream \
  -H "Content-Type: application/json" \
  -N \
  -d '{
    "query": "Analyze the impact of AI on healthcare",
    "max_step_num": 3
  }'
```

**JavaScript Example:**
```javascript
const eventSource = new EventSource('/research/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'What is quantum computing?',
    max_step_num: 3
  })
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Stage: ${data.stage}`, data.message);
};
```

## Report Styles

### Academic
Formal, technical, with citations and structured sections.

**Best for:**
- Technical research
- Scientific topics
- Academic papers
- Detailed analysis

**Example output:**
```markdown
# Abstract
This report examines...

## Introduction
Quantum computing represents...

## Methodology
The research approach...

## Findings
1. Technical Detail 1
2. Technical Detail 2

## Conclusion
Based on the analysis...

## References
[1] Source 1
[2] Source 2
```

### News
Journalistic style, current events focus.

**Best for:**
- Current events
- Breaking news
- Market updates
- Industry trends

**Example output:**
```markdown
# Quantum Computing Breakthrough Announced

In a major development today...

## Key Developments
- Google announces...
- IBM reveals...

## Expert Opinions
Industry experts suggest...

## What's Next
Looking ahead...
```

### Social
Casual, digestible, shareable format.

**Best for:**
- Social media content
- Blog posts
- Newsletter content
- Quick summaries

**Example output:**
```markdown
🚀 What's the deal with Quantum Computing?

Here's what you need to know 👇

💡 Key Points:
• Point 1
• Point 2
• Point 3

🔥 Why it matters:
This changes everything because...

📊 By the numbers:
• Stat 1
• Stat 2
```

### Investment
Business-focused, financial implications.

**Best for:**
- Market analysis
- Investment research
- Business intelligence
- Strategic planning

**Example output:**
```markdown
# Investment Thesis: Quantum Computing Sector

## Executive Summary
Market opportunity...

## Market Analysis
- Market size: $X billion
- Growth rate: Y%
- Key players: A, B, C

## Investment Considerations
### Opportunities
- Opportunity 1
- Opportunity 2

### Risks
- Risk 1
- Risk 2

## Recommendation
Based on analysis...
```

## Error Handling

All errors return a JSON response:

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "research_id": "uuid|null"
}
```

**Common Errors:**

| Error | Status | Cause | Solution |
|-------|--------|-------|----------|
| Missing API key | 500 | OPENAI_API_KEY not set | Set in .env file |
| Invalid query | 500 | Empty or malformed query | Provide valid query string |
| Timeout | 500 | Research took too long | Reduce max_step_num |
| Rate limit | 500 | API rate limit hit | Wait and retry |

## Rate Limiting

Currently no rate limiting. For production:
- Implement API key-based rate limiting
- Add request queuing
- Set maximum concurrent requests

## Performance

**Typical Response Times:**

| Steps | Time | Use Case |
|-------|------|----------|
| 1-2 | 30-60s | Quick facts |
| 3-5 | 1-2 min | Standard research |
| 6-8 | 2-4 min | Deep research |
| 9+ | 4+ min | Comprehensive analysis |

**Optimization Tips:**
1. Use fewer steps for faster results
2. Disable clarification for programmatic use
3. Cache results for repeated queries
4. Use streaming endpoint for real-time updates

## Examples

### Minimal Request
```bash
curl -X POST http://localhost:8080/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is LangGraph?"}'
```

### Full Configuration
```bash
curl -X POST http://localhost:8080/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Comprehensive analysis of renewable energy trends",
    "max_step_num": 8,
    "max_plan_iterations": 2,
    "enable_clarification": false,
    "enable_background_investigation": true,
    "auto_accept_plan": true,
    "report_style": "investment",
    "locale": "en-US"
  }'
```

### Python Client
```python
import httpx

async def research(query: str, steps: int = 5):
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            "http://localhost:8080/research",
            json={
                "query": query,
                "max_step_num": steps,
                "report_style": "academic",
                "enable_clarification": False,
            }
        )
        result = response.json()
        return result["final_report"]
```

## Versioning

Current version: **0.1.0**

Future versions will use semantic versioning and include the version in the URL:
```
http://localhost:8080/v1/research
```

## Support

For issues or questions:
- Check server logs
- Review [README.md](README.md) troubleshooting section
- Ensure all environment variables are set correctly
