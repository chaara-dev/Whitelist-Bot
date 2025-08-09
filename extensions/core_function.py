import discord
import traceback
from datetime import datetime
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
            user_id = button.user.id
            if button.user.get_role(constant.MEMBER_ROLE_ID) is None and not db.has_open_application(user_id):
                new_thread = await channel.create_thread(
                    name=f"{button.user.name}'s application", 
                    message=None, 
                    auto_archive_duration=1440, 
                    type=discord.ChannelType.private_thread, 
                    reason=None,
                    invitable=False
                )
                db.insert_application(thread_id=new_thread.id, user_id=user_id)

                await button.response.send_message(f"Your application thread was created at <#{new_thread.id}>.",ephemeral=True)
                await new_thread.send(f"Hi <@{user_id}>, your whitelist application has been created.", embed=self.template_embed)
                await new_thread.send("# [COPY AND PASTE THE APPLICATION FORM INTO THIS CHANNEL.]\nA staff member will review shortly.")


                logEmbed = discord.Embed(title="Application Created",
                                        description=f"**User**\n<@{user_id}> ({button.user.name})",
                                        color=0x4654c0,
                                        timestamp=datetime.now()
                                        )
                logEmbed.add_field(name="Thread Link", value=f"<#{new_thread.id}>", inline=False)
                logEmbed.set_thumbnail(url=f"{button.user.avatar}")
                logEmbed.set_footer(text=f"User ID: {user_id}")
                
                logs = self.bot.get_channel(constant.LOGS_CHANNEL_ID)
                await logs.send(embed=logEmbed)
            
            elif button.user.get_role(constant.MEMBER_ROLE_ID):
                try:
                    await button.response.send_message(f"**You've already applied for the whitelist.**\nIf you have since been removed, please contact a staff member or make a <#{constant.SUPPORT_CHANNEL_ID}> post.", ephemeral=True)
                except Exception as error:
                    format = "%Y-%m-%d %H:%M:%S%z"
                    print(f'{colored(f"Error: {error}", "red")} at {colored(f"{datetime.now():{format}}", "green")}')
                    traceback.print_exc()
                    await button.response.send_message(f"Something went wrong. Please try again later.\nIf the error persists, contact `@lostbrickplacer`.", ephemeral=True)
            elif db.has_open_application(user_id):
                try:
                    await button.response.send_message(f"**You already have an open application at <#{db.get_open_application_id(user_id)}>**.\nPlease fill that one out or wait to be accepted.", ephemeral=True)
                except Exception as error:
                    format = "%Y-%m-%d %H:%M:%S%z"
                    print(f'{colored(f"Error: {error}", "red")} at {colored(f"{datetime.now():{format}}", "green")}')
                    traceback.print_exc()
                    await button.response.send_message("Something went wrong. Please try again later.\nIf the error persists, contact `@lostbrickplacer`", ephemeral=True)
        except Exception as error:
            print(f"BUTTON CALLBACK FUNCTION ERROR: {error}")
            traceback.print_exc()

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
            traceback.print_exc()
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
            traceback.print_exc()
            await button.response.send_message("Something went wrong while removing your `Available` role.")

