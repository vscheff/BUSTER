# Cog that holds all commands related to server/bot utility

from discord.ext import commands
from datetime import datetime, timedelta
from PIL import Image
import discord
import os
import qrcode


class Utility(commands.Cog):

    # attr      bot - our client
    # attr inv_file - filename/path for storage of inivite link QR image
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.inv_file = './img/qr.png'

    # $invite command used to retrieve invite link and QR code for the server
    @commands.command(help='Returns an invite link and QR code for inviting new users to the server',
                      brief='Returns an invite link for the server')
    async def invite(self, ctx):
        await ctx.send(content='*Invite link:* https://discord.gg/kfPrgSuHA6\n\n*QR Code:*',
                       file=discord.File(self.inv_file))

    # $set_invite command used to update and generate the invite link QR image
    @commands.command(hidden=True,
                      help='Generates and saves a new QR image for the $invite command\n'
                           'Example: `$invite https://discord.gg/kfPrgSuHA6`',
                      brief='Generate a new QR image for $invite')
    @commands.has_permissions(manage_roles=True)
    async def set_invite(self, ctx, *, arg):
        img = self.make_qr(arg)
        img.save(self.inv_file)
        if os.path.exists(self.inv_file):
            await ctx.send('New invite QR code successfully generated.')
        else:
            await ctx.send('Error occured. QR code not generated.')

    # Called if $set_invite encounters an unhandled exception
    @set_invite.error
    async def set_invite_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            print(f'$set_invite command failed: User {ctx.author.name} lacks permissions')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('You must include the server invite link with this command.\n'
                           'Example: `$set_invite https://discord.gg/kfPrgSuHA6`')
        else:
            print(f'$set_invite command failed with error:\n\n{error}')

    # $qr command used to generate QR code images
    # param arg - all user input following command-name
    @commands.command(help='Generate a QR code for input data\nExample: `$qr gowmu.wmich.edu`',
                      brief='Generate a QR code')
    async def qr(self, ctx, *, arg):
        # Filename/path for temporary storage of QR image
        temp_store = './img/temp_qr.png'
        img = self.make_qr(arg)
        img.save(temp_store)
        if os.path.exists(temp_store):
            await ctx.send(file=discord.File(temp_store))
            os.remove(temp_store)
        else:
            print('Error occured while generating QR code. Temp file not created/deleted.')

    # Called if $qr encounters an unhandled exception
    @qr.error
    async def qr_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('You must include a string of data with this command.\n'
                           'Example: `$qr gowmu.wmich.edu`')
        else:
            print(f'$qr command failed with error:\n\n{error}')

    # Used by $qr and $set_invite to creat a QR code image
    # param data - string of data to encode in the QR image
    def make_qr(self, data):
        qr = qrcode.QRCode(version=None,                                       # Nonetype allows dynamic QR size
                           error_correction=qrcode.constants.ERROR_CORRECT_L,  # L <= 7% error correction
                           box_size=10,
                           border=2)
        qr.add_data(data)
        # Construct the QR code with the 'fit' modifier to scale the input data
        qr.make(fit=True)
        return qr.make_image(fill_color='black', back_color='white')

    # $ping command used to test bot readiness and latency
    @commands.command(help='Returns "pong" and round-trip latency if the bot is online.',
                      brief='Returns "pong" if the bot is online.')
    async def ping(self, ctx):
        await ctx.send(f'pong (*{round(self.bot.latency * 1000)}ms*)')

    # $execute command used for ACE
    # param arg - all user input following the command-name
    @commands.command(hidden=True,
                      help='Attempts to execute the given code in Python\n'
                           'This command will only accept one-line statements\n'
                           'Example: `$execute 6 * 7`',
                      brief='Executes given Python code')
    @commands.has_permissions(administrator=True)
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
    @commands.command(hidden=True,
                      help='Performs an "All-Systems-Go" check for the bot, and returns a status report.',
                      brief='Check for "All-Systems-Go"')
    async def ready(self, ctx):
        await ctx.send(f'Websocket closed: {self.bot.is_closed()}\n'
                       f'Internal cache ready: {self.bot.is_ready()}\n'
                       f'Websocket rate limited: {self.bot.is_ws_ratelimited()}')

    # Hidden $add_roles command used to bulk add a collection of roles
    # param filename - string representing the filepath for role definition file
    @commands.command(hidden=True,
                      help='Add roles from an input file in the master directory\n'
                           'Example: `$add_roles new_roles.txt`',
                      brief='Bulk add roles')
    @commands.has_permissions(manage_roles=True)
    async def add_roles(self, ctx, filename):
        try:
            with open(filename, 'r') as inFile:
                # A list of the names of all existing roles
                role_names = [i.name for i in self.guild.roles]
                # This will be the role color of all added roles
                color = discord.Colour.orange()
                count_success = 0
                count_failure = 0
                await ctx.send('Beginning bulk role creation...')
                for line in inFile:
                    name = line.strip()
                    if name not in role_names:
                        print(f'Creating role {count_success}: {name}')
                        await self.guild.create_role(name=name, colour=color)
                        count_success += 1
                    else:
                        print('Skipping redundant role: {name}')
                        count_failure += 1
                await ctx.send(f'Operation complete\n'
                               f'Total Roles Added: {count_success}\n'
                               f'Redundant Roles Skipped: {count_failure}')
        except FileNotFoundError:
            await ctx.send(f'No file in directory found with name: {filename}')

    # Called if $add_roles encounters an unhandled exception
    @add_roles.error
    async def add_roles_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            print(f'$add_roles command failed: User {ctx.author.name} lacks permissions')
        else:
            print(f'$add_roles command failed with error:\n\n{error}')

    # $purge command used to bulk delete messages from a text channel
    # param before - int representing the number of days, before which messages will be deleted
    # param  after - int representing the number of days, before which messages will NOT be deleted
    @commands.command(hidden=True,
                      help='Delete all messages in a channel older than a give number of days.\n'
                           'Example: `$purge 3`\n'
                           'That command will delete all messages older than 3 days.\n\n'
                           'Alternatively, you can include two integers to declare a range.\n'
                           'Example: `$purge 3 42`\n'
                           'That command will delete all messages older than 3 days, '
                           'but not older than 42 days.\n\n',
                      brief='Bulk delete messages in current channel')
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
                           'Please use `$help purge` for more information.')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send('Bad argument, please only use integers with this command.\n')
        else:
            print(f'$purge command failed with error:\n\n{error}')

    async def newboard(self, ctx):
        await ctx.send("01010110 01101111 01101110 \
                        00100000 01010011 01100011 01101000 01100101 01100110 01100110 01101100 01100101 01110010")
