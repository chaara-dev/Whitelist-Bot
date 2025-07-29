import enum
import discord
import datetime
import typing
from termcolor import colored

from storage.system import Constants as constant
from storage.system import CustomErrors as c_error
import extensions.db_logic as db
import extensions.core_function as ext_core

from discord import app_commands
from discord.ext import commands

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    class Platforms(enum.Enum):
        Java = 1
        Bedrock = 2


    # check if command user is Staff
    def user_is_staff():
            async def predicate(interaction: discord.Interaction) -> bool:
                staff_role = interaction.user.get_role(constant.STAFF_ROLE_ID)
                if staff_role is None:
                    raise c_error.UserIsNotStaff("You don't have permission to use that command.")
                return True
            return app_commands.check(predicate)
    # check if command user is Owner
    def user_is_owner():
        async def predicate(interaction: discord.Interaction) -> bool:
            if interaction.user.id != constant.OWNER_ID:
                raise c_error.UserIsNotOwner("You don't have permission to use that command.")
            return True
        return app_commands.check(predicate)
    # check if command used in valid channel
    def used_in_valid_channel():
        def predicate(interaction: discord.Interaction) -> bool:
            valid_channel = bool(interaction.channel.type == discord.ChannelType.private_thread and interaction.channel.parent_id == constant.APP_CHANNEL_ID)
            if valid_channel is False:
                raise c_error.InvalidCommandChannel("You're in the wrong channel for that command!")
            return True
        return app_commands.check(predicate)
    # change nickname and add member role
    async def update_user(self, user, minecraft_name, role):
        nick_success = False
        role_success = False
        
        try: 
            await user.edit(nick=minecraft_name)
            nick_success = True
        except: 
            nick_success = False

        if user.get_role(constant.MEMBER_ROLE_ID): 
            role_success = True
        else: 
            try: 
                await user.add_roles(role)
                role_success = True
            except: 
                role_success = False

        if nick_success and role_success: return "✅Application Approved."
        elif nick_success and not role_success: return "✅Application Approved.\n`❗Failed to add member role.`"
        elif not nick_success and role_success: return "✅Application Approved.\n`❗Failed to change nickname.`"
        else: return "✅Application Approved.\n`❗Failed to change nickname.\n❗Failed to add member role.`"
    # run commands to add member to whitelist
    async def run_whitelist_command(self, minecraft_name, client_type):
        if client_type == self.Platforms.Java: return f"!c whitelist add {minecraft_name}"
        elif client_type == self.Platforms.Bedrock: return f"!c fwhitelist add {minecraft_name}"
        else: return "Something went wrong."
    # populate discord embed with details about approved user
    async def fill_embed(self, interaction, embed_type, user, minecraft_name, client_type, reason):
        if embed_type == True: embed = discord.Embed(color=0x72c87a)
        elif embed_type == False: embed = discord.Embed(color=0xe74d3c)
        else: embed = discord.Embed(title="Error", description="Something went wrong.", color=0xffffff)
        embed.clear_fields()
        
        embed.add_field(name="User", value=f"<@{user.id}> ({user.name})", inline=True)
        embed.add_field(name="Staff Member", value=f"<@{interaction.user.id}> ({interaction.user.name})", inline=True)
        if minecraft_name is not None and client_type is not None:
            embed.add_field(name="** **", value="** **", inline=False)
            embed.add_field(name="Minecraft Name", value=f"** ** ** ** ** ** ** **`{minecraft_name}`", inline=True)
            embed.add_field(name="	Client", value=f"** ** ** ** ** ** ** **`{client_type.name}`", inline=True)
        if reason is not None:
            embed.add_field(name="Denial Reason", value=f"{reason}", inline=False)
        embed.set_thumbnail(url=f"{user.avatar}")
        embed.set_footer(text=f"User ID: {interaction.user.id}")
        embed.timestamp = datetime.datetime.now()

        return embed
    # load whitelist message and return a code block displayable string
    def get_format_whitelist_message(self):
        formatted_message = ""
        try:
            with open("storage/whitelist_message.txt", "r") as file:
                for line in file.readlines():
                    if "```" in line:
                        formatted_message += "+++\n"
                    else:
                        formatted_message += line
                return formatted_message
        except FileNotFoundError:
            return None
    # use input message and set whitelist message with proper code block formatting
    def set_format_whitelist_message(self, message : str):
        formatted_message = ""
        try:
            with open("storage/whitelist_message.txt", "w") as file:
                for line in message.splitlines(keepends=True):
                    if "+++" in line:
                        formatted_message += "```\n"
                    else:
                        formatted_message += line
                file.write(formatted_message)
        except FileNotFoundError:
            return None
    # loads a default whitelist message from seperate file
    def get_default_whitelist_message(self):
        try: 
            with open("storage/whitelist_message_default.txt") as file:
                return file.read()
        except FileNotFoundError:
            return None

    # approve a whitelist application inside private thread
    @app_commands.command(name="approve", description="Approve a whitelist application.")
    @app_commands.describe(client_type="The applicant's platform.")
    @user_is_staff()
    @used_in_valid_channel()
    async def approve(self, interaction, user: discord.Member, minecraft_name: str, client_type: Platforms, message: typing.Optional[str] = "Welcome!"):
                command_channel = interaction.channel
                log_channel = self.bot.get_channel(constant.LOGS_CHANNEL_ID)
                chat_channel = self.bot.get_channel(constant.CHAT_CHANNEL_ID)
                member_role = interaction.guild.get_role(constant.MEMBER_ROLE_ID)

                approved_embed = await self.fill_embed(interaction, True, user, minecraft_name, client_type, None)
                approved_embed.title = "Application Approved"
                approved_embed.add_field(name="Thread", value=f"<#{command_channel.id}>", inline=False)
                
                public_approved_embed = discord.Embed(title="✅ Application Approved", color=0x72c87a)
                public_approved_embed.description = f"Client Type: **{client_type.name}**\nMinecraft Name: **{minecraft_name}**\n\n{message}"
                public_approved_embed.timestamp = datetime.datetime.now()

                await command_channel.send(embed=public_approved_embed)
                await log_channel.send(embed=approved_embed)
                await command_channel.edit(name=f"✅ {minecraft_name}'s application", locked=True, invitable=False, auto_archive_duration=60)

                await chat_channel.send(await self.run_whitelist_command(minecraft_name, client_type))
                user_update_status = await self.update_user(user, minecraft_name, member_role)
                await interaction.response.send_message(f"{user_update_status}", ephemeral=True)


    # deny a whitelist application inside private thread
    @app_commands.command(name="deny", description="Deny a whitelist application.")
    @user_is_staff()
    @used_in_valid_channel()
    async def deny(self, interaction, user: discord.Member, reason: str ):
            command_channel = interaction.channel
            log_channel = self.bot.get_channel(constant.LOGS_CHANNEL_ID)

            deniedEmbed = await self.fill_embed(interaction, False, user, None, None, reason)
            deniedEmbed.title = "Application Denied"
            deniedEmbed.add_field(name="Thread", value=f"<#{command_channel.id}>", inline=False)

            publicDeniedEmbed = discord.Embed(title="❌ Application Denied", color=0xe74d3c)
            publicDeniedEmbed.description = f"Application denied by <@{interaction.user.id}>\nReason: `{reason}`"
            publicDeniedEmbed.timestamp = datetime.datetime.now()

            await interaction.response.send_message("Application Denied.", ephemeral=True)
            await command_channel.send(embed=publicDeniedEmbed)
            await log_channel.send(embed=deniedEmbed)


    # approve a whitelist application without being in application thread
    @app_commands.command(name="quick-approve", description="Simple /approve without channel requirements.")
    @app_commands.describe(client_type="The applicant's platform.")
    @user_is_staff()
    async def quickapprove(self, interaction, user: discord.Member, minecraft_name: str, client_type: Platforms):
            command_channel = interaction.channel
            log_channel = self.bot.get_channel(constant.LOGS_CHANNEL_ID)
            chat_channel = self.bot.get_channel(constant.CHAT_CHANNEL_ID)
            member_role = interaction.guild.get_role(constant.MEMBER_ROLE_ID)

            approvedEmbed = await self.fill_embed(interaction, True, user, minecraft_name, client_type, None)
            approvedEmbed.title = "Application Quick Approved"

            user_update_status = await self.update_user(user, minecraft_name, member_role)
            await interaction.response.send_message(f"{user_update_status}", ephemeral=True)
            
            await chat_channel.send(await self.run_whitelist_command(minecraft_name, client_type))
            await log_channel.send(embed=approvedEmbed)
            await command_channel.send(f"**{minecraft_name}** has been added to the whitelist.")


    # update whitelist message in #apply-here embed
    @app_commands.command(name="update-whitelist-message", description="Update whitelist embed message.")
    @user_is_owner()
    async def update_whitelist_message(self, interaction : discord.Interaction):
        def check_owner_message(m):
            return interaction.user == m.author

        await interaction.response.send_message(
            f"## Current <#{constant.APP_CHANNEL_ID}> Whitelist Message:\n```{self.get_format_whitelist_message()}```\n-# - **Copy** this text to edit. **Paste** it back into the channel to update.\n-# - Cancel this command by typing `cancel` or `quit`, or by not sending a message within the next 60 seconds.\n-# - Reset message to default by typing `default` or `reset`.", 
            ephemeral=True)
        try:
            edited_message = await self.bot.wait_for("message", timeout=60, check=check_owner_message)
        except TimeoutError:
            await interaction.edit_original_response(content="No Message recieved within 60 seconds. Command cancelled.")
            return
        check_message = edited_message.content.lower().strip()
        cog_core = self.bot.get_cog("CoreFunction")

        if check_message == "cancel" or check_message == "quit" or check_message[0] == "$":
            await edited_message.delete()
            await interaction.edit_original_response(content="Command cancelled.")

        elif check_message == "default" or check_message == "reset":
            self.set_format_whitelist_message(self.get_default_whitelist_message())
            await edited_message.delete()
            await self.bot.get_cog("CoreFunction").update_embed_message(
                stored_message_id=db.load_stored_id("application"),
                embed_channel=self.bot.get_channel(constant.APP_CHANNEL_ID),
                embed_message=cog_core.load_whitelist_message(),
                view=ext_core.ApplicationView(self.bot)
            )
            await interaction.edit_original_response(content=f"<#{constant.APP_CHANNEL_ID}> whitelist embed message reset.")

        else:
            self.set_format_whitelist_message(edited_message.content)
            await edited_message.delete()
            await self.bot.get_cog("CoreFunction").update_embed_message(
                stored_message_id=db.load_stored_id("application"),
                embed_channel=self.bot.get_channel(constant.APP_CHANNEL_ID),
                embed_message=cog_core.load_whitelist_message(),
                view=ext_core.ApplicationView(self.bot)
            )
            await interaction.edit_original_response(content=f"<#{constant.APP_CHANNEL_ID}> whitelist embed message updated.")


    # global SlashCommands Cog error handler
    async def cog_app_command_error(self, interaction, error):
        try:
            if isinstance(error, c_error.InvalidCommandChannel):
                await interaction.response.send_message(error, ephemeral=True)
            elif isinstance(error, c_error.UserIsNotStaff):
                await interaction.response.send_message(error, ephemeral=True)
            elif isinstance(error, c_error.UserIsNotOwner):
                await interaction.response.send_message(error, ephemeral=True)
            elif isinstance(error, TimeoutError):
                await interaction.response.send_message("Timed out while waiting for new whitelist message.", ephemeral=True)
            else:
                print(error)
                await interaction.response.send_message(f"Error: {error}", ephemeral=True)
        except:
            if isinstance(error, c_error.InvalidCommandChannel):
                await interaction.followup.send(error, ephemeral=True)
            elif isinstance(error, c_error.UserIsNotStaff):
                await interaction.followup.send(error, ephemeral=True)
            elif isinstance(error, c_error.UserIsNotOwner):
                await interaction.followup.send(error, ephemeral=True)
            elif isinstance(error, TimeoutError):
                await interaction.followup.send(error, ephemeral=True)
            else:
                print(error)
                await interaction.followup.send(f"Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
    print("Extension:", colored("slash_commands.py", "yellow"), "loaded.")