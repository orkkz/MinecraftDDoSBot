#                                   MCPentest

**MCPentest** is a Minecraft pentesting tool that is currently capable of performing the following actions:

## Available Commands

- **`!kickall <IP:PORT>`**  
  Kicks all players connected to the specified Minecraft server.  
  **Usage**: `!kickall 127.0.0.1:25565`

- **`!attack <IP:PORT> <attack_type> <duration>`**  
  Launches bots or sends malicious packets to attack the Minecraft server.  
  **Usage**: `!attack 127.0.0.1:25565 bot 60`  
  **Attack types**: `bot`, `packet`

- **`!scanports <IP>`**  
  Scans open ports on the specified server IP and checks for active services like Minecraft or RCON.  
  **Usage**: `!scanports 127.0.0.1`

- **`!serverinfo <IP:PORT>`**  
  Retrieves detailed information about a Minecraft server, including its ping, player count, server version, and more.  
  **Usage**: `!serverinfo 127.0.0.1:25565`

- **`!nmap <IP>`**  
  Runs an Nmap scan on the specified IP to check for open ports and vulnerabilities.  
  **Usage**: `!nmap 192.168.1.1`

- **`!checkrcon <IP:PORT>`**  
  Checks if the specified IP and port are running an RCON server or a Minecraft server.  
  **Usage**: `!checkrcon 127.0.0.1:25575`

---

> **Note**: These commands are intended for testing Minecraft servers that you own or have explicit permission to test. Use them responsibly.


# Installation

Clone the repository
```bash  
git clone https://github.com/orkkz/MCPentest.git  
cd MCPentest  
```

Save your discord token to .env as TOKEN
```bash
echo "TOKEN=YOUR DISCORD BOT TOKEN" > .env
```

Add executable permissions
```bash
chmod +x install.sh
```

Run the Installer
```bash
./install.sh
```

Start the discord bot
```bash
python3 app.py
```
