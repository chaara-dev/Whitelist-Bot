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


bot_status_list = cycle(["for the keyword...", "for new applications.", "#apply-here", "your backs", "the minecrafters"])

@tasks.loop(seconds=30)
async def update_bot_status():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name=next(bot_status_list)
        ), 
        status=discord.Status.idle
        )

@bot.event
async def on_ready():
    await bot.load_extension("extensions.text_commands")
    print("Extension:", colored("text_commands.py", "yellow"), "loaded.")
    cog_text_commands = bot.get_cog("TextCommands")

    await bot.load_extension("extensions.slash_commands")
    print("Extension:", colored("slash_commands.py", "yellow"), "loaded.")
    cog_slash_commands = bot.get_cog("SlashCommands")

    await bot.load_extension("extensions.core_function")
    print("Extension:", colored("core_function.py", "yellow"), "loaded.")
    cog_core_function = bot.get_cog("CoreFunction")

    print(f"Logged in as", colored(f"{bot.user.name}", "green") + "!")

    await cog_core_function.update_embed_message()
    update_bot_status.start()


load_dotenv()
os.system("color")
bot.run(os.getenv("TOKEN"))