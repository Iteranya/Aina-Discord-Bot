import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import os

# System Setup

load_dotenv()
load_dotenv(override=True)
ai_token: str | None = os.getenv("AI_TOKEN")
discord_token:str | None = os.getenv("DISCORD_TOKEN")
base_llm = "deepseek-ai/DeepSeek-V3-0324"
queue_to_process_everything = asyncio.Queue()

client = OpenAI(
  base_url="https://llm.chutes.ai/v1",
  api_key=ai_token,
)
