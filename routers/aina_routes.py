import asyncio
import json
import uuid
import re
from fastapi import APIRouter, Form, Body, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pathlib import Path
from src.aina import generate_html_stream, active_generations, save_html, title_to_filename

router = APIRouter()

@router.post("/save-html")
async def deploy_site(
    content: str = Body(..., example="<html>...</html>"),
    title: str = Body(..., example="my-page")
):
    try:
        title = title_to_filename(title)
        title = title+".html"
        output_path = save_html(content, title)
        return {"status": "success", "path": output_path}  # Return proper JSON!
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/site-builder", response_class=HTMLResponse)
async def get_html():
    # Path to template and scripts
    template_path = "templates/site-builder/index.html"
    scripts_dir = Path("templates/site-builder/scripts")
    styles_dir = Path("templates/site-builder/styles")
    # Get all JS files in order (adjust as needed)
    css_files = sorted([
        *styles_dir.glob("*.css")
    ])
    js_files = sorted([
        *scripts_dir.glob("utils/*.js"),
        *scripts_dir.glob("*.js"),
        *scripts_dir.glob("services/*.js")
    ])
    
    # Concatenate all JS content
    js_content = []
    for js_file in js_files:
        if js_file.is_file() and js_file.suffix == ".js":
            try:
                with open(js_file, "r") as f:
                    js_content.append(f"\n\n/* {js_file.name} */\n")
                    js_content.append(f.read())
            except Exception as e:
                print(f"Error reading {js_file}: {str(e)}")
    
    css_content = []
    for css_file in css_files:
        if css_file.is_file() and css_file.suffix == ".css":
            try:
                with open(css_file, "r") as f:
                    css_content.append(f"\n\n/* {js_file.name} */\n")
                    css_content.append(f.read())
            except Exception as e:
                print(f"Error reading {css_file}: {str(e)}")
    
    # Read HTML template
    with open(template_path, "r") as f:
        html = f.read()
    
    html = html.replace(
        '<script type="module" src="scripts/main.js"></script>',
        '<script>\n' + '\n'.join(js_content) + '\n</script>'
    )

    html = html.replace(
        '<link rel="stylesheet" href="styles.css">',
        '<style>\n' + '\n'.join(css_content) + '\n</style>'
    )
    return html

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