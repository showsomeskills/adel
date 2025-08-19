# main.py

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import importlib
import glob
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# Simple healthcheck server (works in Python 3.12)
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    server = HTTPServer(("0.0.0.0", 8080), HealthHandler)
    server.serve_forever()

Thread(target=start_health_server, daemon=True).start()

load_dotenv()

TOKEN = os.getenv('TOKEN')
DEFAULT_PREFIX = os.getenv('PREFIX', '-')  # fallback to '-' if PREFIX not set

intents = discord.Intents.default()
intents.message_content = True  # allows reading message content
intents.members = True          # crucial for member-related commands

def prefix_check(bot, message):
    prefixes = [DEFAULT_PREFIX]

    # Check if message starts with any known prefix
    for p in prefixes:
        if message.content.startswith(p):
            return p

    # If no prefix: check if first word matches a command name (case-insensitive)
    first_word = message.content.split(' ')[0]
    if first_word.lower() in [cmd.lower() for cmd in bot.all_commands]:
        return ''  # empty prefix to allow prefixless command trigger

    # Else fallback to default mention prefix
    return commands.when_mentioned(bot, message)

# Enable case-insensitive commands by setting case_insensitive=True
bot = commands.Bot(command_prefix=prefix_check, intents=intents, case_insensitive=True)

# Remove default help command to load your custom help command without conflict
bot.remove_command('help')

# Dynamically load command modules from commands folder
for file in glob.glob('./commands/*.py'):
    cmd_name = file[11:-3]  # strip './commands/' and '.py'
    module = importlib.import_module(f'commands.{cmd_name}')
    if hasattr(module, 'setup'):
        module.setup(bot)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.event
async def on_command_error(ctx, error):
    from discord.ext.commands import CheckFailure

    if isinstance(error, CheckFailure):
        await ctx.send("You do not have permission to use this command.", delete_after=5)
        return
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("**Unknown command.** Type `.help` to see commands.", delete_after=5)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("**You don't have permission to use this command.**", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("**Missing arguments for this command.**", delete_after=5)
    else:
        await ctx.send(f"An error occurred: **{str(error)}**", delete_after=5)
        raise error  # re-raise to help with debugging if needed

bot.run(TOKEN)
