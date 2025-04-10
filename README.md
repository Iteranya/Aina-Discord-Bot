<div align="center">
  <h1 style="color: #9c88ff; margin: 10px 0">🌟 Aina Website Builder 🌟</h1>
  <img src="https://i.imgur.com/VQ2eNhq.jpeg" width="100" style="border-radius:50%;box-shadow:0 5px 15px rgba(156,136,255,0.3)">
  <p>Create Beautiful Websites with AI - Now with Discord Integration!</p>
</div>

## 🌸 Overview

**Aina Website Builder** is an AI-powered platform that allows you to create beautiful websites from simple text descriptions or by directly editing HTML. With the intuitive interface, you can quickly prototype, iterate, and deploy websites without any coding knowledge!

Now featuring full Discord integration, Aina brings its website creation powers directly to your Discord server. Create and share websites without ever leaving Discord using simple slash commands.

## ✨ Key Features

### Interactive Website Builder
![Website Builder Preview](https://github.com/user-attachments/assets/77c26223-f388-46c3-848c-d8a5eb4854b1)

- **AI-Powered Generation**: Create complete websites from text descriptions
- **Live HTML Editor**: View and edit your website in real-time
- **Instant Preview**: See changes as you make them
- **One-Click Publishing**: Deploy your website with a single click

### Discord Integration
- **Create From Discord**: Generate websites directly in your Discord server
- **HTML Hosting**: Upload your own HTML files for instant hosting
- **Browsable Gallery**: View all created websites through an easy-to-use gallery
- **Persistent Tunneling**: Access your websites anytime with permanent URLs

## 🚀 Getting Started

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Iteranya/Aina-Discord-Bot.git
   cd Aina-Discord-Bot
   ```
2. Configure environment variables:
   - Copy `example.env` to `.env`
   - Update the values:
     ```
     DISCORD_TOKEN="your_discord_token_here"
     ```
3. Run the appropriate starter script:
   - Windows: Double-click `start.cmd` or run it from the command line
   - Linux/Mac: `./start.sh`

These scripts will automatically:
- Create a virtual environment if it doesn't exist
- Install required dependencies
- Download cloudflared if needed
- Start both the server and Discord bot (Note, if Discord Key isn't supplied, the Discord Bot automatically closes, but the server is still accessible)

### Accessing the Website Builder
1. After running the start script, the local server will be running
2. Open your browser and go to `http://localhost:5454` to view the gallery of all created websites
3. Navigate to `http://localhost:5454/site-builder` to access the interactive website builder
4. Open the settings menu in the bottom right to manage your connection settings
5. Enter your website description, generate, and edit in real-time!

### Using the Discord Bot
Once your Website Builder is running the bot is now functional, you can use the slash commands to create websites directly from Discord.

## 🤖 Discord Commands

Aina offers the following slash commands in Discord:

| Command | Description |
|---------|-------------|
| `/site_builder` | Opens a modal where you can provide a title and description for your website. Aina will generate a complete website based on your input! |
| `/uploadhtml` | Skip the generation process and upload your own static HTML file directly for hosting. |
| `/tunnel` | Create or refresh the tunnel to Aina's server, where all websites are stored and displayed. |
| `/tunnel_info` | Get the current URL to Aina's website gallery to browse all created sites. |

## ⚙️ Configuration

The application can be configured through:
- `.env` file - Contains your API tokens
- `config.py` - Contains settings for the base LLM and model

## 🏗️ Architecture

Under the hood, Aina Website Builder utilizes:
- FastAPI backend for handling website requests and hosting
- Interactive website builder with real-time preview
- Jinja2 templates for the gallery homepage
- File-based storage system for all generated websites
- Cloudflare tunneling for external access

## 🐛 Known Bugs and Issues

This is a Solo-dev's work with minimal expertise in Javascript or Web, known bugs does exist:
- Lack of clear error and visual feedback
- No admin panel (yet)
- The UI doesn't make it clear enough that for the Discord Bot to work, you need to setup the API inside the Website Builder page.
- Doesn't show errors on screen, harder to debug.

## 🌐 Examples

**Example website prompt:**
```
Title: My Bakery Shop
Description: A cozy bakery website with a vintage feel. Should have sections for our menu, about us story, and a contact form. Use warm colors like browns and cream.
```

## 🔗 Related Projects

- Original [Aina Website Builder](https://github.com/Iteranya/Aina-Website-Builder) project

## 📝 License

This project is licensed under the AGPL-3 License - see the LICENSE file for details.

## 👩‍💻 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## 🙏 Acknowledgements

- Built with ❤️ by [Iteranya](https://github.com/Iteranya)
