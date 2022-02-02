import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from help_command import CustomHelpCommand

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', help_command=CustomHelpCommand(), intents=intents)
bot.load_extension('cogs')


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)

    print(f'{bot.user} is connected to the following guild:\n'
          f'{guild.name}(id: {guild.id})')
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

bot.run(TOKEN)
