from discord.ext import commands, tasks
from dotenv import load_dotenv
from re import search
import discord
import os
import scripts as s

load_dotenv
GUILD = os.getenv('DISCORD_GUILD')


class Classes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.not_majors = ['Admin', 'WMU_Buster_Clone_Bot', 'Cool-Teacher']

    @commands.command(help='Select your major as a server role.\nExample: $major Computer Science\n\n' \
                           'To view a list of supported majors, ' \
                           'use the command with 0 arguments\nExample: $major',
                      brief='Select your major as a server role.')
    async def major(self, ctx, *major):
        guild = discord.utils.get(self.bot.guilds, name=GUILD)
        roles = await guild.fetch_roles()
        major = ' '.join(major).lower()
        selected_role = [i for i in roles if i.name.lower() == major]
        if len(selected_role) == 0:
            if major:
                await ctx.send(f'Invald major! Please be sure to type your major exactly as it appears.')
            await ctx.send(content=f'Supported majors include:\n', file=discord.File(r'./message.txt', filename='Majors.txt'))
            return
        if selected_role[0].name in self.not_majors:
            await ctx.send('Sorry, that role is unavailable for assigment. Please type a valid major.')
            return
        await ctx.send(f'Success! You are now a member of {selected_role[0].name}!')
        await ctx.author.add_roles(selected_role[0])


    async def validate_class(self, ctx, class_name, class_number):
        if class_number:
            department = class_name.lower()
        else:
            match = search(r'\A\D+', class_name)
            if match is None:
                await ctx.send('Invalid class name, please include department prefix')
                return
            else:
                department = match.group().lower()
                class_number = class_name[len(department):]
        try:
            class_int = int(class_number)
            if class_int < 1000 or class_int > 8000:
                await ctx.send(f'Invalid class number: {class_number}')
                return
        except ValueError:
            await ctx.send(f'Invalid class number: {class_number}')
            return
        dep_length = len(department)
        if dep_length > 4 or dep_length < 2:
            await ctx.send('Invalid department prefix')
            return
        return department, class_number

    @commands.command(help='Join the text channel for a specified class.\nExample: $join CS1120',
                      brief='Join the text channel for a specified class.')
    async def join(self, ctx, class_name, class_number=None):
        guild = discord.utils.get(self.bot.guilds, name=GUILD)
        class_info = await self.validate_class(ctx, class_name, class_number)
        if class_info is None:
            return
        department, class_number = class_info
        category = [i for i in guild.categories if i.name == department]
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        if len(category) == 0:
            print(f'Creating category {department}')
            category = await guild.create_category(department, overwrites=overwrites)
        else:
            category = category[0]
        class_name = department + class_number
        channel = [i for i in category.text_channels if i.name == class_name]
        if len(channel) > 0:
            print(f'Adding user to channel {class_name}')
            await channel[0].set_permissions(ctx.author, read_messages=True)
            return
        print(f'Creating channel {class_name}')
        channel = await guild.create_text_channel(class_name, overwrites=overwrites, category=category)
        await channel.set_permissions(ctx.author, read_messages=True)

    @join.error
    async def join_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('You must include a class with this command.\n'
                           'Example: $join CS1120\n\n'
                           'Please use *$help join* for more information.')
        else:
            print(f'$join command failed with error:\n\n{error}')

    @commands.command(help='Leave the text channel for a specified class.\nExample: $leave CS1120',
                      brief='Leave the text channel for a specified class.')
    async def leave(self, ctx, class_name, class_number=None):
        guild = discord.utils.get(self.bot.guilds, name=GUILD)
        class_info = await self.validate_class(ctx, class_name, class_number)
        if class_info is None:
            return
        department, class_number = class_info
        category = [i for i in guild.categories if i.name == department]
        if len(category) > 0:
            channel = [i for i in category[0].text_channels if i.name == class_name]
            if len(channel) > 0:
                await channel[0].set_permissions(ctx.author, read_messages=False)

    @leave.error
    async def leave_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('You must include a class with this command.\n'
                           'Example: $leave CS1120\n\n'
                           'Please use *$help leave* for more information.')
        else:
            print(f'$leave command failed with error:\n\n{error}')
    
    @commands.command(hidden=True)
    @commands.has_permissions(manage_roles=True)
    async def add_roles(self, ctx, filename):
        guild = discord.utils.get(self.bot.guilds, name=GUILD)
        try:
            with open(filename, 'r') as inFile:
                role_objects = await guild.fetch_roles()
                role_names = [i.name for i in role_objects]
                color = discord.Colour.gold()
                count_success = 0
                count_failure = 0
                await ctx.send('Beginning bulk role creation...')
                for line in inFile:
                    name = line.strip()
                    if name not in role_names:
                        print(f'Creating role: {name}')
                        await guild.create_role(name=name, colour=color)
                        count_success += 1
                    else:
                        count_failure += 1
                await ctx.send(f'Operation complete\n' \
                               f'Total Roles Added: {count_success}\n' \
                               f'Redundant Roles Skipped: {count_failure}')
        except FileNotFoundError:
            await ctx.send(f'No file in directory found with name: {filename}')
    
    @add_roles.error
    async def add_roles_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            print(f'$add_roles command failed: User {ctx.author.name} lacks permissions')
        else:
            print(f'$add_roles command failed with error:\n\n{error}')
    
    @commands.command(hidden=True)
    @commands.has_permissions(manage_roles=True)
    async def delete_roles(self, ctx):
        guild = discord.utils.get(self.bot.guilds, name=GUILD)
        role_objects = await guild.fetch_roles()
        for role in role_objects[1:]:
            if role.name not in ['Admin', 'WMU_Bot']:
                print(f'Deleting role {role.name}')
                await role.delete()
    
    @delete_roles.error
    async def delete_roles_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            print(f'$delete_roles command failed: User {ctx.author.name} lacks permissions')
        else:
            print(f'$delete_roles command failed with error:\n\n{error}')


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(help='Returns "pong" if the bot is online.\nExample: $ping',
                      brief='Returns "pong" if the bot is online.')
    async def ping(self, ctx):
        await ctx.send(f'pong (*{round(self.bot.latency * 1000)}ms*)')

    @commands.command(help='Attempts to execute the given code in Python\n'
                           'This command will only accept one-line statements\n'
                           'Example: $execute 6 * 7',
                      brief='Executes given Python code')
    async def execute(self, ctx, *, arg):
        if returned := s.execute(arg):
            if isinstance(returned, str):
                await ctx.send(returned)
            else:
                for line in returned:
                    await ctx.send(line)
                    
    @commands.command(hidden=True)
    async def ready(self, ctx):
        await ctx.send(f'Websocket closed: {self.bot.is_closed()}\n' \
                       f'Internal cache ready: {self.bot.is_ready()}\n' \
                       f'Websocket rate limited: {self.bot.is_ws_ratelimited()}')
    
    @commands.command(hidden=True)
    async def clear(self, ctx):
        self.bot.clear()
        await ctx.send(f'Internal state cleared')
        await self.ready(ctx)


