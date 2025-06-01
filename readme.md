# TeamCollab LLM Proxy

A lightweight OpenAI-compatible proxy server with team-based context injection.
Routes to OpenRouter by default.

## Features

- ✅ Accepts OpenAI-style `/v1/chat/completions` requests
- ✅ Validates API keys (you issue)
- ✅ Injects shared/team chat context
- ✅ Streams responses from upstream
- ✅ Uses OpenRouter (can be changed to OpenAI, Anthropic, etc.)

## Setup

```bash
git clone https://github.com/yourname/proxy-llm
cd proxy-llm

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export OPENROUTER_API_KEY=your-openrouter-key
uvicorn main:app --host 0.0.0.0 --port 4000

