import discord
import datetime
import json
import sqlite3
from contextlib import closing
from termcolor import colored
from discord.ext import commands, tasks

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
    #     self.create_table()


    # def create_table(self):
    #     self.execute_statement("""--sql
    #                 CREATE TABLE IF NOT EXISTS message_storage(
    #                     id INTEGER PRIMARY KEY
    #                     message_id TEXT NOT NULL
    #                     )
    #                 """, fetch=False)
    #     self.execute_statement("""--sql INSERT OR IGNORE INTO message_storage (id, message_id) VALUES (1, '')""", fetch=False)

    # def execute_statement(self, statement, fetch=False):
    #     with closing(sqlite3.connect("storage/database.db")) as conn: # auto-closes
    #         with conn: # auto-commits
    #             with closing(conn.cursor()) as cursor: # auto-closes
    #                 cursor.execute(statement)
    #                 if fetch:
    #                     return cursor.fetchone() # returns fetched row


    # def load_stored_id(self):
    #     try:
    #         row = self.execute_statement("""SELECT message_id FROM message_storage WHERE id = 1""", fetch=True)
    #         if row is not None: return row[0]
    #         else: return None
    #     except:
    #         return None


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


    # async def update_embed_message(self, self.load_stored_id(), self.load_whitelist_message(), self.bot.get_channel(constant.APP_CHANNEL_ID), ApplicationView(self.bot)):

    # BY DOING THIS YOU WILL NEED TO GO BACK THROUGH ALL OTHER FOUR (4) FUNCTION CALLS AND ADD APPROPRIATE PARAMETERS (see next line)
    # cog_core_function.update_embed_message(cog_core_function.load_stored_id, constant.AVAILABLE_CHANNEL, "Set whether you want to be pinged...", cog_core_function.AvailableRoleView)

    # async def update_embed_message(self, stored_message_id, embed_channel, embed_message, view):
    #     last_message = None
    #     if stored_message_id is not None:
    #         try:
    #             last_message = await embed_channel.fetch_message(stored_message_id)
    #         except discord.NotFound:
    #             async for searched_message in embed_channel.history(limit=100, oldest_first=True):
    #                 if searched_message.embeds and searched_message.author == self.bot.user:
    #                     try:
    #                         last_message = await embed_channel.fetch_message(searched_message.id)
    #                     except:
    #                         last_message = None

    #     if last_message is not None:
    #         if last_message.embeds and last_message.embeds[0].description == embed_message:
    #             return
    #         else:
    #             await last_message.edit(embed=view.placeholder_embed_title, view=view)
    #             print(colored(f"Embed message for {embed_channel.name}", "yellow"), "reloaded.")
    #     else:
    #         last_message = await embed_channel.send(embed=view.placeholder_embed_title, view=view)

    #     self.store_id(last_message.id)


    # tasks loop x hours (10080 minutes? or hours and stuff (1 week) - 6 days to account for bad timing or smth)
    # have original message sent (smth with adding another view (no need to update embed I think))
    # add 2 buttons to embed, green to get role red to remove role
        # check if staff regardless, should be in a private thread anyways
        # give available role | remove available role
        # fail giving/removing role quietly, only response.send_message() if roles were updated successfully
    # every @tasksloop, edit the message (check if that makes it not inactive/counts as activity)
        # if not, try sending/deleting message quickly (will mark channel as unread for everyone, probably want alternative way)
            # maybe reply to own embed message ephemerally?
    # should just be able to run `view=AvailabilityRole(self.bot)` then 
        # nvm will probably need to check if message exists already too -> check if can edit `update_embed_message()` to be more general?
    # need to add a new constant.CONSTANT as well
    # using sqlite to store ID probably, can add to existing table for embed_message ID
    


async def setup(bot):
    await bot.add_cog(CoreFunction(bot))
    bot.add_view(ApplicationView(bot)) # IMPORTANT!!!