class Random(commands.Cog):
    @commands.command(help='Returns either "heads" or "tails"\nExample: $flip',
                      brief='Returns either "heads" or "tails"')
    async def flip(self, ctx):
        await ctx.send(s.flip())

    @commands.command(help='Returns a randomly chosen number between two given integers\n'
                           'If only one integer is given, then a number between 1 and that integer will be chosen\n'
                           'Example: $number 1 10',
                      brief='Returns a random number')
    async def number(self, ctx, lower: int, upper: int = None):
        await ctx.send(s.rand_num(lower, upper))

    @number.error
    async def number_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('You must include at least 1 integer to serve as an upper bound\n'
                           'Example: $number 42\n\n'
                           'Please use *$help number* for more information.')
        else:
            print(f'$number command failed with error:\n\n{error}')

    @commands.command(help='Returns 1 chosen item from a given list\n'
                           'The list can be of any size, with each item seperated by a comma\n'
                           'Example: $choice me, myself, I',
                      brief='Returns 1 randomly chosen item')
    async def choice(self, ctx, *, arg):
        await ctx.send(s.rand_choice(arg))

    @choice.error
    async def choice_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('You must include a comma-seperated list of items.\n'
                           'Example: $choice Captain Kirk, Captain Picard\n\n'
                           'Please use *$help choice* for more information.')
        else:
            print(f'$choice command failed with error:\n\n{error}')

    @commands.command(help='Rolls any number of n-sided dice in the classic "xDn format\n'
                           'Where *x* is the quantity of dice being rolled, and *n* is the number of sides on the die\n'
                           'Example: $roll 3d20',
                      brief='Rolls dice in the classic "xDn" format')
    async def roll(self, ctx, *, arg):
        rolls = s.roll_dice(arg)
        await ctx.send('\n'.join(rolls))


def setup(bot: commands.Bot):
    bot.add_cog(Classes(bot))
    bot.add_cog(Random())
    bot.add_cog(Utility(bot))
