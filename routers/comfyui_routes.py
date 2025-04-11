import uuid
import asyncio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json
import os
import random
from dataclasses import dataclass
from src.comfy import (
    process_comfyui_workflow,
    comfy_tasks
)
from src.llm import(
    generate_sd_prompt
)
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

# --- Configuration ---
COMFYUI_SERVER = os.getenv("COMFYUI_SERVER", "127.0.0.1:8181")
DEFAULT_WORKFLOW_FILE = "assets/comfy/default.json" # Default workflow file name

# --- Data Models ---
@dataclass
class ImageGenerationParams:
    # preset:str = "default.json" # Removed, as the workflow file is now handled differently
    width: int = 512
    height: int = 768
    positive_prompt: str = "1girl"
    negative_prompt: str = "lowres, bad anatomy, bad hands, text, error, missing finger, extra digits, fewer digits, cropped, worst quality, low quality, low score, bad score, average score, signature, watermark, username, blurry, embedding:easynegative, embedding:badhandv4"
    server_address: Optional[str] = None # Allow overriding server per request
    # Add seed if you want the user to control it, otherwise random is fine
    # seed: Optional[int] = None

# --- Router Definition ---
router = APIRouter()


# --- Helper Function ---
async def modify_workflow(base_workflow: Dict[str, Any], params: ImageGenerationParams) -> Dict[str, Any]:
    """
    Modifies the loaded ComfyUI workflow dictionary with parameters.
    NOTE: Relies on specific node IDs ('3', '5', '6', '7', '11') existing
          in the base_workflow. This can be fragile if the workflow changes.
    """
    modified_workflow = base_workflow.copy() # Work on a copy
    new_prompt = await generate_sd_prompt(params.positive_prompt)
    # Generate a random seed if not provided (or always use random)
    random_seed = random.randint(1, 999999999999999)
    # If you add seed to ImageGenerationParams and want user control:
    # seed_to_use = params.seed if params.seed is not None else random_seed

    try:
        # Modify Latent Image dimensions (assuming Node '5')
        if "5" in modified_workflow and "inputs" in modified_workflow["5"]:
            modified_workflow["5"]["inputs"]["width"] = params.width
            modified_workflow["5"]["inputs"]["height"] = params.height
        else:
            print("Warning: Node '5' (expected EmptyLatentImage) not found or missing inputs.")

        # Modify Positive Prompt (assuming Node '6')
        if "6" in modified_workflow and "inputs" in modified_workflow["6"]:
            if new_prompt != None or new_prompt!="":
                modified_workflow["6"]["inputs"]["text"] = new_prompt
            else:
                modified_workflow["6"]["inputs"]["text"] = params.positive_prompt
        else:
             print("Warning: Node '6' (expected Positive CLIPTextEncode) not found or missing inputs.")

        # Modify Negative Prompt (assuming Node '7')
        if "7" in modified_workflow and "inputs" in modified_workflow["7"]:
            modified_workflow["7"]["inputs"]["text"] = params.negative_prompt
        else:
             print("Warning: Node '7' (expected Negative CLIPTextEncode) not found or missing inputs.")

        # Modify Sampler Seed (assuming Node '3')
        if "3" in modified_workflow and "inputs" in modified_workflow["3"]:
            modified_workflow["3"]["inputs"]["seed"] = random_seed # Use the random seed
        else:
             print("Warning: Node '3' (expected KSampler) not found or missing inputs.")

        # Modify an optional second Sampler/Refiner Seed (assuming Node '11')
        if "11" in modified_workflow and "inputs" in modified_workflow["11"]:
            modified_workflow["11"]["inputs"]["seed"] = random_seed # Use the same random seed
        # else:
            # print("Warning: Node '11' (optional second sampler/refiner) not found or missing inputs.") # Optional node

    except KeyError as e:
        # This provides more specific feedback if a node or 'inputs' is missing
        print(f"Error modifying workflow: Missing key {e}. Check node IDs and structure in '{DEFAULT_WORKFLOW_FILE}'.")
        # Decide if you want to raise an exception here or just log the warning
        raise ValueError(f"Failed to modify workflow due to missing key: {e}. Ensure nodes 3, 5, 6, 7 exist with correct inputs.") from e
    except Exception as e:
        print(f"An unexpected error occurred during workflow modification: {e}")
        raise # Re-raise unexpected errors

    return modified_workflow

# --- API Endpoints ---

@router.post("/create_prompt")
async def generate_prompt_endpoint(content: dict):
    """
    Generates a potentially enhanced prompt using an LLM (simulated).
    """
    try:
        # Basic input validation
        if not content or "prompt" not in content:
             raise HTTPException(status_code=400, detail="Missing 'prompt' in request body")

        task = {"content": content.get("prompt", "")}
        generated_prompt = await generate_sd_prompt(task)
        return {"status": "success", "prompt": generated_prompt}
    except Exception as e:
        # Log the exception for debugging
        print(f"Error in /create_prompt: {e}")
        # Return a generic error to the user
        raise HTTPException(status_code=500, detail="Oh nyooooo~ Error generating prompt.")


