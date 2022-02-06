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
        self.not_majors = ['Admin', 'WMU_Buster_Clone_Bot', 'Professor']

    @commands.command(help='Select your major as a server role.\nExample: $major Computer Science\n\n' \
                           'To view a list of supported majors, ' \
                           'use the command with 0 arguments\nExample: $major\n\n' \
                           'For some majors you may also use their abbreviation code\nExample: $major AAAS',
                      brief='Select your major as a server role.')
    async def major(self, ctx, *major):
        guild = discord.utils.get(self.bot.guilds, name=GUILD)
        roles = await guild.fetch_roles()
        major = sub(r"'", '', ' '.join(major).lower())
        if major == 'help':
            await ctx.send(self.major.help)
            return
        if major.upper() in major_abbrev:
            major = major_abbrev[major.upper()].lower()
        selected_role = [i for i in roles if i.name.lower() == major]
        if len(selected_role) == 0:
            if major:
                await ctx.send(f'Invald major! Please be sure to type your major exactly as it appears.')
            await ctx.send(content=f'Supported majors include:\n', file=discord.File('./message.txt', filename='Majors.txt'))
            return
        if selected_role[0].name in self.not_majors:
            await ctx.send('Sorry, that role is unavailable for assigment. Please type a valid major.')
            return
        await ctx.send(f'Success! You are now a member of {selected_role[0].name}!')
        await ctx.author.add_roles(selected_role[0])

    async def validate_class(self, ctx, class_name):
        match = search(r'\A\D+', class_name)
        if match is None:
            await ctx.send(f'Unrecognized course name: {class_name}\n' \
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

    @commands.command(help='Join the text channel for a specified class.\nExample: $join CS1120\n\n' \
                           'You may also type several classes at once in a comma-separated list.\n' \
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

    @commands.command(help='Leave the text channel for a specified class.\nExample: $leave CS1120\n\n' \
                           'You may also type several classes at once in a comma-separated list.\n' \
                           'Example: $leave cs1120, math 2240, phys-2130',
                      brief='Leave the text channel for a specified class.')
    async def leave(self, ctx, *, arg):
        arg = arg.strip().lower()
        if arg == 'help':
            await ctx.send(self.leave.help)
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
