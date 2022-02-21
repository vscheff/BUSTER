# Cog that holds all commands related to server/bot utility

from discord.ext import commands
from datetime import datetime, timedelta
import discord


class Utility(commands.Cog):

    # attr bot - our client
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # $invite command used to retrieve invite linke and QR code for the server
    @commands.command(help='Returns an invite link and QR code for inviting new users to the server',
                      brief='Returns an invite link for the server')
    async def invite(self, ctx):
        await ctx.send(content='*Invite link:* https://discord.gg/kfPrgSuHA6\n\n*QR Code:*',
                       file=discord.File('./qr.png'))

    # $ping command used to test bot readiness and latency
    @commands.command(help='Returns "pong" if the bot is online.\nExample: $ping',
                      brief='Returns "pong" if the bot is online.')
    async def ping(self, ctx):
        await ctx.send(f'pong (*{round(self.bot.latency * 1000)}ms*)')

    # $execute command used for ACE
    # param arg - all user input following the command-name
    @commands.command(help='Attempts to execute the given code in Python\n'
                           'This command will only accept one-line statements\n'
                           'Example: $execute 6 * 7',
                      brief='Executes given Python code')
    async def execute(self, ctx, *, arg):
        try:
            compiled = compile(arg, '<string>', 'eval')
            obj = eval(compiled)
            if isinstance(obj, (int, float)):
                obj = str(obj)
            elif isinstance(obj, (list, set, tuple, dict)):
                obj = ', '.join([str(i) for i in obj])
            ret_list = []
            while len(obj) >= 2000:
                ret_list.append(obj[:2000])
                obj = obj[2000:]
            ret_list.append(obj)
            for msg in ret_list:
                await ctx.send(msg)
        except SyntaxError as e:
            await ctx.send(f'Bad Syntax: Error occurred at Index [{e.offset-1}], '
                           f'Character ({e.text[e.offset-1]})')
        except Exception as e:
            await ctx.send(str(e))

    # $info command used to provide some info on this bot
    @commands.command(help='Provides a brief synopsis of BUSTER, including a link to his Open Source code',
                      brief='Provides a brief synopsis of BUSTER')
    async def info(self, ctx):
        await ctx.send(f'Hello! I am BUSTER, your friendly automation bot!\n'
                       f'I was developed by WMU students, and am hosted locally in Kalamazoo!\n'
                       f'If you would like to know me more intimately '
                       f'my Open Source code can be found here:\n\n'
                       f'https://github.com/vscheff/BUSTER')

    # $ready command used as a "all-systems-go" check for the bot
    @commands.command(hidden=True)
    async def ready(self, ctx):
        await ctx.send(f'Websocket closed: {self.bot.is_closed()}\n'
                       f'Internal cache ready: {self.bot.is_ready()}\n'
                       f'Websocket rate limited: {self.bot.is_ws_ratelimited()}')

    # $purge command used to bulk delete messages from a text channel
    # param before - int representing the number of days, before which messages will be deleted
    # param  after - int representing the number of days, before which messages will NOT be deleted
    @commands.command(hidden=True)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, before: int, after: int = None):
        del_before = datetime.now() - timedelta(days=before)
        if after is None:
            await ctx.send(f'Deleting messages sent before **{del_before.isoformat(" ", "minutes")}**')
            deleted = await ctx.channel.purge(before=del_before)
        else:
            if after <= before:
                await ctx.send('Bad argument, second given integer must be larger than the first.')
                return
            # Subtract the remaining days to get the lower-limit
            del_after = del_before - timedelta(days=after - before)
            await ctx.send(f'Deleting messages between **{del_after.isoformat(" ", "minutes")}** '
                           f'and **{del_before.isoformat(" ", "minutes")}**.')
            deleted = await ctx.channel.purge(before=del_before, after=del_after)
        await ctx.send(f'Successfully deleted {len(deleted)} messages from this channel!')

    # Called if $purge encounters an unhandled exception
    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            print(f'$purge command failed: User {ctx.author.name} lacks permissions')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('You must include an integer with this command.\n'
                           'Example: $purge 3\n'
                           'That command will delete all messages older than 3 days.\n\n'
                           'Alternatively, you can include two integers to declare a range.\n'
                           'Example: $purge 3 42\n'
                           'That command will delete all messages older than 3 days, '
                           'but not older than 42 days.\n\n')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send('Bad argument, please only use integers with this command.\n')
        else:
            print(f'$purge command failed with error:\n\n{error}')
