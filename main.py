import os
from pathlib import Path
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import re
import config
import json
import uuid
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI, AsyncOpenAI


app = FastAPI()

# For static HTML tools
app.mount("/sites/tools", StaticFiles(directory="sites/tools"), name="tools")
app.mount("/sites/blogs", StaticFiles(directory="sites/blogs"), name="blogs")
app.mount("/sites/drafts", StaticFiles(directory="sites/drafts"), name="drafts")
# For templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    tool_files = []
    blog_files = []
    draft_files = []
    tools_dir = Path("sites/tools")
    blogs_dir = Path("sites/blogs")
    drafts_dir = Path("sites/drafts")

    for file in tools_dir.glob("*.html"):
        tool_files.append({
            "name": file.stem.replace("-", " ").title(),
            "url": f"/sites/tools/{file.name}"
        })
    
    for file in blogs_dir.glob("*.html"):
        blog_files.append({
            "name": file.stem.replace("-", " ").title(),
            "url": f"/sites/blogs/{file.name}"
        })

    for file in drafts_dir.glob("*.html"):
        draft_files.append({
            "name": file.stem.replace("-", " ").title(),
            "url": f"/sites/drafts/{file.name}"
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tools": sorted(tool_files, key=lambda x: x["name"]),
        "blogs": sorted(blog_files, key=lambda x: x["name"]),
        "drafts": sorted(draft_files, key=lambda x: x["name"])
    })

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active generation tasks
active_generations = {}

@app.get("/site-builder", response_class=HTMLResponse)
async def get_html():
    with open("templates/website_builder.html", "r") as f:
        return f.read()

@app.post("/generate-website")
async def generate_website(content: str = Form(...)):
    # Create a unique ID for this generation
    generation_id = str(uuid.uuid4())
    
    # Start generation in background
    task = asyncio.create_task(generate_html_stream(content, generation_id))
    active_generations[generation_id] = {"task": task, "chunks": []}
    
    # Return the ID immediately
    return {"id": generation_id}

@app.get("/stream/{generation_id}")
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

async def generate_html_stream(content, generation_id):
    try:
        # Create the prompt
        messages = [
            {
            "role": "system",
            "content": "ONLY USE HTML, CSS AND JAVASCRIPT. If you want to use ICON make sure to import the library first. Try to create the best UI possible by using only HTML, CSS and JAVASCRIPT. Also, try to ellaborate as much as you can, to create something unique. ALWAYS GIVE THE RESPONSE INTO A SINGLE HTML FILE"
            },
            {
            "role": "user",
            "content": f"{content}"
            },
            {
            "role": "assistant",
            "content": "Understood, here's the requested site: ```html\n"
            }
        ]
        
        # Use synchronous client with stream=True for streaming
        stream = config.client.chat.completions.create(
            model=config.base_llm,
            messages=messages,
            stream=True
        )
        
        html_so_far = ""
        # Iterate through the stream (this works synchronously)
        for chunk in stream:
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                html_so_far += delta_content
                # Store this chunk
                if generation_id in active_generations:
                    active_generations[generation_id]["chunks"].append(delta_content)
                await asyncio.sleep(0.01)  # Small delay to prevent CPU overload
        
        return html_so_far
    except Exception as e:
        print(f"Error in generation: {str(e)}")
        return f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>"

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

# Note: Removed the duplicate generate_website function and the problematic llm module