import discord
import os
from storage.system import Constants as constant

from dotenv import load_dotenv
from discord.ext import commands, tasks
from termcolor import colored
from itertools import cycle

# Discord API
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("$"), intents=intents)

@tasks.loop(seconds=5)
async def update_bot_status():
    bot_status_list = cycle([
        "for the keyword...", "for new applications", "#apply-here", "your backs", "the Minecraft movie", "barebonesmp.com"
        ])
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name=next(bot_status_list)
        ), 
        status=discord.Status.idle
        )

@bot.event
async def on_ready():
    await bot.load_extension("extensions.db_logic")

    await bot.load_extension("extensions.text_commands")
    cog_text = bot.get_cog("TextCommands")

    await bot.load_extension("extensions.slash_commands")
    cog_slash = bot.get_cog("SlashCommands")

    await bot.load_extension("extensions.core_function")
    cog_core = bot.get_cog("CoreFunction")

    print(f"Logged in as", colored(f"{bot.user.name}", "green") + "!")

    await cog_core.update_embed_message()
    update_bot_status.start()


load_dotenv()
os.system("color")
bot.run(os.getenv("TOKEN"))