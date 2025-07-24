import storage.constants as constant
from discord.ext import commands


class TextCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def purge(self, context, amount: int):
        if context.author.id == constant.OWNER_ID:
            deleted = await context.channel.purge(limit=amount + 1)
            await context.send(f"Deleted {len(deleted) - 1} message(s).", delete_after=0.25)
        else:
            await context.reply(content="You can't use that command!", delete_after=2)

    @commands.command()
    async def sync(self, context):
            if context.author.id == constant.OWNER_ID:
                await self.bot.tree.sync()
                print("Syncing...")
                await context.send("Command tree synced.")
                print("Synced.")
                await context.channel.purge(limit=2)
                
            else:
                await context.send(content="You must be the owner to use this command.", delete_after=2)


async def setup(bot):
    await bot.add_cog(TextCommands(bot))