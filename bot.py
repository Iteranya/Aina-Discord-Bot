import discord
from discord import app_commands
from discord.ui import Modal, TextInput

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
    
    description_input = TextInput(
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
        # For example: save_to_database(self.title_input.value, self.description_input.value)
        print(f"Received form data - Title: {self.title_input.value}, Description: {self.description_input.value}")

@tree.command(name="uploadhtml", description="Upload an HTML file")
async def upload_html(interaction: discord.Interaction, html_file: discord.Attachment):
    try:
        # Check if the file is an HTML file
        if not html_file.filename.endswith('.html'):
            await interaction.response.send_message("Please give me the HTML File Senpai~", ephemeral=True)
            return
            
        # Read the file content
        html_content = await html_file.read()
        
        # Process the HTML file (backend handling)
        print(f"Received HTML file: {html_file.filename}, Size: {len(html_content)} bytes")
        
        # Here you would process the HTML content with your backend logic
        # process_html_file(html_content)
        
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
    # Sync commands with Discord
    await tree.sync()
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("Bot is ready!")

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
if __name__ == "__main__":
    client.run("YOUR_BOT_TOKEN")