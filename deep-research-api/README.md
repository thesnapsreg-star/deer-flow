# Deep Research API & MCP Server

A standalone multi-agent deep research framework extracted from DeerFlow, providing both REST API and MCP (Model Context Protocol) server implementations.

## Overview

This package provides a sophisticated multi-agent research system that can:
- Conduct comprehensive research on any topic
- Plan and execute multi-step research workflows
- Gather information from web searches
- Analyze data and perform computations
- Generate detailed research reports in multiple styles

### Architecture

The system uses specialized AI agents:
- **Coordinator**: Handles user queries and clarifications
- **Planner**: Creates structured research plans
- **Researcher**: Performs web searches and information gathering
- **Coder**: Analyzes data and performs calculations
- **Reporter**: Synthesizes findings into comprehensive reports

## Quick Start

### 1. Installation

```bash
cd deep-research-api
pip install -e .
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required configuration:
- `OPENAI_API_KEY`: Your OpenAI API key
- `TAVILY_API_KEY`: Your Tavily search API key (optional but recommended)

### 3. Start the API Server

```bash
# Start API server
python -m api.main

# Server will be available at http://localhost:8080
```

### 4. Install MCP Server for Claude Code

```bash
# Run the installation script
./install-mcp.sh

# Restart Claude Code to load the MCP server
```

## API Usage

### REST API Endpoints

#### Health Check
```bash
curl http://localhost:8080/health
```

#### Synchronous Research
```bash
curl -X POST http://localhost:8080/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest developments in quantum computing?",
    "max_step_num": 5,
    "report_style": "academic"
  }'
```

#### Streaming Research
```bash
curl -X POST http://localhost:8080/research/stream \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze the current state of AI safety research",
    "max_step_num": 3
  }'
```

### Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | The research question or topic |
| `max_step_num` | integer | 5 | Maximum number of research steps |
| `max_plan_iterations` | integer | 1 | Maximum plan iterations |
| `enable_clarification` | boolean | true | Enable multi-turn clarification |
| `enable_background_investigation` | boolean | true | Enable pre-planning background search |
| `auto_accept_plan` | boolean | true | Auto-accept the research plan |
| `report_style` | string | "academic" | Report style (academic, news, social, investment) |
| `locale` | string | "en-US" | Research locale |

### Response Format

```json
{
  "research_id": "uuid",
  "query": "research question",
  "plan": {
    "title": "Research Plan Title",
    "thought": "Planning rationale",
    "steps": [
      {
        "title": "Step title",
        "description": "Step description",
        "step_type": "research",
        "need_search": true,
        "status": "completed",
        "execution_result": "Result summary"
      }
    ],
    "has_enough_context": true,
    "locale": "en-US"
  },
  "final_report": "Comprehensive research report...",
  "observations": ["key finding 1", "key finding 2"],
  "resources": [
    {
      "url": "https://example.com",
      "title": "Source title"
    }
  ],
  "locale": "en-US",
  "metadata": {}
}
```

## MCP Server Usage

### Available Tools

Once installed in Claude Code, two tools are available:

#### 1. `deep_research`
Comprehensive research with full multi-agent workflow.

**Use cases:**
- Complex research questions
- Market analysis
- Technical investigations
- Academic research
- Competitive intelligence

**Example:**
```
Use the deep_research tool to analyze the competitive landscape
of electric vehicles in 2024, focusing on battery technology
and market share.
```

#### 2. `quick_research`
Fast research with reduced steps for quick answers.

**Use cases:**
- Quick fact-checking
- Simple questions
- Preliminary research
- Rapid results needed

**Example:**
```
Use quick_research to find out when Python 3.13 was released
and what are its main new features.
```

### MCP Configuration

The MCP server configuration is automatically added to:
```
~/.config/claude-code/mcp.json
```

Manual configuration:
```json
{
  "mcpServers": {
    "deep-research": {
      "command": "python",
      "args": ["-m", "mcp-server.server"],
      "cwd": "/path/to/deep-research-api",
      "env": {
        "PYTHONPATH": "/path/to/deep-research-api"
      },
      "timeout": 300000
    }
  }
}
```

## Development

### Project Structure

```
deep-research-api/
├── api/                          # REST API
│   ├── main.py                  # FastAPI application
│   ├── models.py                # Request/response models
│   └── config.py                # Configuration
├── mcp-server/                  # MCP Server
│   └── server.py                # MCP server implementation
├── research-core/               # Core research framework
│   ├── agents/                  # Agent definitions
│   ├── config/                  # Agent configurations
│   ├── graph/                   # LangGraph workflow
│   ├── llms/                    # LLM providers
│   ├── prompts/                 # Agent prompts
│   ├── tools/                   # Research tools
│   ├── utils/                   # Utilities
│   └── workflow.py              # Workflow orchestration
├── pyproject.toml               # Package configuration
├── .env.example                 # Environment template
├── mcp-config.json              # MCP client config
└── install-mcp.sh               # MCP installation script
```

### Running Tests

```bash
# Start API server
python -m api.main

