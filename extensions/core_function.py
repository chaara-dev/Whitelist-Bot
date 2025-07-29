import discord
import datetime
import json
import sqlite3
from contextlib import closing
from termcolor import colored
from discord.ext import commands, tasks

from storage.system import Constants as constant
import extensions.db_logic as db

class ApplicationView(discord.ui.View):
    def __init__(self, bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.template_embed = discord.Embed(title="Whitelist Application Requirements", description=CoreFunction.load_whitelist_message(self), color=0x4654c0)

    @discord.ui.button(label="Apply for Whitelist", style=discord.ButtonStyle.primary, custom_id="whitelist_button")
    @commands.Cog.listener()
    async def button_callback(self, button, interaction):
        try:
            channel = self.bot.get_channel(constant.APP_CHANNEL_ID)
            if button.user.get_role(constant.MEMBER_ROLE_ID) is None: # or button.user.id == constant.OWNER_ID:
                new_thread = await channel.create_thread(
                    name=f"{button.user.name} application", 
                    message=None, 
                    auto_archive_duration=1440, 
                    type=discord.ChannelType.private_thread, 
                    reason=None,
                    invitable=False
                )

                await button.response.send_message(f"Your application thread was created at <#{new_thread.id}>.",ephemeral=True)
                await new_thread.send(f"\n-# <@&{constant.AVAILABLE_ROLE_ID}>")
                await new_thread.send(embed=self.template_embed)
                
                await new_thread.send(f"**Hi <@{button.user.id}>, your whitelist application has been created. Please fill out the above application in the chat here. A staff member will review shortly.**")


                logEmbed = discord.Embed(title="Application Created",
                                        description=f"**User**\n<@{button.user.id}>",
                                        color=0x4654c0,
                                        timestamp=datetime.datetime.now()
                                        )
                logEmbed.add_field(name="Thread Link", value=f"<#{new_thread.id}>", inline=False)
                logEmbed.set_thumbnail(url=f"{button.user.avatar}")
                logEmbed.set_footer(text=f"User ID: {button.user.id}")
                
                logs = self.bot.get_channel(constant.LOGS_CHANNEL_ID)
                await logs.send(embed=logEmbed)
            
            elif button.user.get_role(constant.MEMBER_ROLE_ID):
                try:
                    await button.response.send_message(f"**You've already applied for the whitelist.**\nIf you have since been removed, please contact a staff member or make a <#{constant.SUPPORT_CHANNEL_ID}> post.", ephemeral=True)
                except Exception as idfk:
                    print(f"error: {idfk}")
                    await button.response.send_message("Something went wrong. Please try again later.\nIf the error persists, contact a staff member.", ephemeral=True)
        except Exception as e:
            print(f"ERROR: {e}")

class AvailableRoleView(discord.ui.View):
    def __init__(self, bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.template_embed = discord.Embed(
            title="Application Ping Role", 
            description="Members with this role will be pinged every time a new application is created.\n\n:3", 
            color=0xe30855)

    @discord.ui.button(label="Get Ping Role", style=discord.ButtonStyle.green, custom_id="get_role_button")
    @commands.Cog.listener()
    async def button_callback_add(self, button, interaction):
        try:
            if button.user.get_role(constant.AVAILABLE_ROLE_ID) is None:
                await button.user.add_roles(button.guild.get_role(constant.AVAILABLE_ROLE_ID))
                await button.response.send_message(f"You've added to the `Available` role.",ephemeral=True)
            else:
                await button.response.defer()
        except Exception as error:
            print(f"ERROR: {error}")
            await button.response.send_message("Something went wrong while adding your `Available` role.")

    @discord.ui.button(label="Remove Ping Role", style=discord.ButtonStyle.red, custom_id="remove_role_buton")
    @commands.Cog.listener()
    async def button_callback_remove(self, button, interaction):
        try:
            if button.user.get_role(constant.AVAILABLE_ROLE_ID) is not None:
                await button.user.remove_roles(button.guild.get_role(constant.AVAILABLE_ROLE_ID))
                await button.response.send_message(f"You've removed from the `Available` role.",ephemeral=True)
            else:
                await button.response.defer()
        except Exception as error:
            print(f"ERROR: {error}")
            await button.response.send_message("Something went wrong while removing your `Available` role.")

class CoreFunction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cog_slash = self.bot.get_cog("SlashCommands")


    # load whitelist message details from txt storage
    def load_whitelist_message(self):
        try:
            with open("storage/whitelist_message.txt", "r") as file:
                return file.read()
        except FileNotFoundError:
            return None

    async def update_embed_message(self, stored_message_id, embed_channel, embed_name, embed_message, view, view_embed):
        last_message = None
        if stored_message_id is not None:
            try:
                last_message = await embed_channel.fetch_message(stored_message_id)
            except discord.NotFound:
                async for searched_message in embed_channel.history(limit=100, oldest_first=True):
                    if searched_message.embeds and searched_message.author == self.bot.user:
                        try:
                            last_message = await embed_channel.fetch_message(searched_message.id)
                        except:
                            last_message = None

        if last_message is not None:
            if last_message.embeds and last_message.embeds[0].description == embed_message:
                return
            else:
                await last_message.edit(embed=view_embed, view=view)
                print(colored(f"Embed message for {embed_channel.name}", "yellow"), "reloaded.")
        else:
            last_message = await embed_channel.send(embed=view_embed, view=view)

        db.store_id(embed_name, last_message.id)


async def setup(bot):
    await bot.add_cog(CoreFunction(bot))
    print("Extension:", colored("core_function.py", "yellow"), "loaded.")
    bot.add_view(ApplicationView(bot))
    bot.add_view(AvailableRoleView(bot))