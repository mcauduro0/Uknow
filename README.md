# UKNOW - Multi-Agent AI Research System

A channel-agnostic AI orchestration system that coordinates multiple LLMs for deep research and business intelligence tasks.

## Architecture Overview

UKNOW uses a multi-agent debate architecture where different AI models challenge and refine each other's analysis before producing a final research report.

```
User Question
      ↓
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐     ┌──────────────────┐              │
│  │ SPARRING PARTNER │ ←→  │  DEBATE ANALYST  │              │
│  │    (OpenAI)      │     │    (Claude)      │              │
│  │                  │     │                  │              │
│  │ • Challenge      │     │ • Critique       │              │
│  │ • Question       │     │ • Expand         │              │
│  │ • Identify gaps  │     │ • Structure      │              │
│  └────────┬─────────┘     └────────┬─────────┘              │
│           │                        │                         │
│           └────────────┬───────────┘                         │
│                        ↓                                     │
│              ┌──────────────────┐                            │
│              │  DEEP RESEARCHER │                            │
│              │    (Gemini)      │                            │
│              │                  │                            │
│              │ • Research       │                            │
│              │ • Analyze        │                            │
│              │ • Recommend      │                            │
│              └────────┬─────────┘                            │
│                       ↓                                      │
│              ┌──────────────────┐                            │
│              │    PACKAGERS     │                            │
│              │                  │                            │
│              │ • Slides (Manus) │                            │
│              │ • App (Replit)   │                            │
│              └──────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
      ↓
Final Output (Report / Slides / App Spec)
```

## Agent Roles

### 1. Sparring Partner (OpenAI GPT)
- Challenges assumptions
- Identifies blind spots
- Asks clarifying questions
- Prepares initial research brief

### 2. Debate Analyst (Anthropic Claude)
- Critiques Sparring Partner's analysis
- Adds strategic perspectives
- Suggests research structure
- Produces final research brief

### 3. Deep Researcher (Google Gemini)
- Executes comprehensive research
- Produces structured analysis
- Provides prioritized recommendations
- Acknowledges uncertainties

### 4. Packagers
- **Slides Packager**: Transforms report into presentation outline
- **App Packager**: Creates app/webpage specification

## Processing Flow

1. **Round 1**: Sparring Partner analyzes the user's question
2. **Round 1**: Debate Analyst critiques and expands
3. **Round 2**: Sparring Partner refines based on critique
4. **Round 2**: Debate Analyst produces final brief
5. **Research**: Deep Researcher executes the investigation
6. **Packaging**: Output is formatted for delivery

### Quick Mode

For faster results, quick mode skips the second debate round:
1. Sparring Round 1 → Claude Round 1 → Gemini Research → Packaging

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/uknow.git
cd uknow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
```

## Configuration

Edit `.env` with your API keys:

```env
# OpenAI (Sparring Partner)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic (Debate Analyst)
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Google AI (Deep Researcher)
GOOGLE_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.0-flash-exp

# Optional: WhatsApp Channel
WHATSAPP_PHONE_NUMBER_ID=your-phone-id
WHATSAPP_ACCESS_TOKEN=your-token
WHATSAPP_VERIFY_TOKEN=your-verify-token
```

## Running the API

```bash
# Development mode with auto-reload
python -m uknow

# Or using uvicorn directly
uvicorn uknow.api.app:app --reload --host 0.0.0.0 --port 8000
```

API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Tasks

```bash
# Create a new task (async)
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key trends in AI for 2025?",
    "output_format": "report",
    "quick_mode": false
  }'

# Get task status and results
curl http://localhost:8000/api/v1/tasks/{task_id}

# List all tasks
curl http://localhost:8000/api/v1/tasks

# Create and process synchronously (for testing)
curl -X POST http://localhost:8000/api/v1/tasks/sync \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Analyze the competitive landscape of cloud computing",
    "output_format": "slides",
    "quick_mode": true
  }'
```

### Webhooks

```bash
# Generic webhook (for custom integrations)
curl -X POST http://localhost:8000/webhooks/generic \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "slack",
    "user_id": "U123456",
    "question": "Research question here",
    "callback_url": "https://your-callback.com/results"
  }'
```

## Output Formats

### Report (Default)
Full JSON research output with:
- Executive summary
- Detailed analysis
- Prioritized recommendations
- References

### Slides
Presentation outline ready for Manus or GenSpark:
```json
{
  "slides": [
    {
      "number": 1,
      "title": "Executive Summary",
      "bullet_points": ["Key finding 1", "Key finding 2"]
    }
  ]
}
```

### App
Application specification for Replit Agent:
```json
{
  "general_description": "...",
  "features": ["..."],
  "screens_or_sections": [...],
  "suggested_stack": "React + Tailwind"
}
```

## Project Structure

```
uknow/
├── src/uknow/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── config.py            # Settings management
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py          # Base agent classes
│   │   ├── prompts.py       # System prompts
│   │   ├── sparring.py      # OpenAI Sparring Partner
│   │   ├── debate.py        # Claude Debate Analyst
│   │   ├── researcher.py    # Gemini Deep Researcher
│   │   └── packagers.py     # Output packagers
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py          # Task state machine
│   │   └── agents.py        # Agent I/O models
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── core.py          # Main orchestrator
│   │   └── runner.py        # Task runner
│   └── api/
│       ├── __init__.py
│       ├── app.py           # FastAPI app
│       └── routes/
│           ├── health.py
│           ├── tasks.py
│           └── webhooks.py
├── pyproject.toml
├── requirements.txt
├── .env.example
└── README.md
```

## Task States

```
RECEIVED → SPARRING_ROUND_1 → CLAUDE_ROUND_1 → SPARRING_ROUND_2
    → CLAUDE_ROUND_2 → GEMINI_RESEARCH → PACKAGING → COMPLETED
                           ↓
                         ERROR
```

## Channel Integration

UKNOW is designed to be channel-agnostic. Currently supported:

1. **Web API**: Direct REST API access
2. **WhatsApp Business**: Via Meta Cloud API webhooks
3. **Generic Webhook**: Custom integration point with callbacks

### Adding New Channels

1. Create a new webhook handler in `api/routes/webhooks.py`
2. Extract the user's question from the channel's message format
3. Create a task with appropriate metadata
4. Process and send results back via the channel's API

## Development

```bash
# Run tests
pytest

# Format code
black src/

# Lint
ruff check src/

# Type checking
mypy src/
```

## Roadmap

### MVP 1 (Current)
- [x] Core multi-agent architecture
- [x] Web API with async processing
- [x] Report output format
- [x] Quick mode support

### MVP 2
- [ ] Database persistence (PostgreSQL)
- [ ] Redis for task queues
- [ ] WhatsApp integration testing
- [ ] Slides output with Manus integration

### MVP 3
- [ ] App output with Replit integration
- [ ] User authentication
- [ ] Usage metrics dashboard
- [ ] Rate limiting and cost controls

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

For issues and feature requests, please use the GitHub issue tracker.
