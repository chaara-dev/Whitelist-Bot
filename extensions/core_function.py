import storage.constants as constant
from termcolor import colored
from discord.ext import commands

class CoreFunction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reload(self, context):
        pass
        # this will be where the $reload function goes.
        # it will reload the application embed message by grabbing the string from json
        # might still check/edit the message to avoid sending new one
        # 