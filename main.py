from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from pathlib import Path
app = FastAPI()

# For static HTML tools - THESE LINES ARE IMPORTANT!
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
            "url": f"/sites/tools/{file.name}"  # Note the leading slash
        })
    
    for file in blogs_dir.glob("*.html"):
        blog_files.append({
            "name": file.stem.replace("-", " ").title(),
            "url": f"/sites/blogs/{file.name}"  # Note the leading slash
        })

    for file in drafts_dir.glob("*.html"):
        draft_files.append({
            "name": file.stem.replace("-", " ").title(),
            "url": f"/sites/drafts/{file.name}"  # Note the leading slash
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tools": sorted(tool_files, key=lambda x: x["name"]),
        "blogs": sorted(blog_files, key=lambda x: x["name"]),
        "drafts": sorted(draft_files, key=lambda x: x["name"])
    })