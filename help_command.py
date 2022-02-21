# Custom help command for BUSTER
# Inititialized by ./bot.py and used to override the defualt help command

from discord.ext import commands


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.qualified_name = 'Help'

    # Called when a user gives the $help command
    # param mapping - a mapping of cogs to commands
    async def send_bot_help(self, mapping):
        cog_list = []
        for cog, commands in mapping.items():
            try:
                cog_name = cog.qualified_name
            # Catch and skip the $help command itself, who's cog does not have a qualified_name
            except AttributeError:
                continue
            command_list = '\n'.join([f'    *{i.name}* - {i.brief}' for i in commands if not i.hidden])
            # Only include this cog if it has at least one public command
            if command_list:
                cog_list.append(f'**{cog_name}**:\n{command_list}')

        await self.get_destination().send('\n'.join(cog_list))

    # Called when user gives the $help {cog_name} command
    # param cog - the cog that was requested for help
    async def send_cog_help(self, cog):
        command_list = '\n'.join([f'    *{i.name}* - {i.brief}' for i in cog.get_commands() if not i.hidden])
        await self.get_destination().send(f'**{cog.qualified_name}**:\n{command_list}')

    # Called when user gives the $help {command_name} command
    # param command - the command that was requested for help
    async def send_command_help(self, command):
        if command.hidden:
            return
        await self.get_destination().send(f'**{command.name}**:\n{command.help}')
