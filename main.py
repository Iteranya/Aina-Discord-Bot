import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from routers import home_routes, comfyui_routes, aina_routes, config_routes

app = FastAPI()

# For static HTML tools
app.mount("/tools", StaticFiles(directory="sites/tools"), name="tools")
app.mount("/blogs", StaticFiles(directory="sites/blogs"), name="blogs")
app.mount("/drafts", StaticFiles(directory="sites/drafts"), name="drafts")

# For templates
templates = Jinja2Templates(directory="templates")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(home_routes.router)
app.include_router(comfyui_routes.router, prefix="/comfyui")
app.include_router(aina_routes.router)
app.include_router(config_routes.router)

# Run the application with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5454, reload=True)