@router.post("/generate")
async def generate_image_endpoint(params: ImageGenerationParams):
    """
    Generates an image using ComfyUI with parameters applied to a default workflow.

    Accepts image generation parameters and returns a task ID.
    """
    task_id = str(uuid.uuid4())
    server_addr_to_use = params.server_address or COMFYUI_SERVER
    print("The Current Task ID is: "+task_id)
    try:
        # 1. Load the base workflow from the default file
        if not os.path.exists(DEFAULT_WORKFLOW_FILE):
             raise HTTPException(status_code=500, detail=f"Default workflow file '{DEFAULT_WORKFLOW_FILE}' not found.")

        with open(DEFAULT_WORKFLOW_FILE, 'r') as f:
            base_workflow = json.load(f)

        # 2. Modify the loaded workflow with the provided parameters
        modified_workflow = await modify_workflow(base_workflow, params)
        print("Here's the modified workflow")
        print(modified_workflow)

        # 3. Start the generation task in the background
        task = asyncio.create_task(process_comfyui_workflow(
            modified_workflow,
            task_id,
            server_addr_to_use
        ))
        print("Made It Here")

        # 4. Store task info
        comfy_tasks[task_id] = {
            "status": "processing",
            "task": task,
            "images": []
        }
        print("Just before retuning task_id")

        return {"task_id": task_id}

    except FileNotFoundError:
         raise HTTPException(status_code=500, detail=f"Error: Default workflow file '{DEFAULT_WORKFLOW_FILE}' not found on server.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Error: Could not parse '{DEFAULT_WORKFLOW_FILE}'. Invalid JSON.")
    except ValueError as e: # Catch errors from modify_workflow
         raise HTTPException(status_code=400, detail=f"Error processing workflow: {e}")
    except Exception as e:
        # Log unexpected errors
        print(f"Unexpected error in /generate endpoint: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred during image generation setup.")


@router.get("/status/{task_id}")
async def get_generation_status(task_id: str):
    """
    Check the status of a ComfyUI generation task.
    """
    print("Trying to check taskId: "+task_id)
    print("Here's the Task info: ")
    print(comfy_tasks[task_id])
    if task_id not in comfy_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task_info = comfy_tasks[task_id]

    # Check if the task is complete only if it's currently 'processing'
    # Avoids repeatedly checking finished tasks
    if task_info["status"] == "processing" and task_info["task"].done():
        try:
            # Accessing result() will raise any exception the task encountered
            task_info["task"].result()
            # Check if images were actually added (process_comfyui_workflow should do this)
            if task_info.get("images"):
                 task_info["status"] = "completed"
            else:
                 # If the task finished but no images were added, mark as failed.
                 # This depends on process_comfyui_workflow's behavior.
                 print(f"Task {task_id} finished but no images found.")
                 task_info["status"] = "failed"
                 task_info["error"] = "Task completed without producing images."

        except Exception as e:
            print(f"Task {task_id} failed with exception: {e}") # Log the error
            task_info["status"] = "failed"
            # Store a simplified error message for the client
            task_info["error"] = f"Processing error: {type(e).__name__}" # Don't expose detailed internal errors directly

    return {
        "status": task_info["status"],
        "image_count": len(task_info["images"]) if task_info["status"] == "completed" else 0,
        # Optionally include error message if failed
        **({"error": task_info["error"]} if task_info["status"] == "failed" and "error" in task_info else {})
    }

@router.get("/image/{task_id}")
async def get_generated_image(task_id: str, index: int = 0):
    """
    Retrieve a generated image by task ID and index.
    """
    if task_id not in comfy_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task_info = comfy_tasks[task_id]

    # Check status first
    current_status = await get_generation_status(task_id) # Re-check status in case it just finished

    if current_status["status"] == "processing":
         # Use 202 Accepted: Request accepted, processing not complete.
        raise HTTPException(status_code=202, detail="Image generation still in progress")

    if current_status["status"] == "failed":
        error_msg = current_status.get("error", "Unknown error during generation")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {error_msg}")

    if current_status["status"] != "completed":
         # Catch any other unexpected status
         raise HTTPException(status_code=500, detail=f"Task is in an unexpected state: {current_status['status']}")

    # Now we know status is 'completed'
    if not task_info.get("images"):
         raise HTTPException(status_code=404, detail="Task completed, but no images are available.")

    if index < 0 or index >= len(task_info["images"]):
        raise HTTPException(status_code=404, detail=f"Image index {index} out of range (0 to {len(task_info['images']) - 1})")

    # Return the image
    image_data = task_info["images"][index]
    return Response(content=image_data, media_type="image/png")


@router.get("/ui", response_class=HTMLResponse) # Keep response_class here for clarity, though TemplateResponse overrides it
async def comfyui_simple_interface(request: Request): # Add 'request: Request'
    """
    A simple web interface updated to use parameters instead of full workflow JSON,
    served via Jinja2 template.
    """
    # Default values matching ImageGenerationParams (or your defaults)
    default_width = 512
    default_height = 768
    default_positive = "1girl"
    default_negative = "lowres, bad anatomy, bad hands, text, error, missing finger, extra digits, fewer digits, cropped, worst quality, low quality, low score, bad score, average score, signature, watermark, username, blurry, embedding:easynegative, embedding:badhandv4"
    default_server = COMFYUI_SERVER
    default_workflow_file = DEFAULT_WORKFLOW_FILE # Use the config variable

    # Prepare the context dictionary to pass variables to the template
    context = {
        "request": request, # Required by Jinja2Templates
        "default_width": default_width,
        "default_height": default_height,
        "default_positive": default_positive,
        "default_negative": default_negative,
        "default_server": default_server,
        "default_workflow_file": default_workflow_file # Pass the workflow filename
    }

    # Render the template, passing the context
    return templates.TemplateResponse("image_gen.html", context)