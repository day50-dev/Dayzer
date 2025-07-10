A lightweight OpenAI-compatible proxy server with team-based context injection.
Routes to OpenRouter by default.

## Features

- ✅ Accepts OpenAI-style `/v1/chat/completions` requests
- ✅ Validates API keys (you issue)
- ✅ Injects shared/team chat context
- ✅ Streams responses from upstream
- ✅ Uses OpenRouter (can be changed to OpenAI, Anthropic, etc.)

## Setup

Dayzer is a way to have conversations with your previous conversations and other peoples conversations and have them associated with work.

This is the core tech of day50. The primary way to do this will be mcp to recall, proxy to store.

litellm is not the right way to go.

make it public

Dayzer is a memory and routing layer for LLM conversations.
It lets you persist, transfer, and resume threads across tools like VS Code, Aider, chat UIs, and agent shells — without losing context.

Powered by a pluggable proxy (e.g. LiteLLM), Dayzer tags each conversation with a unique ID and tracks the flow across applications. Whether you're coding, chatting, or running agents, you can recall, merge, or branch conversations like source control for thought.

Built for:

* Cross-app memory: Continue a conversation started in one tool from any other
* Thread syncing: Route context through a centralized store with clear APIs
* Git-style ops: Tag, merge, fork, and audit conversational history

This is part of Day50, which does  [llmehelp](https://github.com/kristopolous/llmehelp), [streamdown](https://github.com/kristopolous/Streamdown), and [Week7](https://github.com/kristopolous/megacode) .
