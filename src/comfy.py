import json
import uuid
import asyncio
import urllib.request
import urllib.parse
import websocket

# Store active generation tasks
comfy_tasks = {}

async def process_comfyui_workflow(workflow, task_id, server_address):
    """
    Process a ComfyUI workflow and retrieve the generated images.
    """
    print(server_address)
    try:
        # Generate a unique client ID for this connection
        client_id = str(uuid.uuid4())
        
        # Connect to WebSocket
        ws = websocket.create_connection(
            f"ws://{server_address}/ws?clientId={client_id}"
        )
        
        try:
            # Queue the prompt
            prompt_id = queue_prompt(workflow, client_id, server_address)
            
            # Process WebSocket messages to track execution
            output_images = await process_websocket_messages(ws, prompt_id, task_id)
            
            # Get history and retrieve images if not received via WebSocket
            if not output_images:
                history = get_history(prompt_id, server_address)
                output_images = extract_images_from_history(history, prompt_id, server_address)
            
            # Store the images
            comfy_tasks[task_id]["images"] = output_images
            comfy_tasks[task_id]["status"] = "completed"
            
            return output_images
        finally:
            # Always close the WebSocket connection
            ws.close()
            
    except Exception as e:
        comfy_tasks[task_id]["status"] = "failed"
        comfy_tasks[task_id]["error"] = str(e)
        raise


def queue_prompt(prompt, client_id, server_address):
    """
    Submit a workflow prompt to ComfyUI's queue.
    """
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    response = urllib.request.urlopen(req)
    return json.loads(response.read())['prompt_id']


async def process_websocket_messages(ws, prompt_id, task_id):
    """
    Process WebSocket messages to track execution progress and collect images.
    """
    output_images = []
    current_node = ""
    
    # Set a timeout for the WebSocket connection (30 minutes)
    max_wait_time = 30 * 60  # 30 minutes in seconds
    start_time = asyncio.get_event_loop().time()
    
    # Update task status to processing
    comfy_tasks[task_id]["status"] = "processing"
    
    while True:
        # Check if we've hit the timeout
        current_time = asyncio.get_event_loop().time()
        if current_time - start_time > max_wait_time:
            raise TimeoutError("Image generation timed out after 30 minutes")
        
        # Make the WebSocket receive non-blocking
        ws.settimeout(1.0)  # 1 second timeout
        
        try:
            out = ws.recv()
            
            # Process string messages (status updates)
            if isinstance(out, str):
                message = json.loads(out)
                
                if message['type'] == 'executing':
                    data = message['data']
                    
                    # Update node being executed
                    if data['prompt_id'] == prompt_id:
                        if data['node'] is None:
                            # Execution complete
                            break
                        else:
                            current_node = data['node']
                            
                            # Update the task info for status checking
                            update_task = f"Processing node: {current_node}"
                            if task_id in comfy_tasks:
                                comfy_tasks[task_id]["current_node"] = current_node
            
            # Process binary data (preview images)
            else:
                # Check if this is binary data from a SaveImageWebsocket node
                if current_node and 'SaveImageWebsocket' in current_node:
                    # Skip the first 8 bytes of binary header
                    image_data = out[8:] if len(out) > 8 else out
                    output_images.append(image_data)
        
        except websocket.WebSocketTimeoutException:
            # Just a timeout, continue waiting
            await asyncio.sleep(0.1)
            continue
        
        except Exception as e:
            print(f"WebSocket error: {str(e)}")
            break
    
    return output_images


def get_history(prompt_id, server_address):
    """
    Fetch execution history for a completed prompt.
    """
    with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())


def get_image(filename, subfolder, folder_type, server_address):
    """
    Retrieve an image from ComfyUI's view endpoint.
    """
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
        return response.read()


def extract_images_from_history(history, prompt_id, server_address):
    """
    Extract saved images from the execution history.
    """
    output_images = []
    if prompt_id in history:
        for node_id in history[prompt_id]['outputs']:
            node_output = history[prompt_id]['outputs'][node_id]
            if 'images' in node_output:
                for image in node_output['images']:
                    image_data = get_image(
                        image['filename'], 
                        image['subfolder'], 
                        image['type'],
                        server_address
                    )
                    output_images.append(image_data)
    
    return output_images