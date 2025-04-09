<div align="center">
  <h1 style="color: #9c88ff; margin: 10px 0">🌟 Aina-chan Discord Integration 🌟</h1>
  <img src="https://i.imgur.com/VQ2eNhq.jpeg" width="100" style="border-radius:50%;box-shadow:0 5px 15px rgba(156,136,255,0.3)">
  <p>Invite Aina-chan Into Your Server!</p>
</div>

## 🌸 Overview

**Aina-chan Discord Integration** is a Discord bot that brings the power of [Aina Website Builder](https://github.com/Iteranya/Aina-Website-Builder) directly to your Discord server! With simple slash commands, users can create, upload, and share beautiful websites without ever leaving Discord.

Generate complete websites from text prompts or host your own HTML files with ease. Aina-chan specializes in creating visually appealing websites quickly - perfect for prototyping, creative projects, or just having fun!

## ✨ Features

- **AI-Powered Website Generation**: Create complete websites from text descriptions
- **HTML Hosting**: Upload your own HTML files for instant hosting
- **Browsable Gallery**: View all created websites through an easy-to-use gallery
- **Persistent Tunneling**: Access your websites anytime with persistent URLs

## 🤖 Commands

Aina-chan offers the following slash commands:

| Command | Description |
|---------|-------------|
| `/site_builder` | Opens a modal where you can provide a title and description for your website. Aina will generate a complete website based on your input! |
| `/uploadhtml` | Skip the generation process and upload your own static HTML file directly for hosting. |
| `/tunnel` | Create or refresh the tunnel to Aina's server, where all websites are stored and displayed. |
| `/tunnel_info` | Get the current URL to Aina's website gallery to browse all created sites. |

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Discord Bot Token
- Basic knowledge of Discord bots

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
     AI_TOKEN="your_ai_token_here"
     DISCORD_TOKEN="your_discord_token_here"
     ```
   - Optionally, configure the base LLM and model settings in `config.py`

3. Run the appropriate starter script:
   - Windows: Double-click `start.cmd` or run it from the command line
   - Linux/Mac: `./start.sh`

These scripts will automatically:
- Create a virtual environment if it doesn't exist
- Install required dependencies
- Download cloudflared if needed
- Start both the server and Discord bot

## ⚙️ Configuration

The bot can be configured through:

- `.env` file - Contains your API tokens
- `config.py` - Contains settings for the base LLM and model

## 🏗️ Architecture

Under the hood, Aina-chan Discord Integration utilizes:
- FastAPI backend for handling website requests and hosting
- Jinja2 templates for the gallery homepage
- File-based storage system for all generated websites
- Cloudflare tunneling for external access

## 🌐 Examples

**Example website prompt:**
```
/site_builder
Title: My Bakery Shop
Description: A cozy bakery website with a vintage feel. Should have sections for our menu, about us story, and a contact form. Use warm colors like browns and cream.
```

## 🔗 Related Projects

- [Aina Website Builder](https://github.com/Iteranya/Aina-Website-Builder) - The core AI website generator that powers this Discord bot

## 📝 License

This project is licensed under the GPL-3 License - see the LICENSE file for details.

## 👩‍💻 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## 🙏 Acknowledgements

- Built with ❤️ by [Iteranya](https://github.com/Iteranya)
- Powered by Aina-chan Website Builder