class CoreFunction(commands.Cog):
    def __init__(self, bot: discord.BotIntegration):
        self.bot = bot
        self.cog_slash = self.bot.get_cog("SlashCommands")
        self.check_application_status.start()


    def cog_unload(self):
        self.check_application_status.cancel()

    @tasks.loop(minutes=5)
    async def check_application_status(self):
        now = datetime.now()
        open_apps = db.get_all_open_applications()

        for row in open_apps:
            thread_id = row[0]
            applicant_id = row[1]
            created_at = row[3]
            reminded_stage = row[4]
            application_at = row[5]
            if application_at is not None:
                continue
            hours_open = (now - datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S.%f")).total_seconds() / 3600

            if reminded_stage == "none" and hours_open >= 2:
                thread = self.bot.get_channel(thread_id)
                if thread:
                    await thread.send(f"⏰ <@{applicant_id}> Please complete your whitelist application!")
                    db.mark_applicant_reminded(thread_id, "warning")
            elif reminded_stage == "warning" and hours_open >= 4:
                thread = self.bot.get_channel(thread_id)
                if thread:
                    await self.delete_last_bot_message(thread)
                    await thread.send(f"⏰❗ <@{applicant_id}> **Final reminder!** Please complete your application!")
                    db.mark_applicant_reminded(thread_id, "final_warning")
            elif reminded_stage == "final_warning" and hours_open >= 6:
                thread = self.bot.get_channel(thread_id)
                if thread:
                    await self.delete_last_bot_message(thread)
                    embed = discord.Embed(
                        color=0x4a4a4f, 
                        title="🪦 Application Automatically Closed", 
                        description=f"Application was not completed. If you would still like to join, please apply again at <#{constant.APP_CHANNEL_ID}>",
                        timestamp=datetime.now()
                    )
                    await thread.send(content=f"-# <@{applicant_id}>", embed=embed)

                db.mark_applicant_reminded(thread_id, "complete")
                await self.set_application_abandoned(thread_id, applicant_id)

    @check_application_status.before_loop
    async def before_check_application_reminders(self):
        await self.bot.wait_until_ready()


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

    async def set_application_abandoned(self, thread_id, user_id):
        app_thread = await self.bot.fetch_channel(thread_id)
        user = await self.bot.fetch_user(user_id)
        log_channel = self.bot.get_channel(constant.LOGS_CHANNEL_ID)

        abandoned_embed = discord.Embed(title="Application Abandoned", color=0x4a4a4f)
        abandoned_embed.add_field(name="User", value=f"<@{user.id}> ({user.name})", inline=True)
        abandoned_embed.add_field(name="Thread", value=f"<#{app_thread.id}>", inline=False)
        abandoned_embed.set_thumbnail(url=f"{user.avatar}")
        abandoned_embed.set_footer(text=f"User ID: {user.id}")
        abandoned_embed.timestamp = datetime.now()

        db.mark_application(thread_id, "abandoned", None)
        await app_thread.edit(name=f"🗑️ {user.name}'s application", locked=True, invitable=False, auto_archive_duration=60)
        await log_channel.send(embed=abandoned_embed)

    async def delete_last_bot_message(self, channel):
        async for message in channel.history(limit=10):
            if message.author == self.bot.user:
                await message.delete()
                break

    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.author == self.bot.user or
            message.channel.type != discord.ChannelType.private_thread or
            message.channel.parent_id != constant.APP_CHANNEL_ID or
            message.author.get_role(constant.STAFF_ROLE_ID) is not None
        ):
            return
        app_msg = message.content.lower()

        if (("andesite" in app_msg or "keyword" in app_msg) and
            ("java" in app_msg or "bedrock" in app_msg) and 
            ("yes" in app_msg or 
            "yup" in app_msg or 
            "yep" in app_msg or 
            "yeah" in app_msg or 
            "agree" in app_msg or 
            "indeed" in app_msg or 
            "ofc" in app_msg or 
            "course" in app_msg)
        ):
            await message.channel.send(f"\n-# New application created. <@&{constant.AVAILABLE_ROLE_ID}>")
            db.mark_applicant_reminded(message.channel.id, "complete")
            db.update_created_timestamp(thread_id=message.channel.id, user_id=message.author.id)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        open_apps = db.get_open_application_members(member.id)

        for row in open_apps:
            applicant_id = row[1]
            thread_id = row[0]

            if member.id == applicant_id:
                await self.set_application_abandoned(thread_id, applicant_id)

    async def dm_member_approve(self, member: discord.Member, channel: discord.Thread, minecraft_name: str):
        await member.send(f"## Your whitelist application to BareBonesMP has been approved!\nWelcome to the community!\n\n**Minecraft Name:** `{minecraft_name}`\n**Your Application:** <#{channel.id}>\n**Java IP:** `play.barebonesmp.com`\n**Bedrock IP:** `play.barebonesmp.com:19132`\n-# If you have any issues joining or any questions you can ask in <#{constant.SUPPORT_CHANNEL_ID}> or @ any of the staff members.")

    async def dm_member_deny(self, member: discord.Member, reason: str, channel: discord.Thread):
        await member.send(f"## Your whitelist application to BareBonesMP has been denied.\n**Denial Reason:** `{reason}`\n**Your Application:** <#{channel.id}>\n*Please review the rules and reasoning before applying again. Spam applying will result in a ban.*")


async def setup(bot):
    await bot.add_cog(CoreFunction(bot))
    print("Extension:", colored("core_function.py", "yellow"), "loaded.")
    bot.add_view(ApplicationView(bot))
    bot.add_view(AvailableRoleView(bot))
