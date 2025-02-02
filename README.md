#                                   MCPentest

**MCPentest** is a Minecraft pentesting tool that is currently capable of performing the following actions:

## Available Commands

- **`!kickall <IP:PORT>`**  
  Kicks all players connected to the specified Minecraft server.  
  **Usage**: `!kickall 127.0.0.1:25565`

- **`!crash <IP:PORT> <protocol> <attack_type> <duration> <CPS>`**  
  Launches bots or sends malicious packets to attack the Minecraft server.  
  **Usage**: `!attack 127.0.0.1:25565 bot 60`  
  **Attack types**: `join`, `legitjoin`, `localhost`, `invalidnames`, `longnames`, `botjoiner`, `power`, `spoof`, `ping`, `spam`, `killer`, `nullping`, `charonbot`, `multikiller`, `packet`, `handshake`, `bighandshake`, `query`, `bigpacket`, `network`, `randombytes`, `spamjoin`, `nettydowner`, `ram`, `yoonikscry`, `colorcrasher`, `tcphit`, `queue`, `botnet`, `tcpbypass`, `ultimatesmasher`, `sf`, `nabcry`

- **`!kickev <IP:PORT> <duration>`**  
  Kicks specific players connected to the specified Minecraft server.  
  **Usage**: `!kickall 127.0.0.1:25565 60`

- **`!port <hostname>`**  
  Fetch the IP and port of a Minecraft server from the DNS records.  
  **Usage**: `!port hypixel.net`

- **`!capture <IP:PORT> <duration>`**  
  Captures chat messages from the server for the specified duration.
  **Usage**: `!capture 127.0.0.1:25565 60`

- **`!chat <IP:PORT> <username> <version>`**  
  Creates a persistent chat session with the specified Minecraft server. Type !exit to stop the chat and delete the channel.
  **Usage**: `!capture 127.0.0.1:25565 60`

- **`!serverinfo <IP:PORT>`**  
  Retrieves detailed information about a Minecraft server, including its ping, player count, server version, and more.  
  **Usage**: `!serverinfo 127.0.0.1:25565`

- **`!nmap <IP>`**  
  Runs an Nmap scan on the specified IP to check for open ports and vulnerabilities.  
  **Usage**: `!nmap 192.168.1.1`
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
