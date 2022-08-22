# Cog that holds all commands related to WMU classes & majors

from discord.ext import commands
from re import search, sub
import discord

# Local dependencies
from majors import major_abbrev


class Classes(commands.Cog):

    # attr bot - our client
    # attr guild - target Discord server
    # major_list - list of valid majors
    def __init__(self, bot: commands.Bot, guild: discord.Guild):
        self.bot = bot
        self.guild = guild
        self.major_list = []
        with open('message.txt', 'r') as inFile:
            self.major_list = [line.strip().lower() for line in inFile]

    # $major command used to assign users to the role representing their major
    # param major - all user input following command-name
    @commands.command(help='Select your major as a server role.\nExample: $major Computer Science\n\n'
                           'To view a list of supported majors, '
                           'use the command with 0 arguments\nExample: $major\n\n'
                           'For some majors you may also use their abbreviation code\nExample: $major AAAS',
                      brief='Select your major as a server role.')
    async def major(self, ctx, *major):
        # Name of the defualt role everyone will be added to when they run this command
        DEFAULT = 'broncos'
        # Lower and join user input, and remove all apostrophes
        major = sub(r"'", '', ' '.join(major)).lower()
        if major == 'help':
            await ctx.send(self.major.help)
            return
        # Check if user input is in our abbreviations mapping
        if major in major_abbrev:
            major = major_abbrev[major].lower()
        elif major not in self.major_list:
            # Only warn the user about bad input if they included an argument that wasn't "list"
            if major and major != 'list':
                await ctx.send('Invalid major! Please be sure to type your major exactly as it appears.\n')
            await ctx.send(content='Supported majors include:',
                           file=discord.File('./message.txt', filename='Majors.txt'))
            return
        # Find the role requested by the user, as well as the default role
        roles = filter(lambda x: x.name.lower() in (DEFAULT, major), self.guild.roles)
        await ctx.author.add_roles(*roles)
        await ctx.send(f'Success! You are now a member of {major.title()}!')

    # Used by $join and $leave to validate user input for class names
    # param class_name - one instance of user input for class name
    async def validate_class(self, ctx, class_name):
        # Pull non-digit characters from the beginning of the argument
        match = search(r'\A\D+', class_name)
        if match is None:
            await ctx.send(f'Unrecognized course name: {class_name}\nPlease include a valid department prefix.')
            return
        else:
            department = match.group().lower()
            # Pull the rest of the argument that was not matched
            class_number = class_name[match.span()[1]:]

        try:
            class_int = int(class_number)
            # Class numbers at WMU are strictly in this range
            if class_int < 1000 or class_int > 8000:
                print(f'Bad range for class number: {class_int}')
                await ctx.send(f'Invalid class number: {class_name}')
                return
        except ValueError:
            print(f'Caught ValueError on class number: {class_number}')
            await ctx.send(f'Invalid class number: {class_name}')
            return
        dep_length = len(department)
        # Department names are strictly 2, 3, or 4 letters
        if not 1 < dep_length < 5:
            await ctx.send(f'Invalid department prefix: {department}')
            return
        return department, class_number

    # $join command used to add users to text channels for classes
    # param arg - all user input following command-name
    @commands.command(help='Join the text channel for a specified class.\nExample: $join CS1120\n\n'
                           'You may also join several classes at once by using a comma-separated list.\n'
                           'Example: $join cs1120, MATH 2240, phys-2130',
                      brief='Join the text channel for a specified class.')
    async def join(self, ctx, *, arg):
        arg = arg.strip().lower()
        if arg == 'help':
            await ctx.send(self.join.help)
            return
        successful_joins = []
        for element in arg.split(','):
            # Remove all whitespace and hyphens from the argument
            class_name = sub(r'[\s\-]', '', element)
            class_info = await self.validate_class(ctx, class_name)
            if class_info is None:
                await ctx.send(f'Course "{class_name}" not joined.')
                continue
            department, class_number = class_info
            # Get the category for the department of this class
            category = discord.utils.get(self.guild.categories, name=department)
            # Used when creating categories and channels to hide them from users by default
            o_writes = {self.guild.default_role: discord.PermissionOverwrite(read_messages=False)}
            if category is None:
                print(f'Creating category {department}')
                category = await self.guild.create_category(department, overwrites=o_writes)
            class_name = department + class_number
            # Get the channel for this class
            channel = discord.utils.get(category.text_channels, name=class_name)
            if channel:
                print(f'Adding user {ctx.author.name} to channel {class_name}')
                await channel.set_permissions(ctx.author, read_messages=True)
            else:
                print(f'Creating channel {class_name}')
                channel = await self.guild.create_text_channel(class_name, overwrites=o_writes, category=category)
                await channel.set_permissions(ctx.author, read_messages=True)
            successful_joins.append(class_name)
        if successful_joins:
            await ctx.send(f'Successfully joined text channels for: {", ".join(successful_joins)}')

    # Called if $join encounters an unhandled exception
    @join.error
    async def join_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('You must include at least one class with this command.\n'
                           'Example: $join CS1120\n\n'
                           'Please use *$help join* for more information.')
        else:
            print(f'$join command failed with error:\n\n{error}')

    # $leave command used by users to leave class-specific channels
    # param arg - all user input following command-name
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
        successful_leaves = []
        for element in arg.split(','):
            # Remove all whitespace and hyphens from the argument
            class_name = sub(r'[\s\-]', '', element)
            class_info = await self.validate_class(ctx, class_name)
            if class_info is None:
                await ctx.send(f'Course "{class_name}" not left.')
                continue
            department, class_number = class_info
            # Get the category for the department of this class
            category = discord.utils.get(self.guild.categories, name=department)
            if category:
                # Get the channel for this class
                channel = discord.utils.get(category.text_channels, name=class_name)
                if channel:
                    # Hide this channel from the user who sent the command
                    await channel.set_permissions(ctx.author, read_messages=None)
                    successful_leaves.append(class_name)
                else:
                    await ctx.send(f'No channel with name "{class_name}" found, channel not left.')
            else:
                await ctx.send(f'No category with name "{department}" found, channel not left.')
        if successful_leaves:
            await ctx.send(f'Successfully left text channels for: {", ".join(successful_leaves)}')

    # Called if $leave encounters an unhandled exception
    @leave.error
    async def leave_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('You must include at least one class with this command.\n'
                           'Example: $leave CS1120\n\n'
                           'Please use *$help leave* for more information.')
        else:
            print(f'$leave command failed with error:\n\n{error}')

    # Called by $leave if user passes "all" as an argument
    # Removes user from all class-specific channels for which they are a member
    # param ctx - message context forwarded from $leave
    async def leave_all(self, ctx):
        channels_left = []
        # Loop once for each text channel for which the user has permission overwrite(s)
        for channel in filter(lambda x: not x.overwrites_for(ctx.author).is_empty(), self.guild.text_channels):
            # Clear all of the user's overwrites for this channel
            await channel.set_permissions(ctx.author, overwrite=None)
            channels_left.append(channel.name)
        if channels_left:
            await ctx.send(f'Successfully left text channels for: {", ".join(channels_left)}')
        else:
            await ctx.send("No text channels left. Are you sure you're a member of any?")
