from discord.ext import commands
import discord


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(help='Returns an invite link and QR code for inviting new users to the server',
                      brief='Returns an invite link for the server')
    async def invite(self, ctx):
        await ctx.send(content='Invite link: https://discord.gg/kfPrgSuHA6', 
                       file=discord.File('./qr.png'))

    @commands.command(help='Returns "pong" if the bot is online.\nExample: $ping',
                      brief='Returns "pong" if the bot is online.')
    async def ping(self, ctx):
        await ctx.send(f'pong (*{round(self.bot.latency * 1000)}ms*)')

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
    
    @commands.command(help='Provides a brief synopsis of BUSTER, including a link to his Open Source code',
                      brief='Provides a brief synopsis of BUSTER')
    async def info(self, ctx):
        await ctx.send(f'Hello! I am BUSTER, your friendly automation bot!\n'
                       f'I was developed by WMU students, and am hosted locally in Kalamazoo!\n'
                       f'If you would like to know me more intimately '
                       f'my Open Source code can be found here:\n\n'
                       f'https://github.com/vscheff/BUSTER')
                    
    @commands.command(hidden=True)
    async def ready(self, ctx):
        await ctx.send(f'Websocket closed: {self.bot.is_closed()}\n'
                       f'Internal cache ready: {self.bot.is_ready()}\n'
                       f'Websocket rate limited: {self.bot.is_ws_ratelimited()}')
