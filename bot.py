import discord
from discord import app_commands
from discord.ui import Modal, TextInput
from src import aina
import config
import asyncio
# Bot setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)



class WebsiteBuilderModal(Modal, title="Make Your Own Website!!!"):
    # Create text inputs for the modal
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
        # Acknowledge the submission
        await interaction.response.send_message(f"Thank You Senpai!!!\n\nPlease wait warmly while Aina-chan makes  the website for you! Ehehe~", ephemeral=True)
        
        # Here you would process the data on the backend
        config.queue_to_process_everything.put_nowait({
            "title" : self.title_input.value,
            "content":self.content_input.value
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

        # Process the HTML file (backend handling)
        print(f"Received HTML file: {html_file.filename}, Size: {len(html_content)} bytes")
        
        # Here you would process the HTML content with your backend logic
        aina.save_html(html_content,html_file.filename)
        
        await interaction.response.send_message(f"Thank You Senpai! Aina-chan will take care of it~", ephemeral=True)
    
    except Exception as e:
        await interaction.response.send_message(f"An error occurred while processing the file: {str(e)}", ephemeral=True)

@tree.command(name="site_builder", description="Have Aina-chan Make You A Website!!!")
async def open_feedback(interaction: discord.Interaction):
    # Create the modal
    modal = WebsiteBuilderModal()
    
    # Send the modal to the user
    await interaction.response.send_modal(modal)

@client.event
async def on_ready():
    asyncio.create_task(aina.work())
    # Sync commands with Discord
    await tree.sync()
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("Bot is ready!")

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
if __name__ == "__main__":
    client.run(config.discord_token)