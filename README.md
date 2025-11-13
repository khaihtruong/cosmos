# LLM Chat

LLM Chat is a chatbot leveraging industry-standard LLM models (OpenAI, Gemini, Anthropic) to converse and capture patient's behavior in between therapy sessions. This allows clinicians to have a good understanding of their patients.

## TODO
- [ ] Clarify on different workflows and states
- [ ] User active chat should show both started and non-started chat
- [x] Add filtering/sorting order for rovider chat window / potentially rearrange order
- [ ] CHeck if report generate per convo or per window
- [ ] Add more informational for when creating new chat window
- [ ] Adding model for report
- [x] Adding header, standardizing language across pages and chat creation
- [x] Navigation standardization, settings hiding, lock ability to recreate chat, showing inactive/past convo
## Quick Start for Mac

### Prerequisites

1. **Open Terminal** (press `Cmd + Space`, type "Terminal", and press Enter)

2. **Install Homebrew** (if you don't have it):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. **Install Python and Git**:
   ```bash
   brew install python@3.11 git
   ```

### Installation

1. **Download the project**:
   ```bash
   cd ~/Desktop
   git clone https://github.com/yourusername/cosmos.git
   cd cosmos
   ```

2. **Set up Python environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   **Note**: Run `source .venv/bin/activate` each time you open a new Terminal window to work on this project.

3. **Configure API keys**:
   ```bash
   cp .env.example .env
   open -a TextEdit .env
   ```

   In TextEdit, add at least one API key and save the file. The app will automatically load it when you start.

4. **Start the application**:
   ```bash
   python manage.py
   ```

   Open your browser and go to: `http://localhost:5000`

### (Optional) Local LLM with Ollama

For complete privacy without cloud APIs:

```bash
brew install ollama
ollama serve              # Keep this running in one Terminal window
ollama pull llama3.2:1b   # Run in a new Terminal window
```

**Trade-offs**: Complete privacy and free to use, but slower responses (30-60s vs 5-10s) and lower quality than cloud models.

### Updating the Code

```bash
cd ~/Desktop/cosmos
git pull
source .venv/bin/activate
pip install -r requirements.txt
python manage.py
```

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
