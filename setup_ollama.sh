#!/bin/bash
# Setup script for Ollama local LLM

set -e  # Exit on error

echo "=== Ollama Setup Script ==="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "This script is designed for macOS. For other platforms, see: https://ollama.ai"
    exit 1
fi

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is already installed"
    ollama --version
else
    echo "Installing Ollama..."
    if command -v brew &> /dev/null; then
        brew install ollama
    else
        echo "Homebrew not found. Please install from: https://ollama.ai"
        exit 1
    fi
fi

echo ""
echo "=== Starting Ollama Service ==="
# Check if Ollama is already running
if pgrep -x "ollama" > /dev/null; then
    echo "✓ Ollama service is already running"
else
    echo "Starting Ollama service in background..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 2
    echo "✓ Ollama service started"
fi

echo ""
echo "=== Downloading Llama 3.2 1B Model ==="
echo "This will download ~1GB of data..."
ollama pull llama3.2:1b

echo ""
echo "=== Testing Ollama ==="
# Test the endpoint
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✓ Ollama API is responding"
    echo "Available models:"
    curl -s http://localhost:11434/api/tags | python3 -m json.tool
else
    echo "✗ Ollama API is not responding. Please check the service."
    exit 1
fi

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Ollama is running at: http://localhost:11434"
echo "Model endpoint: http://localhost:11434/v1/chat/completions"
echo ""
echo "To stop Ollama: killall ollama"
echo "To restart Ollama: ollama serve"
echo "To pull more models: ollama pull <model-name>"
echo ""
