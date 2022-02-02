from discord.ext import commands


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        cog_list = []
        for cog in mapping:
            try:
                name = cog.qualified_name
            except AttributeError:
                name = 'No Category'
            command_list = []
            for command in mapping[cog]:
                if not command.hidden:
                    command_list.append(f'    *{command.name}* - {command.brief}')
            command_names = '\n'.join(command_list)
            if command_names:
                cog_list.append(f'**{name}**:\n{command_names}')
        help_string = '\n'.join(cog_list)
        await self.get_destination().send(help_string)

    async def send_cog_help(self, cog):
        command_list = []
        for command in cog.get_commands():
            command_list.append(f'    *{command.name}* - {command.brief}')
        command_names = '\n'.join(command_list)
        await self.get_destination().send(f'**{cog.qualified_name}**:\n{command_names}')

    async def send_command_help(self, command):
        await self.get_destination().send(f'**{command.name}**:\n{command.help}')
