import discord
import datetime
import time
import os
import enum
import typing
import json

import storage.constants as constant

from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View
from termcolor import colored
from itertools import cycle


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("$"), intents=intents)
last_application_message = None
bot_status_list = cycle(["for the keyword...", "for new applications.", "#apply-here"])


templateEmbed = discord.Embed(title="Whitelist Application Requirements", description=constant.WHITELIST_APP_MESSAGE, color=0x4654c0)

approvedEmbed = discord.Embed(title="Application Approved", color=0x72c87a)
publicApprovedEmbed = discord.Embed(title="Application Approved ✅", color=0x72c87a)

deniedEmbed = discord.Embed(title="Application Denied", color=0xe74d3c)
publicDeniedEmbed = discord.Embed(title="Application Denied ❌", color=0xe74d3c)

class ApplicationView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    @discord.ui.button(
              label="Apply for Whitelist", 
              style=discord.ButtonStyle.primary, 
              custom_id="whitelist_button"
              )
    
    async def button_callback(self, button, interaction):
            if not button.user.get_role(constant.MEMBER_ROLE_ID):
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


# ----------------------------------------------------------------------------------------------------------------------------
# Slash Commands
class Platforms(enum.Enum):
     Java = 1
     Bedrock = 2
@bot.tree.command(name="approve", description="Approve a whitelist", guild=bot.get_guild(constant.SERVER_ID))
@app_commands.describe(client_type="The applicant's platform")
async def approve(
                interaction, 
                user: discord.Member,
                minecraft_name: str,
                client_type: Platforms,
                message: typing.Optional[str] = "Welcome!"
                ):
        command_channel = interaction.channel
        if interaction.user.get_role(constant.STAFF_ROLE_ID) and command_channel.type == discord.ChannelType.private_thread and command_channel.parent_id == constant.APP_CHANNEL_ID:
            approvedEmbed.clear_fields()
            approvedEmbed.add_field(name="User", value=f"<@{user.id}> ({user.name})", inline=True)
            approvedEmbed.add_field(name="Staff Member", value=f"<@{interaction.user.id}> ({interaction.user.name})", inline=True)
            approvedEmbed.add_field(name="** **", value="** **", inline=False)
            approvedEmbed.add_field(name="Minecraft Name", value=f"** ** ** ** ** ** ** **`{minecraft_name}`", inline=True)
            approvedEmbed.add_field(name="	Client", value=f"** ** ** ** ** ** ** **`{client_type.name}`", inline=True)

            approvedEmbed.add_field(name="Thread", value=f"<#{command_channel.id}>", inline=False)

            approvedEmbed.set_thumbnail(url=f"{user.avatar}")
            approvedEmbed.timestamp = datetime.datetime.now()
            approvedEmbed.set_footer(text=f"User ID: {interaction.user.id}")

            logs = await bot.get_channel(constant.LOGS_CHANNEL_ID)
            await logs.send(embed=approvedEmbed)

            await interaction.response.send_message("Application Approved.", ephemeral=True)
            await command_channel.send(content=f"<@{user.id}> Application approved. {message}") 
            # CHANGE TO BE publicApprovedEmbed !!!

            try:
                await command_channel.edit(
                    name=f"{minecraft_name}'s application ✅",
                    locked=True,
                    invitable=False,
                    auto_archive_duration=60
                    )
            except discord.Forbidden:
                print(colored("Error:", "red"), f"Could not edit thread. Missing Permissions.")
            except discord.HTTPException:
                print(colored("Error:", "red"), f"Failed to edit thread.")
            

            try:
                await user.edit(nick=minecraft_name)
            except discord.errors.Forbidden:
                print(colored("Error:", "red"), "Could not change nickname. Missing Permissions.")
                await logs.send(f"❗ Failed to change **{user.name}**'s nickname. Missing Permissions.")

            try:
                member_role = discord.utils.get(user.guild.roles, id=constant.MEMBER_ROLE_ID)
                await user.add_roles(member_role)
            except discord.Forbidden:
                print(colored("Error:", "red"), f"Error adding {member_role.name} role to {user.name}. Missing Permissions.")
                await logs.send(f"❗ Failed to add **{member_role.name}** role to **{user.name}**. Missing Permissions.")
            except discord.HTTPException:
                print(colored("Error:", "red"), f"Failed to add role to {user.name}.")
            
        elif interaction.user.get_role(constant.STAFF_ROLE_ID) and not command_channel.type == discord.ChannelType.private_thread: 
             await interaction.response.send_message("You're in the wrong channel for that command!", ephemeral=True)
        elif interaction.user.get_role(constant.STAFF_ROLE_ID) and command_channel.type == discord.ChannelType.private_thread and not command_channel.parent_id == constant.APP_CHANNEL_ID:
             await interaction.response.send_message("You're in the wrong channel for that command!", ephemeral=True)

        else:
            await interaction.response.send_message("You don't have permission to use that command.", ephemeral=True)


