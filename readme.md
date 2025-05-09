# Shopping Assistant with OpenAI and Ollama Integration

This repository contains a Shopping Assistant AI agent that helps users search for products, get product details, and handle unclear requests through conversation. This demo showcases how an agent can leverage Large Language Models (LLMs) for tool calling or function calling capabilities. The main implementation come from [Martin Fowler's blog](https://martinfowler.com/articles/function-call-LLM.html).

## Overview

The Shopping Assistant is implemented in two versions:
- `agent.py` - Uses OpenAI API for LLM inference via [openrouter](https://openrouter.ai/)
- `agent_ollama.py` - Uses locally deployed Ollama for LLM inference

Both versions provide identical functionality but utilize different backend LLM providers.

## Features

- **Product Search**: Search for products using keywords
- **Product Details**: Get detailed information about specific products
- **Request Clarification**: Ask clarifying questions when user requests are unclear
- **Conversation History**: Maintain context throughout the interaction
- **Tool-calling**: Leverage function/tool calling capabilities of modern LLMs

## Prerequisites

### For OpenAI version (agent.py)

- Python 3.8+
- OpenAI API key (set as environment variable `OPENROUTER_API_KEY`)
- Required Python packages:
  - `openai`
  - `pydantic`
  - `instructor`

### For Ollama version (agent_ollama.py)
- Python 3.8+ 
- Ollama installed and running locally
- Required Python packages:
  - `ollama`
  - `openai`
  - `pydantic`
  - `instructor`

## Setup

1. Clone this repository
2. Install required dependencies:
   ```bash
   pip install openai pydantic instructor ollama
   ```
3. For OpenAI version, set your API key:
   ```bash
   export OPENROUTER_API_KEY="your-api-key"
   ```
4. For Ollama version, start Ollama service and pull the required model:
   ```bash
   ollama serve
   ollama pull qwen3:8b
   ```

## Usage

### Running with OpenAI
```bash
python agent.py
```

### Running with local Ollama
```bash
python agent_ollama.py
```

### Example Conversation
```
Shopping Assistant: Hello! How can I help you today? (Type 'bye' to exit)
You: I'm looking for shirts
Shopping Assistant: Here are the products I found: Product 1 (ID: p1), Product 2 (ID: p2)
You: tell me more about p1
Shopping Assistant: Product p1: price: $19.99 - A great product.
You: bye
Shopping Assistant: Goodbye! Have a nice day!
```

## Architecture

The system is built with the following components:

- `ShoppingAgent`: Main class that manages user interaction and decision-making
- `SearchClient`: Simulates a product search database (currently uses mock data)
- Action classes (`Search`, `GetProductDetails`, `Clarify`): Represent possible actions the agent can take
- LLM integration: Utilizes OpenAI or Ollama for natural language understanding and tool calling

## Implementation Details

The Shopping Assistant uses function/tool calling to determine which action to take based on user input. The agent:

1. Maintains conversation history for context
2. Sends user queries to the LLM with available functions
3. Interprets the LLM's function call decision
4. Executes the appropriate action
5. Returns the result to the user

## Extending the Assistant

You can extend this Shopping Assistant by:
- Connecting to a real product database
- Adding more sophisticated search capabilities
- Implementing additional tools/functions
- Enhancing the conversation capabilities
- Implementing robust error handling and edge cases

## License

[Add your license information here]