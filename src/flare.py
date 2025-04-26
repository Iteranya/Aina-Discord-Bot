import asyncio
import re
import json
import os
from dataclasses import dataclass
import platform

@dataclass
class FlareTunnel:
    name: str
    description: str
    localhost: str
    flarelink: str
    accesslink: str

# File to store tunnel information
TUNNEL_INFO_FILE = 'aina_tunnel_info.json'
TUNNEL_NAME = "AinaService"  # Hardcoded name
LOCALHOST_PORT = "http://127.0.0.1:5454"  # Hardcoded port

async def create_cloudflare_tunnel(channel):
    """Create a Cloudflare tunnel for port 5454"""
    # Load existing tunnel info
    try:
        with open(TUNNEL_INFO_FILE, 'r') as f:
            tunnel_info = json.load(f)
    except FileNotFoundError:
        tunnel_info = {}

    cmd = get_cloudflared_command(LOCALHOST_PORT)

    # Start the process
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Pattern to match the Cloudflare URL
    url_pattern = re.compile(r'https?://[a-zA-Z0-9-]+\.trycloudflare\.com')

    # Wait for the URL to appear in the output
    tunnel_created = False
    while True:
        line = await process.stderr.readline()
        if not line:
            break
        line = line.decode('utf-8')
        print(line, end='')  # Print the line for debugging
        match = url_pattern.search(line)
        if match and not tunnel_created:
            cloudflare_url = match.group(0)
            # Store the URL
            access = cloudflare_url
            tunnel = FlareTunnel(
                name=TUNNEL_NAME,
                description="Aina's service tunnel for port 5544",
                localhost=LOCALHOST_PORT,
                flarelink=cloudflare_url,
                accesslink=access
            )
            store_tunnel_info(tunnel)
            if channel!=None:
                await channel.send(f"Tunnel activated! Access your service at: {access}")
            tunnel_created = True

    # Wait for the process to complete in the background
    await process.wait()

    return None

def store_tunnel_info(tunnel: FlareTunnel):
    """Store tunnel information in a JSON file"""
    try:
        with open(TUNNEL_INFO_FILE, 'r') as f:
            tunnel_info = json.load(f)
    except FileNotFoundError:
        tunnel_info = {}

    # Store the tunnel info
    tunnel_info[tunnel.name] = {
        'description': tunnel.description,
        'localhost': tunnel.localhost,
        'flarelink': tunnel.flarelink,
        'accesslink': tunnel.accesslink
    }

    with open(TUNNEL_INFO_FILE, 'w') as f:
        json.dump(tunnel_info, f, indent=4)

    return f"Tunnel for {tunnel.name} has been updated."

def get_tunnel_info():
    """Get information about the existing tunnel"""
    try:
        with open(TUNNEL_INFO_FILE, 'r') as f:
            tunnel_info = json.load(f)
    except FileNotFoundError:
        return "No tunnel information available. Use `/aina tunnel` to create one!"

    if TUNNEL_NAME not in tunnel_info:
        return "No tunnel has been created yet. Use `/aina tunnel` to create one!"

    details = tunnel_info[TUNNEL_NAME]
    accesslink = details.get("accesslink", "")
    description = details.get("description", "Aina's service tunnel")
    status = f"Active at {accesslink}" if accesslink else "Inactive"

    message = f"**Tunnel Information**\n"
    message += f"**Name:** {TUNNEL_NAME}\n"
    message += f"**Description:** {description}\n"
    message += f"**Status:** {status}\n\n"
    message += "If the link doesn't work, use the `/aina tunnel` command to reactivate it."

    return message

def clear_tunnel_links():
    """Clear the tunnel links (useful on bot restart)"""
    try:
        with open(TUNNEL_INFO_FILE, 'r') as f:
            tunnel_info = json.load(f)
    except FileNotFoundError:
        return

    # Clear the links if our tunnel exists
    if TUNNEL_NAME in tunnel_info:
        tunnel_info[TUNNEL_NAME]['accesslink'] = ""
        tunnel_info[TUNNEL_NAME]['flarelink'] = ""

    with open(TUNNEL_INFO_FILE, 'w') as f:
        json.dump(tunnel_info, f, indent=4)

    print(f"Cleared links for {TUNNEL_NAME} tunnel.")

def get_cloudflared_command(port):
    system = platform.system()
    
    if system == "Windows":
        cloudflared = "cloudflared.exe"
        cmd = f"{cloudflared} tunnel --url {port}"
    else:  # Linux, macOS, etc.
        # Check if cloudflared is in current directory
        if os.path.isfile("./cloudflared"):
            cloudflared = "./cloudflared"
        else:
            # Assume cloudflared is in PATH
            cloudflared = "cloudflared"
        
        cmd = f"{cloudflared} tunnel --url {port}"
    
    return cmd