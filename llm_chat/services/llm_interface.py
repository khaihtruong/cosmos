import os
import time
import json
import requests
from typing import List, Dict, Optional, Tuple

# Provider clients (optional imports)
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class LLMInterface:
    """Unified interface for different LLM providers"""
    _provider_clients: Dict[str, object] = {}

    @classmethod
    def initialize_clients(cls):
        """Initialize provider clients based on available API keys"""
        # OpenAI
        openai_key = os.environ.get('OPENAI_API_KEY')
        if OpenAI and openai_key and openai_key.strip() and openai_key != 'your_openai_key_here':
            try:
                cls._provider_clients['openai'] = OpenAI(api_key=openai_key)
                print("✓ OpenAI client initialized successfully")
            except Exception as e:
                print(f"✗ Could not initialize OpenAI client: {e}")
        else:
            print("✗ OpenAI API key not configured or invalid")

        # Anthropic
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if Anthropic and anthropic_key and anthropic_key.strip() and anthropic_key != 'your_anthropic_key_here':
            try:
                cls._provider_clients['anthropic'] = Anthropic(api_key=anthropic_key)
                print("✓ Anthropic client initialized successfully")
            except Exception as e:
                print(f"✗ Could not initialize Anthropic client: {e}")
        else:
            print("✗ Anthropic API key not configured or invalid")

        # Google
        google_key = os.environ.get('GOOGLE_API_KEY')
        if genai and google_key and google_key.strip() and google_key != 'your_google_api_key_here':
            try:
                genai.configure(api_key=google_key)
                cls._provider_clients['google'] = genai
                print("✓ Google client initialized successfully")
            except Exception as e:
                print(f"✗ Could not initialize Google client: {e}")
        else:
            print("✗ Google API key not configured or invalid")

        print("\n=== LLM Client Status ===")
        print(f"Initialized providers: {list(cls._provider_clients.keys())}")
        for provider in ['openai', 'anthropic', 'google']:
            status = "✓ AVAILABLE" if provider in cls._provider_clients else "✗ NOT AVAILABLE"
            print(f"{provider}: {status}")
        print("========================\n")

    @classmethod
    def call_llm(cls, model, messages: List[Dict], system_prompt: Optional[str] = None) -> Tuple[str, float]:
        """Call LLM with messages and return (response_text, response_time_sec)"""
        start_time = time.time()

        # Format messages with system prompt
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({'role': 'system', 'content': system_prompt})
        formatted_messages.extend(messages)

        config = json.loads(model.config or '{}')

        try:
            if model.provider == 'openai':
                client = cls._provider_clients.get('openai')
                if not client:
                    raise RuntimeError("OpenAI client not available")

                response = client.chat.completions.create(
                    model=model.model_identifier,
                    messages=formatted_messages,
                    temperature=config.get('temperature', 0.7),
                    max_tokens=config.get('max_tokens', 1000),
                )
                result = response.choices[0].message.content

            elif model.provider == 'anthropic':
                client = cls._provider_clients.get('anthropic')
                if not client:
                    raise RuntimeError("Anthropic client not available")

                # Extract system message
                system_msg = None
                anthropic_messages = []
                for msg in formatted_messages:
                    if msg['role'] == 'system':
                        system_msg = msg['content']
                    else:
                        anthropic_messages.append(msg)

                response = client.messages.create(
                    model=model.model_identifier,
                    max_tokens=config.get('max_tokens', 1000),
                    temperature=config.get('temperature', 0.7),
                    system=system_msg,
                    messages=anthropic_messages,
                )
                # anthropic SDK returns list of content blocks
                result = response.content[0].text

            elif model.provider == 'google':
                client = cls._provider_clients.get('google')
                if not client:
                    raise RuntimeError("Google client not available")

                gemini_messages = []
                for msg in formatted_messages:
                    if msg['role'] == 'system':
                        continue
                    role = 'model' if msg['role'] == 'assistant' else 'user'
                    gemini_messages.append({'role': role, 'parts': [{'text': msg['content']}]})

                model_obj = genai.GenerativeModel(model.model_identifier)
                response = model_obj.generate_content(
                    contents=gemini_messages,
                    generation_config={
                        'temperature': config.get('temperature', 0.7),
                        'max_output_tokens': config.get('max_tokens', 1000),
                    },
                )
                result = response.text

            elif model.provider == 'local':
                response = requests.post(
                    model.api_endpoint,
                    json={
                        'messages': formatted_messages,
                        'temperature': config.get('temperature', 0.7),
                        'max_tokens': config.get('max_tokens', 1000),
                    },
                    timeout=60,
                )
                response.raise_for_status()
                result = response.json()['choices'][0]['message']['content']

            else:
                raise ValueError(f"Unknown provider: {model.provider}")

        except Exception as e:
            result = f"Error calling {model.provider}: {str(e)}"

        response_time = time.time() - start_time
        return result, response_time
