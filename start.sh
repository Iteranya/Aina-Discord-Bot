#!/bin/bash

# Check if cloudflared exists, if not download it
if [ ! -f "cloudflared" ]; then
    curl -Lo cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x cloudflared
fi

# Activate virtual environment
source venv/bin/activate

# Start uvicorn in background
uvicorn main:app --reload --port 5454 &

# Run the bot
python bot.py