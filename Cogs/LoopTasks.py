from discord.ext import commands, tasks
from os import getenv
from dotenv import load_dotenv
from datetime import datetime, timedelta
import discord

load_dotenv
GUILD = getenv('DISCORD_GUILD')
WELCOME_CHANNEL_ID = int(getenv('WELCOME_CH_ID'))
ROLE_CLAIM_CHANNEL_ID = int(getenv('ROLECLM_CH_ID'))


class LoopTasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild = None
        self.ch_welcome = None
        self.ch_roleClaim = None
        
        self.purge_channels.start()
    
    @tasks.loop(hours=24)
    async def purge_channels(self):
        print(f'Beginning default channel purge #{self.purge_channels.current_loop}:')
        del_before = datetime.now() - timedelta(hours=76)
        print(f'Deleting messages before {del_before}')
        for channel in (self.ch_welcome, self.ch_roleClaim):
            await self.delete_messages(channel, del_before)
        print('Purge successfully completed!\n')
    
    async def delete_messages(self, channel, del_before):
        deleted = await channel.purge(before=del_before)
        print(f'Deleted {len(deleted)} messages from {channel.name}')
        
    @purge_channels.before_loop
    async def before_purge(self):
        print('Starting default channel purge 24 hour loop')
        await self.bot.wait_until_ready()
        self.guild = discord.utils.get(self.bot.guilds, name=GUILD)
        self.ch_welcome = self.guild.get_channel(WELCOME_CHANNEL_ID)
        if self.ch_welcome is None:
            print('WARNING: Welcome channel not found. Loop not started.\n')
            self.purge_channels.cancel()
            return
        self.ch_roleClaim = self.guild.get_channel(ROLE_CLAIM_CHANNEL_ID)
        if self.ch_roleClaim is None:
            print('WARNING: Role Claim channel not found. Loop not started.\n')
            self.purge_channels.cancel()
            return
        print('Loop successfully started!\n')

