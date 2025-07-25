import discord
import datetime
import time
import os
import json

import storage.constants as constant

from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.ui import Button, View
from termcolor import colored
from itertools import cycle

# Discord API
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("$"), intents=intents)

# Variables
bot_status_list = cycle(["for the keyword...", "for new applications.", "#apply-here", "your backs", "the minecrafters"])
templateEmbed = discord.Embed(title="Whitelist Application Requirements", description=constant.WHITELIST_APP_MESSAGE, color=0x4654c0)

class ApplicationView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Apply for Whitelist", style=discord.ButtonStyle.primary, custom_id="whitelist_button")
    async def button_callback(self, button, interaction):
            if not button.user.get_role(constant.MEMBER_ROLE_ID) or button.user.id == constant.OWNER_ID:
                channel = bot.get_channel(constant.APP_CHANNEL_ID)
                new_thread = await channel.create_thread(
                    name=f"{button.user.name} application", 
                    message=None, 
                    auto_archive_duration=1440, 
                    type=discord.ChannelType.private_thread, 
                    reason=None,
                    invitable=False
                )

                time.sleep(1.5)
                await button.response.send_message(f"Your application thread was created at <#{new_thread.id}>.",ephemeral=True)
                await new_thread.send(embed=templateEmbed)
                
                await new_thread.send(f"**Hi <@{button.user.id}>, your whitelist application has been created. Please fill out the above application in the chat here. A staff member will review shortly.**")


                logEmbed = discord.Embed(title="Application Created",
                                        description=f"**User**\n<@{button.user.id}>",
                                        color=0x4654c0,
                                        timestamp=datetime.datetime.now()
                                        )
                logEmbed.add_field(
                    name="Thread Link",
                    value=f"<#{new_thread.id}>",
                    inline=False
                )
                logEmbed.set_thumbnail(url=f"{button.user.avatar}")
                logEmbed.set_footer(text=f"User ID: {button.user.id}")
                
                logs = bot.get_channel(constant.LOGS_CHANNEL_ID)
                await logs.send(embed=logEmbed)
            
            elif button.user.get_role(constant.MEMBER_ROLE_ID):
                try:
                    await button.response.send_message(f"You've already applied for the whitelist. If you have since been removed, please contact a\n Staff member.", ephemeral=True)
                except:
                    await button.response.send_message("Something went wrong. Please try again later.\nIf the error persists, contact a Staff member.", ephemeral=True)
                    print(colored("Error:", "red"), "Something went wrong sending [Already Applied to Whitelist] message.")

def load_stored_message():
    try:
        with open('storage/message_id.json', 'r') as file:
            data = json.load(file)
            return data.get('message_id', None)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def store_message(message_id):
    with open('storage/message_id.json', 'w') as file:
        json.dump({'message_id': message_id}, file)

@tasks.loop(seconds=30)
async def update_bot_status():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name=next(bot_status_list)
        ), 
        status=discord.Status.idle
        )

async def update_embed_message():
    last_embed_message = None
    application_channel = bot.get_channel(constant.APP_CHANNEL_ID)
    view = ApplicationView()
    stored_message = load_stored_message()

    if stored_message is not None:
        try:
            last_embed_message = await application_channel.fetch_message(stored_message)
        except discord.NotFound:
            async for searched_message in application_channel.history(limit=5):
                if searched_message.embeds and searched_message.author == bot.user:
                    try:
                        last_embed_message = await application_channel.fetch_message(searched_message.id)
                    except:
                        last_embed_message = None

    if last_embed_message is not None:
        if last_embed_message.embeds and last_embed_message.embeds[0].description == constant.WHITELIST_APP_MESSAGE:
            return 
        else:
            await last_embed_message.edit(embed=templateEmbed, view=view)
    else:
        try:
            last_embed_message = await application_channel.send(embed=templateEmbed, view=view)
        except discord.Forbidden:
            print(colored("Error", "red"), "Failed to send application message embed. Missing Permissions.")

    store_message(last_embed_message.id)

@bot.event
async def on_ready():
    await bot.load_extension("extensions.text_commands")
    print("Extension:", colored("text_commands.py", "yellow"), "loaded.")

    await bot.load_extension("extensions.slash_commands")
    print("Extension:", colored("slash_commands.py", "yellow"), "loaded.")


    print(f"Logged in as", colored(f"{bot.user.name}", "green") + "!")
    bot.add_view(ApplicationView())

    await update_embed_message()
    update_bot_status.start()


load_dotenv()
os.system("color")
bot.run(os.getenv("TOKEN"))