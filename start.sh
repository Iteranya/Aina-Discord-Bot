#!/bin/bash

echo "========================================================"
echo "Hello, Thanks For Installing Aina-chan Discord Bot"
echo "Sorry, Claude made this bash script, hope it works..."
echo "I'm just so tired, I'll test this later..."
echo "========================================================"
echo "This script will:"
echo "  1. Create a virtual environment if needed"
echo "  2. Install required dependencies"
echo "  3. Download cloudflared if needed"
echo "  4. Start the server and discord bot"
echo "========================================================"

# Check if virtual environment exists, create if it doesn't
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created!"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing required packages..."
pip install -r requirements.txt

# Check architecture for correct cloudflared binary
ARCH=$(uname -m)
CLOUDFLARED_URL=""

if [ "$ARCH" == "x86_64" ]; then
    CLOUDFLARED_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
elif [ "$ARCH" == "aarch64" ] || [ "$ARCH" == "arm64" ]; then
    CLOUDFLARED_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
else
    echo "Unsupported architecture: $ARCH"
    echo "Please download cloudflared manually from https://github.com/cloudflare/cloudflared/releases"
fi

# Download cloudflared if needed
if [ ! -f "cloudflared" ] && [ "$CLOUDFLARED_URL" != "" ]; then
    echo "Downloading cloudflared..."
    curl -Lo cloudflared "$CLOUDFLARED_URL"
    chmod +x cloudflared
fi

# Start the server and bot
echo "Starting server and bot..."
uvicorn main:app --reload --port 5454 &
python bot.py