# Test health endpoint
curl http://localhost:8080/health

# Test research endpoint
curl -X POST http://localhost:8080/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is quantum computing?", "max_step_num": 2}'

# Test MCP server (requires Claude Code)
# Just use the tools in Claude Code after installation
```

### Customization

#### Adding New Report Styles

Edit `research-core/prompts/reporter.md` to add new report styles.

#### Configuring Models

Edit `.env` to customize which models are used for each agent:
```env
COORDINATOR_MODEL=gpt-4o-mini
PLANNER_MODEL=gpt-4o
RESEARCHER_MODEL=gpt-4o-mini
CODER_MODEL=gpt-4o-mini
REPORTER_MODEL=gpt-4o
```

#### Adding Search Providers

Edit `research-core/tools/search.py` to add new search providers.

## Troubleshooting

### API Server Issues

**Server won't start:**
- Check if port 8080 is already in use: `lsof -i :8080`
- Change port in `.env`: `API_PORT=8081`

**API requests fail:**
- Verify `.env` configuration
- Check API keys are valid
- Review logs for error details

### MCP Server Issues

**Tools not appearing in Claude Code:**
- Restart Claude Code after installation
- Check MCP config: `cat ~/.config/claude-code/mcp.json`
- Verify API server is running
- Check MCP server logs

**Research fails:**
- Ensure API server is running at http://localhost:8080
- Check API server logs
- Verify environment variables are set correctly

**Connection timeout:**
- Increase timeout in `mcp-config.json`: `"timeout": 600000`
- Reduce research steps: use `max_steps: 2` or `quick_research` tool

## Performance Tips

1. **Use quick_research for simple queries** - It's 2-3x faster
2. **Adjust max_step_num** - Fewer steps = faster results
3. **Disable clarification** - For programmatic use, set `enable_clarification: false`
4. **Cache results** - Store research results to avoid re-running identical queries

## API Examples

### Python Client

```python
import httpx
import asyncio

async def research(query: str):
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            "http://localhost:8080/research",
            json={
                "query": query,
                "max_step_num": 3,
                "report_style": "academic"
            }
        )
        return response.json()

# Run research
result = asyncio.run(research("What is quantum entanglement?"))
print(result["final_report"])
```

### JavaScript/Node.js Client

```javascript
async function research(query) {
  const response = await fetch('http://localhost:8080/research', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      max_step_num: 3,
      report_style: 'academic'
    })
  });

  return await response.json();
}

// Run research
research('What is quantum entanglement?')
  .then(result => console.log(result.final_report));
```

## License

This package is extracted from the DeerFlow project. Please refer to the original project's license.

## Contributing

This is a standalone extraction from DeerFlow. For contributions to the main framework, please visit the original repository.

## Credits

Extracted from [DeerFlow](https://github.com/yourusername/deer-flow) - Deep Exploration and Efficient Research Flow
