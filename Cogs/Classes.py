from discord.ext import commands
from dotenv import load_dotenv
from re import search, sub
from os import getenv
from majors import major_abbrev
import discord

load_dotenv
GUILD = getenv('DISCORD_GUILD')


class Classes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.major_list = []
        with open('message.txt', 'r') as inFile:
            for line in inFile:
                self.major_list.append(line.strip().lower())

    @commands.command(help='Select your major as a server role.\nExample: $major Computer Science\n\n'
                           'To view a list of supported majors, '
                           'use the command with 0 arguments\nExample: $major\n\n'
                           'For some majors you may also use their abbreviation code\nExample: $major AAAS',
                      brief='Select your major as a server role.')
    async def major(self, ctx, *major):
        major = sub(r"'", '', ' '.join(major).lower())
        if major == 'help':
            await ctx.send(self.major.help)
            return
        if major.upper() in major_abbrev:
            major = major_abbrev[major.upper()].lower()
        elif major not in self.major_list:
            if major and major != 'list':
                await ctx.send('Invalid major! Please be sure to type your major exactly as it appears.\n')
            await ctx.send(content='Supported majors include:',
                           file=discord.File('./message.txt', filename='Majors.txt'))
            return        
        guild = discord.utils.get(self.bot.guilds, name=GUILD)
        roles = await guild.fetch_roles()
        selected_role = [i for i in roles if i.name.lower() == major][0]
        await ctx.author.add_roles(selected_role)
        await ctx.send(f'Success! You are now a member of {selected_role.name}!')

    async def validate_class(self, ctx, class_name):
        match = search(r'\A\D+', class_name)
        if match is None:
            await ctx.send(f'Unrecognized course name: {class_name}\n'
                           f'Please include a valid department prefix.')
            return
        else:
            department = match.group().lower()
            class_number = class_name[len(department):]
        try:
            class_int = int(class_number)
            if class_int < 1000 or class_int > 8000:
                print(f'Bad range for class number: {class_int}')
                await ctx.send(f'Invalid class number: {class_number}')
                return
        except ValueError:
            print(f'Caught ValueError on class number: {class_number}')
            await ctx.send(f'Invalid class number: {class_number}')
            return
        dep_length = len(department)
        if dep_length > 4 or dep_length < 2:
            await ctx.send(f'Invalid department prefix: {department}')
            return
        return department, class_number

    @commands.command(help='Join the text channel for a specified class.\nExample: $join CS1120\n\n'
                           'You may also join several classes at once by using a comma-separated list.\n'
                           'Example: $join cs1120, MATH 2240, phys-2130',
                      brief='Join the text channel for a specified class.')
    async def join(self, ctx, *, arg):
        arg = arg.strip().lower()
        if arg == 'help':
            await ctx.send(self.join.help)
            return
        guild = discord.utils.get(self.bot.guilds, name=GUILD)
        successful_joins = []
        for element in arg.split(','):
            class_name = sub(r'[\s\-]', '', element)
            class_info = await self.validate_class(ctx, class_name)
            if class_info is None:
                await ctx.send(f'Course "{class_name}" not joined.')
                continue
            department, class_number = class_info
            category = [i for i in guild.categories if i.name == department]
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
            }
            if len(category) == 0:
                print(f'Creating category {department}')
                category = await guild.create_category(department, overwrites=overwrites)
            else:
                category = category[0]
            class_name = department + class_number
            channel = [i for i in category.text_channels if i.name == class_name]
            if len(channel) > 0:
                print(f'Adding user {ctx.author.name} to channel {class_name}')
                await channel[0].set_permissions(ctx.author, read_messages=True)
            else:
                print(f'Creating channel {class_name}')
                channel = await guild.create_text_channel(class_name, 
                                                          overwrites=overwrites, 
                                                          category=category)
                await channel.set_permissions(ctx.author, read_messages=True)
            successful_joins.append(class_name)
        if successful_joins:
            await ctx.send(f'Successfully joined text channels for: {", ".join(successful_joins)}')
            

    @join.error
    async def join_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('You must include at least one class with this command.\n'
                           'Example: $join CS1120\n\n'
                           'Please use *$help join* for more information.')
        else:
            print(f'$join command failed with error:\n\n{error}')

    @commands.command(help='Leave the text channel for a specified class.\nExample: $leave CS1120\n\n'
                           'You may also leave several classes at once by using a comma-separated list.\n'
                           'Example: $leave cs1120, math 2240, PHYS-2130\n\n'
                           'To leave all joined text channels use argument "all":\nExample: $leave all',
                      brief='Leave the text channel for a specified class.')
    async def leave(self, ctx, *, arg):
        arg = arg.strip().lower()
        if arg == 'help':
            await ctx.send(self.leave.help)
            return
        if arg == 'all':
            await self.leave_all(ctx)
            return
        guild = discord.utils.get(self.bot.guilds, name=GUILD)
        successful_leaves = []
        for element in arg.split(','):
            class_name = sub(r'[\s\-]', '', element)
            class_info = await self.validate_class(ctx, class_name)
            if class_info is None:
                await ctx.send(f'Course "{class_name}" not left.')
                continue
            department, class_number = class_info
            category = [i for i in guild.categories if i.name == department]
            if len(category) > 0:
                channel = [i for i in category[0].text_channels if i.name == class_name]
                if len(channel) > 0:
                    await channel[0].set_permissions(ctx.author, read_messages=False)
                    successful_leaves.append(class_name)
                else:
                    await ctx.send(f'No channel with name "{class_name}" found, channel not left.')
            else:
                await ctx.send(f'No category with name "{department}" found, channel not left.')
        if successful_leaves:
            await ctx.send(f'Successfully left text channels for: {", ".join(successful_leaves)}')

    @leave.error
    async def leave_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('You must include at least one class with this command.\n'
                           'Example: $leave CS1120\n\n'
                           'Please use *$help leave* for more information.')
        else:
            print(f'$leave command failed with error:\n\n{error}')

    async def leave_all(self, ctx):
        guild = discord.utils.get(self.bot.guilds, name=GUILD)
        channels_left = []
        for channel in guild.text_channels:
            if not channel.overwrites_for(ctx.author).is_empty():
                await channel.set_permissions(ctx.author, overwrite=None)
                channels_left.append(channel.name)
        if channels_left:
            await ctx.send(f'Successfully left text channels for: {", ".join(channels_left)}')
        else:
            await ctx.send("No text channels left. Are you sure you're a member of any?")
    
    @commands.command(hidden=True)
    @commands.has_permissions(manage_roles=True)
    async def add_roles(self, ctx, filename):
        guild = discord.utils.get(self.bot.guilds, name=GUILD)
        try:
            with open(filename, 'r') as inFile:
                role_objects = await guild.fetch_roles()
                role_names = [i.name for i in role_objects]
                color = discord.Colour.orange()
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
                        print('Skipping redundant role: {name}')
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