@bot.tree.command(name="deny", description="Deny a whitelist", guild=bot.get_guild(constant.SERVER_ID))
async def deny(
            interaction, 
            user: discord.Member,
            reason: str
            ):
        command_channel: discord.Thread = interaction.channel
        if interaction.user.get_role(constant.STAFF_ROLE_ID) and command_channel.type == discord.ChannelType.private_thread and command_channel.parent_id == constant.APP_CHANNEL_ID:
            deniedEmbed.add_field(name="User", value=f"<@{user.id}> ({user.name})", inline=True)
            deniedEmbed.add_field(name="Staff Member", value=f"<@{interaction.user.id}> ({interaction.user.name})", inline=True)
            deniedEmbed.add_field(name="Denial Reason", value=f"{reason}", inline=False)

            deniedEmbed.add_field(name="Thread", value=f"<#{command_channel.id}>", inline=False)
        
            deniedEmbed.set_thumbnail(url=f"{user.avatar}")
            deniedEmbed.timestamp = datetime.datetime.now()
            deniedEmbed.set_footer(text=f"User ID: {interaction.user.id}")

            logs = bot.get_channel(constant.LOGS_CHANNEL_ID)
            await logs.send(embed=deniedEmbed)

            await interaction.response.send_message("Application Denied.", ephemeral=True)
            publicDeniedEmbed.description = f"Application denied by <@{interaction.user.id}>\nReason: `{reason}`"


            await command_channel.send(embed=publicDeniedEmbed)



        elif interaction.user.get_role(constant.STAFF_ROLE_ID) and not command_channel.type == discord.ChannelType.private_thread: 
             await interaction.response.send_message("You're in the wrong channel for that command!", ephemeral=True)
        elif interaction.user.get_role(constant.STAFF_ROLE_ID) and command_channel.type == discord.ChannelType.private_thread and not command_channel.parent_id == constant.APP_CHANNEL_ID:
             await interaction.response.send_message("You're in the wrong channel for that command!", ephemeral=True)

        else:
            await interaction.response.send_message("You don't have permission to use that command.", ephemeral=True)
# ----------------------------------------------------------------------------------------------------------------------------


def load_last_message_id():
    try:
        with open('storage/last_message_id.json', 'r') as file:
            data = json.load(file)
            return data.get('last_bot_message_id', None)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
         return None

def save_last_message_id(message_id):
    with open('storage/last_message_id.json', 'w') as file:
        json.dump({'last_bot_message_id': message_id}, file)

@tasks.loop(hours=2)
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
    print("Extension:", colored("text_commands", "yellow"), "loaded.")
    print(f"Logged in as", colored(f"{bot.user.name}", "green") + "!")
    bot.add_view(ApplicationView())

    # Logic for updating embedded Application template message (collapsible)
    application_channel = bot.get_channel(constant.APP_CHANNEL_ID)
    global last_application_message
    view = ApplicationView()
    last_bot_message_id = load_last_message_id()
    if last_bot_message_id is not None:
        try:
            last_application_message = await application_channel.fetch_message(last_bot_message_id)
        except discord.NotFound:
            async for searched_message in application_channel.history(limit=1):
                last_bot_message_id = application_channel.fetch_message(searched_message.id)

    if last_application_message is not None:
        if last_application_message.embeds[0].description == constant.WHITELIST_APP_MESSAGE:
            return 

        await last_application_message.edit(embed=templateEmbed, view=view)
    else:
        try:
            last_application_message = await application_channel.send(embed=templateEmbed, view=view)
            save_last_message_id(last_application_message.id)
        except discord.Forbidden:
            print(colored("Error", "red"), "Failed to send application message embed. Missing Permissions.")

    update_bot_status.start()


load_dotenv()
os.system("color")
bot.run(os.getenv("TOKEN"))