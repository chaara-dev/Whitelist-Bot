import discord
import datetime
import json
from termcolor import colored
from discord.ext import commands

from storage.system import Constants as constant

class ApplicationView(discord.ui.View):
    def __init__(self, bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.templateEmbed = discord.Embed(title="Whitelist Application Requirements", description=CoreFunction.load_whitelist_message(self), color=0x4654c0)

    @discord.ui.button(label="Apply for Whitelist", style=discord.ButtonStyle.primary, custom_id="whitelist_button")
    @commands.Cog.listener()
    async def button_callback(self, button, interaction):
        try:
            channel = self.bot.get_channel(constant.APP_CHANNEL_ID)
            if button.user.get_role(constant.MEMBER_ROLE_ID) is None or button.user.id == constant.OWNER_ID:
                new_thread = await channel.create_thread(
                    name=f"{button.user.name} application", 
                    message=None, 
                    auto_archive_duration=1440, 
                    type=discord.ChannelType.private_thread, 
                    reason=None,
                    invitable=False
                )

                await button.response.send_message(f"Your application thread was created at <#{new_thread.id}>.",ephemeral=True)
                await new_thread.send(embed=self.templateEmbed)
                
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
                    await button.response.send_message(f"You've already applied for the whitelist. If you have since been removed, please contact a\n Staff member.", ephemeral=True)
                except Exception as idfk:
                    print(f"error: {idfk}")
                    await button.response.send_message("Something went wrong. Please try again later.\nIf the error persists, contact a Staff member.", ephemeral=True)
        except Exception as e:
            print(f"ERROR: {e}")

class CoreFunction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # load message ID from json storage for application channel
    def load_stored_id(self):
        try:
            with open('storage/message_id.json', 'r') as file:
                data = json.load(file)
                return data.get('message_id', None)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return None


    # store message ID to json storage for application channel
    def store_id(self, message_id):
        with open('storage/message_id.json', 'w') as file:
            json.dump({'message_id': message_id}, file)


    # load whitelist message details from txt storage
    def load_whitelist_message(self):
        try:
            with open("storage/whitelist_message.txt", "r") as file:
                return file.read()
        except FileNotFoundError:
            return None


    # check id and contents of whitelist message and update/send depending
    async def update_embed_message(self):
        last_message = None
        application_channel = self.bot.get_channel(constant.APP_CHANNEL_ID)
        view = ApplicationView(self.bot)
        stored_message_id = self.load_stored_id()
        whitelist_message = self.load_whitelist_message()

        if stored_message_id is not None:
            try:
                last_message = await application_channel.fetch_message(stored_message_id)
            except discord.NotFound:
                async for searched_message in application_channel.history(limit=100, oldest_first=True):
                    if searched_message.embeds and searched_message.author == self.bot.user:
                        try:
                            last_message = await application_channel.fetch_message(searched_message.id)
                        except:
                            last_message = None

        if last_message is not None:
            if last_message.embeds and last_message.embeds[0].description == whitelist_message:
                return 
            else:
                await last_message.edit(embed=view.templateEmbed, view=view)
                print(colored("Embed message", "yellow"), "reloaded.")
        else:
            last_message = await application_channel.send(embed=view.templateEmbed, view=view)

        self.store_id(last_message.id)


async def setup(bot):
    await bot.add_cog(CoreFunction(bot))
    bot.add_view(ApplicationView(bot)) # IMPORTANT!!!