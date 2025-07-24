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

    @app_commands.command(name="approve", description="Approve a whitelist")
    @app_commands.describe(client_type="The applicant's platform")
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
            approvedEmbed = discord.Embed(title="Application Approved", color=0x72c87a)
            publicApprovedEmbed = discord.Embed(title="✅ Application Approved", color=0x72c87a)


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

                await interaction.response.send_message("Application Approved.", ephemeral=True)
                await command_channel.send(embed=publicApprovedEmbed)
                await log_channel.send(embed=approvedEmbed)



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
                    await log_channel.send(f"❗ Failed to change **{user.name}**'s nickname. Missing Permissions.")

                try:
                    member_role = discord.utils.get(user.guild.roles, id=constant.MEMBER_ROLE_ID)
                    await user.add_roles(member_role)
                except discord.Forbidden:
                    print(colored("Error:", "red"), f"Error adding {member_role.name} role to {user.name}. Missing Permissions.")
                    await log_channel.send(f"❗ Failed to add **{member_role.name}** role to **{user.name}**. Missing Permissions.")
                except discord.HTTPException:
                    print(colored("Error:", "red"), f"Failed to add role to {user.name}.")
                
            elif interaction.user.get_role(constant.STAFF_ROLE_ID) and not command_channel.type == discord.ChannelType.private_thread: 
                await interaction.response.send_message("You're in the wrong channel for that command!", ephemeral=True)
            elif interaction.user.get_role(constant.STAFF_ROLE_ID) and command_channel.type == discord.ChannelType.private_thread and not command_channel.parent_id == constant.APP_CHANNEL_ID:
                await interaction.response.send_message("You're in the wrong channel for that command!", ephemeral=True)

            else:
                await interaction.response.send_message("You don't have permission to use that command.", ephemeral=True)



    @app_commands.command(name="deny", description="Deny a whitelist")
    async def deny(
                self,
                interaction, 
                user: discord.Member,
                reason: str
                ):

            command_channel: discord.Thread = interaction.channel
            log_channel = self.bot.get_channel(constant.LOGS_CHANNEL_ID)
            deniedEmbed = discord.Embed(title="Application Denied", color=0xe74d3c)
            publicDeniedEmbed = discord.Embed(title="❌ Application Denied", color=0xe74d3c)

            if interaction.user.get_role(constant.STAFF_ROLE_ID) and command_channel.type == discord.ChannelType.private_thread and command_channel.parent_id == constant.APP_CHANNEL_ID:
                deniedEmbed.add_field(name="User", value=f"<@{user.id}> ({user.name})", inline=True)
                deniedEmbed.add_field(name="Staff Member", value=f"<@{interaction.user.id}> ({interaction.user.name})", inline=True)
                deniedEmbed.add_field(name="Denial Reason", value=f"{reason}", inline=False)
                deniedEmbed.add_field(name="Thread", value=f"<#{command_channel.id}>", inline=False)
                deniedEmbed.set_thumbnail(url=f"{user.avatar}")
                deniedEmbed.set_footer(text=f"User ID: {interaction.user.id}")
                deniedEmbed.timestamp = datetime.datetime.now()

                publicDeniedEmbed.description = f"Application denied by <@{interaction.user.id}>\nReason: `{reason}`"
                publicDeniedEmbed.timestamp = datetime.datetime.now()

                await interaction.response.send_message("Application Denied.", ephemeral=True)
                await command_channel.send(embed=publicDeniedEmbed)
                await log_channel.send(embed=deniedEmbed)
            
            
            elif interaction.user.get_role(constant.STAFF_ROLE_ID) and not command_channel.type == discord.ChannelType.private_thread: 
                await interaction.response.send_message("You're in the wrong channel for that command!", ephemeral=True)
            elif interaction.user.get_role(constant.STAFF_ROLE_ID) and command_channel.type == discord.ChannelType.private_thread and not command_channel.parent_id == constant.APP_CHANNEL_ID:
                await interaction.response.send_message("You're in the wrong channel for that command!", ephemeral=True)

            else:
                await interaction.response.send_message("You don't have permission to use that command.", ephemeral=True)




async def setup(bot):
    await bot.add_cog(SlashCommands(bot))