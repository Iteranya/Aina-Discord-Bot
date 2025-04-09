import discord
from discord import app_commands
from discord.ui import Modal, TextInput
from src import aina
import config
import asyncio
import concurrent.futures
from src import flare

# Bot setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Create a thread pool for CPU-bound tasks
thread_pool = concurrent.futures.ThreadPoolExecutor()

class WebsiteBuilderModal(Modal, title="Make Your Own Website!!!"):
    # Text inputs remain the same
    title_input = TextInput(
        label="Title",
        placeholder="Enter a title...",
        required=True,
        max_length=100
    )
    
    content_input = TextInput(
        label="Content",
        placeholder="Tell Me All You Want About This Website~",
        required=True,
        style=discord.TextStyle.long,
        max_length=2000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        # Acknowledge the submission immediately
        await interaction.response.send_message(f"Thank You Senpai!!!\n\nPlease wait warmly while Aina-chan makes the website for you! Ehehe~", ephemeral=True)
        
        # Add to queue without blocking
        config.queue_to_process_everything.put_nowait({
            "title": self.title_input.value,
            "content": self.content_input.value,
            "channel":interaction.channel
        })
        print(f"Received form data - Title: {self.title_input.value}, Description: {self.content_input.value}")

@tree.command(name="uploadhtml", description="Upload an HTML file")
async def upload_html(interaction: discord.Interaction, html_file: discord.Attachment):
    try:
        # Check if the file is an HTML file
        if not html_file.filename.endswith('.html'):
            await interaction.response.send_message("Please give me the HTML File Senpai~", ephemeral=True)
            return
            
        # Read the file content
        html_bytes = await html_file.read()
        html_content = html_bytes.decode('utf-8')

        # Acknowledge the receipt of the file first
        await interaction.response.send_message(f"Thank You Senpai! Aina-chan will take care of it~", ephemeral=True)
        
        # Process the HTML file off the main thread
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            thread_pool,
            aina.save_html,
            html_content,
            html_file.filename
        )
        
        print(f"Processed HTML file: {html_file.filename}, Size: {len(html_content)} bytes")
    
    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"An error occurred while processing the file: {str(e)}", ephemeral=True)
        else:
            await interaction.followup.send(f"An error occurred while processing the file: {str(e)}", ephemeral=True)

@tree.command(name="site_builder", description="Have Aina-chan Make You A Website!!!")
async def open_feedback(interaction: discord.Interaction):
    # Create the modal
    modal = WebsiteBuilderModal()
    
    # Send the modal to the user
    await interaction.response.send_modal(modal)

@tree.command(name="refresh_tunnel", description="Get Flare-chan to make a new site~")
async def refresh_tunnel(interaction: discord.Interaction):
    await interaction.response.send_message("Making a brand new link just for you senpai~", ephemeral=True)
    await flare.create_cloudflare_tunnel(interaction.channel)

@tree.command(name="get_tunnel", description="Get the current site!")
async def get_tunnel(interaction: discord.Interaction):
    response = flare.get_tunnel_info()
    await interaction.response.send_message(response, ephemeral=True)

async def process_queue():
    """Worker function to process items in the queue without blocking the main event loop"""
    while True:
        try:
            # Check if there's anything in the queue
            if not config.queue_to_process_everything.empty():
                # Get item from queue
                item = config.queue_to_process_everything.get_nowait()
                
                # Process the item in a separate thread
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    thread_pool,
                    process_item,  # You'll need to implement this function in aina module
                    item
                )
                
                # Mark the task as done
                config.queue_to_process_everything.task_done()
            
            # Always yield control back to the event loop
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error processing queue item: {e}")
            await asyncio.sleep(1)

def process_item(item):
    """Process a single queue item - this runs in a separate thread"""
    # Replace with your actual processing logic
    aina.process_website_request(item['title'], item['content'])

@client.event
async def on_ready():
    # Start the queue processor
    asyncio.create_task(process_queue())
    
    # Start any other background tasks
    asyncio.create_task(aina.work())
    
    # Sync commands with Discord
    await tree.sync()
    await flare.create_cloudflare_tunnel(None)
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("Bot is ready!")

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
if __name__ == "__main__":
    
    client.run(config.discord_token)