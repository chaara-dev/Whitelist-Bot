import discord
from termcolor import colored
from discord.ext import commands

from storage.system import Constants as constant


class TextCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reload(self, context):
        cog_text_commands = self.bot.get_cog("TextCommands")
        cog_slash_commands = self.bot.get_cog("SlashCommands")
        cog_core_function = self.bot.get_cog("CoreFunction")

        if context.author.id == constant.OWNER_ID:
            await self.bot.reload_extension("extensions.text_commands")
            print("Extension:", colored("text_commands.py", "yellow"), "reloaded.")
            await self.bot.reload_extension("extensions.slash_commands")
            print("Extension:", colored("slash_commands.py", "yellow"), "reloaded.")
            await self.bot.reload_extension("extensions.core_function")
            print("Extension:", colored("core_function.py", "yellow"), "reloaded.")

            await cog_core_function.update_embed_message()

            try:
                await context.message.add_reaction("✅")
                await context.message.delete(delay=1)
            except discord.NotFound:
                pass


    @commands.command()
    async def purge(self, context, amount: int):
        if context.author.id == constant.OWNER_ID:
            deleted = await context.channel.purge(limit=amount + 1)
            await context.send(f"Deleted {len(deleted) - 1} message(s).", delete_after=0.25)
        else:
            await context.reply(content="You can't use that command!", delete_after=2)
    @purge.error
    async def purge_error(self, context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await context.send("Please specify an amount of messages to delete.", delete_after=1)


    @commands.command()
    async def sync(self, context):
            if context.author.id == constant.OWNER_ID:
                await self.bot.tree.sync()
                print("Command tree synced.")
                await context.message.add_reaction("✅")
                await context.message.delete(delay=1)


async def setup(bot):
    await bot.add_cog(TextCommands(bot))