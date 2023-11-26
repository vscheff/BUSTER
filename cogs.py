# Common collection space for all of the bots cogs
# This file imports the cogs from each file and adds them to the bot

# Local dependencies
from Cogs.Classes import Classes
from Cogs.Utility import Utility
from Cogs.Random import Random
from Cogs.LoopTasks import LoopTasks

# Adds each cog to the bot, this is called once the bot is ready for the first time
# param   bot - commands.Bot object containing our client
# param guild - discord.Guild object containing the target server
async def add_cogs(bot, guild):
    await bot.add_cog(Classes(bot, guild))
    await bot.add_cog(Random())
    await bot.add_cog(Utility(bot))
    await bot.add_cog(LoopTasks(bot, guild))
