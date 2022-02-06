from Cogs.Classes import Classes
from Cogs.Utility import Utility
from Cogs.Random import Random


def setup(bot):
    bot.add_cog(Classes(bot))
    bot.add_cog(Random())
    bot.add_cog(Utility(bot))
