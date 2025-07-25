import enum
import discord
import datetime
import typing
from termcolor import colored

import storage.constants as constant

from discord import app_commands
from discord.ext import commands

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    class Platforms(enum.Enum):
        Java = 1
        Bedrock = 2


    async def name_and_role(self, user, minecraft_name, role):
        nick_success = None 
        role_success = None
        try:
            await user.edit(nick=minecraft_name)
            nick_success = True
        except:
            nick_success = False

        if user.get_role(constant.MEMBER_ROLE_ID):
            role_success = True
        else:
            # try:
                await user.add_roles(role)
                role_success = True
            # except:
                role_success = False


        if nick_success and role_success:
            return "✅Application Approved."
        elif nick_success and not role_success:
            return "✅Application Approved.\n`❗Failed to add member role.`"
        elif not nick_success and role_success:
            return "✅Application Approved.\n`❗Failed to change nickname.`"
        else:
            return "✅Application Approved.\n`❗Failed to change nickname.\n❗Failed to add member role.`"


    async def add_to_whitelist(self, minecraft_name, client_type):

        if client_type == self.Platforms.Java:
            return f"!c whitelist add {minecraft_name}"
        elif client_type == self.Platforms.Bedrock:
            return f"!c fwhitelist add {minecraft_name}"
        else:
            return "Something went wrong."


    @app_commands.command(name="approve", description="Approve a whitelist.")
    @app_commands.describe(client_type="The applicant's platform.")
    async def approve(
                    self,
                    interaction, 
                    user: discord.Member,
                    minecraft_name: str,
                    client_type: Platforms,
                    message: typing.Optional[str] = "Welcome!"
                    ):

            command_channel = interaction.channel
            log_channel = self.bot.get_channel(constant.LOGS_CHANNEL_ID)
            chat_channel = self.bot.get_channel(constant.CHAT_CHANNEL_ID)
            member_role = interaction.guild.get_role(constant.MEMBER_ROLE_ID)
            approvedEmbed = discord.Embed(title="Application Approved", color=0x72c87a)
            publicApprovedEmbed = discord.Embed(title="✅ Application Approved", color=0x72c87a)

            # if user IS staff AND command IS used in private thread AND private thread parent IS #apply-here:
            if interaction.user.get_role(constant.STAFF_ROLE_ID) and command_channel.type == discord.ChannelType.private_thread and command_channel.parent_id == constant.APP_CHANNEL_ID:
                approvedEmbed.clear_fields()
                approvedEmbed.add_field(name="User", value=f"<@{user.id}> ({user.name})", inline=True)
                approvedEmbed.add_field(name="Staff Member", value=f"<@{interaction.user.id}> ({interaction.user.name})", inline=True)
                approvedEmbed.add_field(name="** **", value="** **", inline=False)
                approvedEmbed.add_field(name="Minecraft Name", value=f"** ** ** ** ** ** ** **`{minecraft_name}`", inline=True)
                approvedEmbed.add_field(name="	Client", value=f"** ** ** ** ** ** ** **`{client_type.name}`", inline=True)
                approvedEmbed.add_field(name="Thread", value=f"<#{command_channel.id}>", inline=False)
                approvedEmbed.set_thumbnail(url=f"{user.avatar}")
                approvedEmbed.set_footer(text=f"User ID: {interaction.user.id}")
                approvedEmbed.timestamp = datetime.datetime.now()

                publicApprovedEmbed.description = f"Client Type: **{client_type.name}**\nMinecraft Name: **{minecraft_name}**\n\n{message}"
                publicApprovedEmbed.timestamp = datetime.datetime.now()

                await command_channel.send(embed=publicApprovedEmbed)
                await log_channel.send(embed=approvedEmbed)


                try:
                    await command_channel.edit(name=f"{minecraft_name}'s application ✅", locked=True, invitable=False, auto_archive_duration=60)
                except:
                    log_channel.send(f"Something went wrong editing <#{command_channel.id}>")
                


                await chat_channel.send(self.add_to_whitelist(minecraft_name, client_type))
                status = await self.name_and_role(user, minecraft_name, member_role)
                await interaction.response.send_message(f"{status}", ephemeral=True)
                
            # if user IS staff AND command IS NOT used in private thread:
            elif interaction.user.get_role(constant.STAFF_ROLE_ID) and not command_channel.type == discord.ChannelType.private_thread: 
                await interaction.response.send_message("You're in the wrong channel for that command!", ephemeral=True)
            # if user IS staff AND command IS used in private thread AND private thread parent IS NOT #apply-here:
            elif interaction.user.get_role(constant.STAFF_ROLE_ID) and command_channel.type == discord.ChannelType.private_thread and not command_channel.parent_id == constant.APP_CHANNEL_ID:
                await interaction.response.send_message("You're in the wrong channel for that command!", ephemeral=True)

            # else user IS NOT staff
            else:
                await interaction.response.send_message("You don't have permission to use that command.", ephemeral=True)


    @app_commands.command(name="deny", description="Deny a whitelist")
    async def deny(
                self,
                interaction, 
                user: discord.Member,
                reason: str
                ):

            command_channel = interaction.channel
            log_channel = self.bot.get_channel(constant.LOGS_CHANNEL_ID)
            deniedEmbed = discord.Embed(title="Application Denied", color=0xe74d3c)
            publicDeniedEmbed = discord.Embed(title="❌ Application Denied", color=0xe74d3c)

            # if user IS staff AND command IS used in private thread AND private thread parent IS #apply-here:
            if interaction.user.get_role(constant.STAFF_ROLE_ID) and command_channel.type == discord.ChannelType.private_thread and command_channel.parent_id == constant.APP_CHANNEL_ID:
                deniedEmbed.add_field(name="User", value=f"<@{user.id}> ({user.name})", inline=True)
                deniedEmbed.add_field(name="Staff Member", value=f"<@{interaction.user.id}> ({interaction.user.name})", inline=True)
                deniedEmbed.add_field(name="Denial Reason", value=f"{reason}", inline=False)
                deniedEmbed.add_field(name="Thread", value=f"<#{command_channel.id}>", inline=False)
                deniedEmbed.set_thumbnail(url=f"{interaction.user.avatar}")
                deniedEmbed.set_footer(text=f"User ID: {interaction.user.id}")
                deniedEmbed.timestamp = datetime.datetime.now()

                publicDeniedEmbed.description = f"Application denied by <@{interaction.user.id}>\nReason: `{reason}`"
                publicDeniedEmbed.timestamp = datetime.datetime.now()

                await interaction.response.send_message("Application Denied.", ephemeral=True)
                await command_channel.send(embed=publicDeniedEmbed)
                await log_channel.send(embed=deniedEmbed)
            
            
            # if user IS staff AND command IS NOT used in private thread:
            elif interaction.user.get_role(constant.STAFF_ROLE_ID) and not command_channel.type == discord.ChannelType.private_thread: 
                await interaction.response.send_message("You're in the wrong channel for that command!", ephemeral=True)
            # if user IS staff AND command IS used in private thread AND private thread parent IS NOT #apply-here:
            elif interaction.user.get_role(constant.STAFF_ROLE_ID) and command_channel.type == discord.ChannelType.private_thread and not command_channel.parent_id == constant.APP_CHANNEL_ID:
                await interaction.response.send_message("You're in the wrong channel for that command!", ephemeral=True)

            # else user IS NOT staff
            else:
                await interaction.response.send_message("You don't have permission to use that command.", ephemeral=True)


    @app_commands.command(name="quick-approve", description="Simple /approve without channel requirements.")
    @app_commands.describe(client_type="The applicant's platform.")
    async def quickapprove(
                        self,
                        interaction,
                        user: discord.Member,
                        minecraft_name: str,
                        client_type: Platforms
                        ):

            command_channel = interaction.channel
            log_channel = self.bot.get_channel(constant.LOGS_CHANNEL_ID)
            chat_channel = self.bot.get_channel(constant.CHAT_CHANNEL_ID)
            member_role = interaction.guild.get_role(constant.MEMBER_ROLE_ID)
            approvedEmbed = discord.Embed(title="Application Quick Approved", color=0x72c87a)

            if interaction.user.get_role(constant.STAFF_ROLE_ID):
                approvedEmbed.clear_fields()
                approvedEmbed.add_field(name="User", value=f"<@{user.id}> ({user.name})", inline=True)
                approvedEmbed.add_field(name="Staff Member", value=f"<@{interaction.user.id}> ({interaction.user.name})", inline=True)
                approvedEmbed.add_field(name="** **", value="** **", inline=False)
                approvedEmbed.add_field(name="Minecraft Name", value=f"** ** ** ** ** ** ** **`{minecraft_name}`", inline=True)
                approvedEmbed.add_field(name="Client", value=f"** ** ** ** ** ** ** **`{client_type.name}`", inline=True)
                approvedEmbed.set_thumbnail(url=f"{user.avatar}")
                approvedEmbed.set_footer(text=f"User ID: {interaction.user.id}")
                approvedEmbed.timestamp = datetime.datetime.now()


                await chat_channel.send(await self.add_to_whitelist(minecraft_name, client_type))
                await command_channel.send(f"**{minecraft_name}** has been added to the whitelist.")
                await log_channel.send(embed=approvedEmbed)

                status = await self.name_and_role(user, minecraft_name, member_role)
                await interaction.response.send_message(f"{status}", ephemeral=True)

            else:
                await interaction.response.send_message("You don't have permission to use that command.", ephemeral=True)


    # add a /close command here

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))