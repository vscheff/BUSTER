# Cog that holds all looping tasks for the bot

from discord.ext import commands, tasks
from os import getenv
from datetime import datetime, timedelta
import discord

WELCOME_CHANNEL_ID = int(getenv('WELCOME_CH_ID'))     # ID of channel 'welcome'
ROLE_CLAIM_CHANNEL_ID = int(getenv('ROLECLM_CH_ID'))  # ID of channel 'claim-your-major-and-classes'


class LoopTasks(commands.Cog):

    # attr bot - our client
    # attr guild - target Discord server
    def __init__(self, bot: commands.Bot, guild: discord.Guild):
        self.bot = bot
        self.guild = guild
        self.ch_welcome = None
        self.ch_roleClaim = None

        self.purge_channels.start()

    # Purges general channels of messages older than 3 days once a day
    @tasks.loop(hours=24)
    async def purge_channels(self):
        print(f'\nBeginning default channel purge #{self.purge_channels.current_loop}:')
        del_before = datetime.now() - timedelta(hours=72)
        print(f'Deleting messages before {del_before}')
        for channel in (self.ch_welcome, self.ch_roleClaim):
            # Delete all messages sent before del_before
            deleted = await channel.purge(before=del_before)
            print(f'Deleted {len(deleted)} messages from {channel.name}')
        print('Purge successfully completed!\n')

    # Called before the purge_channels loop starts
    @purge_channels.before_loop
    async def before_purge(self):
        await self.bot.wait_until_ready()
        print('Starting default channel purge 24 hour loop')
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
