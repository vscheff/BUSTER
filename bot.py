# Main starting file for BUSTER.
# This file creates the Bot object, loads the cogs, and starts the event loop

from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
import discord

# env must be loaded before importing ./cogs.py
load_dotenv()
TOKEN = getenv('DISCORD_TOKEN')  # API token for the bot
GUILD = getenv('DISCORD_GUILD')  # ID of desired guild for bot to interact with
if TOKEN is None or GUILD is None:
    exit('Environment file missing/corrupted. Halting now!')

# Local dependencies
from cogs import add_cogs
from help_command import CustomHelpCommand

bot = commands.Bot(command_prefix='$', help_command=CustomHelpCommand(), intents=discord.Intents.all())

# Runs when bot has successfully logged in
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    if not bot.cogs:
        add_cogs(bot, guild)

    print(f'{bot.user} is connected to the following guild:\n'
          f'{guild.name} (ID: {guild.id})\n'
          f'Guild Members: {len(guild.members)}\n')

# Begin the bot's event loop
bot.run(TOKEN)
