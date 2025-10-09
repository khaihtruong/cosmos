# LLM Chat

LLM Chat is a chatbot leveraging industry-standard LLM models (OpenAI, Gemini, Anthropic) to converse and capture patient's behavior in between therapy session. This would allow the clinician to have a good understand of their patient.

## Installation

### 1. Install Python Dependencies

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install necessary packages.

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
# OpenAI API Key (optional)
OPENAI_API_KEY=your_openai_key_here

# Anthropic API Key (optional)
ANTHROPIC_API_KEY=your_anthropic_key_here

# Google API Key (optional)
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. (Optional) Setup Local LLM with Ollama

For complete privacy and offline usage, you can run a local LLM:

```bash
# Run the setup script (macOS only)
./setup_ollama.sh

# Or install manually:
brew install ollama
ollama serve
ollama pull llama3.2:1b
```

The local model will be available at `http://localhost:11434/v1/chat/completions`

**Note**: Local models provide complete data privacy but with lower quality responses than cloud APIs. Perfect for development and privacy-sensitive applications.

### 4. Start the Application

To start the program run the following command from the root of the project:
```bash
python manage.py
```

The application will automatically detect and initialize available LLM providers (OpenAI, Anthropic, Google, and local Ollama).

## Features

### Conversation Context
All conversations maintain context across messages, sending the **last 20 messages** to the LLM with each new message. This allows the AI to remember earlier parts of the conversation and provide contextually relevant responses.

- System prompts are included at the beginning of each request
- Older messages (beyond the last 20) are automatically dropped to manage token limits
- To adjust the context window, modify the `limit(20)` value in `llm_chat/routes/conversations.py:260`

### Performance Notes
- **Cloud APIs** (OpenAI, Anthropic, Google): Fast responses (5-10 seconds)
- **Local Ollama on M1 MacBook Air**: Slower responses (~30-60 seconds for Llama 3.2 1B)
- Local models prioritize privacy over speed - ideal for development and sensitive data

## Documentation
API documentation implemented with Swagger available at /docs

## Project Structure
```bash
|-- main
|   |-- llm_chat              # backend
|       |-- models            # database model
|       |-- routes            # api routes
|       |-- services          # setup LLM interface
|       |-- utils             # role management
|       |--__init__.py
|       |--extensions.py
|   |-- client                # frontend (soon)
|   |-- templates             # frontend (current)
|   |-- manage.py             # app entry point
|   |-- README.md
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MindLamp](https://www.digitalpsych.org/mindlamp.html)