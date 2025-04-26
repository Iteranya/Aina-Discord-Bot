import config
from src import flare
from src import llm
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import discord
import asyncio
from openai import OpenAI
import config

# Create a thread pool for CPU-bound tasks
executor = ThreadPoolExecutor()

def save_html(html_content, file_name):
    """Save HTML content to file - this can run in a separate thread"""
    output_path = f"drafts/{file_name}"
    # Open file in text write mode (not binary)
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    print(f"HTML successfully saved to {output_path}")
    return output_path

def process_website_request(title, content):
    """Process a website generation request - runs in a separate thread"""
    # This is a blocking function that will be run in a thread pool
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Generate the website synchronously since we're already in a separate thread
        website_html = loop.run_until_complete(llm.generate_website({"title": title, "content": content}))
        # Convert title to filename
        filename = title_to_filename(title)
        
        # Save the HTML file
        filename = title_to_filename(filename)
        save_html(website_html, f"{filename}.html")
        
        print(f"Successfully processed website request: {title}")


    finally:
        loop.close()

async def work():
    """Background task to process items from the queue"""
    print("Aina-chan starting work loop!")
    
    try:
        while True:
            try:
                # Get a task from the queue
                task = await config.queue_to_process_everything.get()
                
                # Process this in a separate thread to avoid blocking the event loop
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    executor,
                    process_website_request,
                    task["title"],
                    task["content"]
                )

                await send_new_site(task["title"],task["channel"])
                
                # Mark task as done
                config.queue_to_process_everything.task_done()
                
            except Exception as e:
                print(f"Error in work loop: {e}")
            
            # Always yield back to the event loop
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        print("Aina-chan's work loop was cancelled!")
    except Exception as e:
        print(f"Fatal error in work loop: {e}")

def title_to_filename(title):
    # Convert to lowercase
    filename = title.lower()
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '-')
    
    # Remove special characters
    import re
    filename = re.sub(r'[^\w\s_-]', '', filename)
    
    return filename

async def send_new_site(filename, channel: discord.channel.TextChannel):
            # Get The Tunnel
        filename = title_to_filename(filename)
        try:
            with open(flare.TUNNEL_INFO_FILE, 'r') as f:
                tunnel_info = json.load(f)
        except FileNotFoundError:
            message = "Ah, oh nyooo~ Flare-chan is still asleep! Please use the `/aina tunnel` to wake her up senpai!\n\nDon't worry! Aina has finished the website! You can access it from Aina's website once Flare-chan finished making the tunnel. \n\nThanks in advance, ehehe~"

        if flare.TUNNEL_NAME not in tunnel_info:
            tunnel_info = json.load(f)
        
        details = tunnel_info[flare.TUNNEL_NAME]
        accesslink = details.get("accesslink", "")
        message = f"Website is finished senpai!\n\nYou can access it here: {accesslink}/sites/drafts/{filename}.html\n\nI hope you like it! Aina-chan did her best~\n\nPS: If the link don't work, use `/aina tunnel` to reactivate it, you can find the new website in Aina's website~"

        await channel.send(message)




# Store active generation tasks
active_generations = {}

async def generate_html_stream(content, generation_id):
    ai_config:config.Config = config.load_or_create_config()

    client = OpenAI(
        base_url=ai_config.ai_endpoint,
        api_key=config.get_key(),
    )
    try:
        # Create the prompt
        messages = [
            {
            "role": "system",
            "content": ai_config.system_note
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
        stream = client.chat.completions.create(
            model=ai_config.base_llm,
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