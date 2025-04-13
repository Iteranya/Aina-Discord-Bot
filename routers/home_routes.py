from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
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
            "url": f"/tools/{file.name}"
        })
    
    for file in blogs_dir.glob("*.html"):
        blog_files.append({
            "name": file.stem.replace("-", " ").title(),
            "url": f"/blogs/{file.name}"
        })

    for file in drafts_dir.glob("*.html"):
        draft_files.append({
            "name": file.stem.replace("-", " ").title(),
            "url": f"/drafts/{file.name}"
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tools": sorted(tool_files, key=lambda x: x["name"]),
        "blogs": sorted(blog_files, key=lambda x: x["name"]),
        "drafts": sorted(draft_files, key=lambda x: x["name"])
    })