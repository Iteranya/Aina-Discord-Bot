import asyncio
import json
import uuid
import re
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, StreamingResponse

from src.aina import generate_html_stream, active_generations

router = APIRouter()

@router.get("/site-builder", response_class=HTMLResponse)
async def get_html():
    with open("templates/website_builder.html", "r") as f:
        return f.read()

@router.post("/generate-website")
async def generate_website(content: str = Form(...)):
    # Create a unique ID for this generation
    generation_id = str(uuid.uuid4())
    
    # Start generation in background
    task = asyncio.create_task(generate_html_stream(content, generation_id))
    active_generations[generation_id] = {"task": task, "chunks": []}
    
    # Return the ID immediately
    return {"id": generation_id}

@router.get("/stream/{generation_id}")
async def stream_response(generation_id: str):
    if generation_id not in active_generations:
        return {"error": "Generation not found"}
    
    # Create a streaming response
    async def event_generator():
        current_index = 0
        chunks = active_generations[generation_id]["chunks"]
        
        while True:
            # Check if there are new chunks
            if current_index < len(chunks):
                # Send all new chunks
                for i in range(current_index, len(chunks)):
                    yield f"data: {json.dumps({'html': chunks[i]})}\n\n"
                current_index = len(chunks)
            
            # Check if task is done
            if active_generations[generation_id]["task"].done():
                if current_index == len(chunks):  # Make sure we've sent everything
                    yield f"data: {json.dumps({'done': True})}\n\n"
                    break
            
            # Wait before checking again
            await asyncio.sleep(0.1)
        
        # Clean up after streaming is complete
        if generation_id in active_generations:
            del active_generations[generation_id]
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


def regex_html(text):
    # Try to find complete HTML document with doctype
    doctype_pattern = re.compile(r'<!DOCTYPE\s+html[^>]*>.*?</html>', re.DOTALL | re.IGNORECASE)
    match = doctype_pattern.search(text)
    if match:
        return match.group(0)
    
    # Try to find HTML without doctype but with html tags
    html_pattern = re.compile(r'<html[^>]*>.*?</html>', re.DOTALL | re.IGNORECASE)
    match = html_pattern.search(text)
    if match:
        return match.group(0)
    
    return None