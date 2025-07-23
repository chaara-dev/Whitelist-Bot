import discord, datetime, time, os, enum, typing
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

BUTTON_CHANNEL_ID = 1397063461900648551
APP_CHANNEL_ID = 1397078581435170917
LOGS_CHANNEL_ID = 1397088020611596458

WHITELIST_APP_MESSAGE = """
- Applicant must be at least 18 years old.
- Applicant must have read all info in ⁠:wave:︱welcome
- Please specify in your application whether your account is a Java or Bedrock account!
- If you're not comfortable putting your age, thats fine. 
- Just put "over 18" etc as the answer for age.
- While you're waiting for your app to be reviewed, checkout our ⁠:question:︱faq

## Whitelist Application Form:
```Minecraft Name: 
Age (18+): 
Is your account Bedrock or Java?: 
Where did you find out about us?: 
Why are you interested in joining?: 
What is your favorite thing about Minecraft?: 
What is the Keyword?: 
Do you agree to our server's rules?: ```
## NOTICE:
## Season 8 is about to end on August 1st, 2025; with season 9 starting August 9th, 2025
"""

SERVER_ID = 1085767835495714888
OWNER_ID = 624613879414259789

STAFF_ROLE_ID = 1397108751579873371
MEMBER_ROLE_ID = 1397367926440329216


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("$"), intents=intents)

templateEmbed = discord.Embed(title="Whitelist Application Requirements", description=WHITELIST_APP_MESSAGE, color=0x4654c0)
approvedEmbed = discord.Embed(title="Application Approved", color=0x72c87a)


class ApplicationView(discord.ui.View):
    @discord.ui.button(
              label="Apply for Whitelist", 
              style=discord.ButtonStyle.primary, 
              custom_id="whitelist_button"
              )
    
    async def button_callback(self, button, interaction):
                channel = bot.get_channel(APP_CHANNEL_ID)
                new_thread = await channel.create_thread(
                    name=f"{button.user.name} application", 
                    message=None, 
                    auto_archive_duration=60, 
                    type=discord.ChannelType.private_thread, 
                    reason=None,
                    invitable=False
                )

                time.sleep(1.5)
                await button.response.send_message(f"Your application thread was created at <#{new_thread.id}>.",ephemeral=True)
                await new_thread.send(embed=templateEmbed)

                # Silently pings Staff Team then deletes message (will automatically open thread for all staff)
                staff_ping = await new_thread.send("-# staff ping")
                await staff_ping.edit(content=f"<@&{STAFF_ROLE_ID}>")
                await new_thread.purge(limit=1)
                
                # Sends message to applicant (adds them to channel)
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
                
                logs = bot.get_channel(LOGS_CHANNEL_ID)
                await logs.send(embed=logEmbed)


# ----------------------------------------------------------------------------------------------------------------------------
# Slash Commands
class Platforms(enum.Enum):
     Java = 1
     Bedrock = 2
@bot.tree.command(name="approve", description="Approve a whitelist", guild=bot.get_guild(SERVER_ID))
@app_commands.describe(client_type="The applicant's platform")
async def approve(interaction, 
                  user: discord.Member,
                  minecraft_name: str,
                  client_type: Platforms,
                  message: typing.Optional[str] = "Welcome!"
                ):
        if interaction.user.get_role(STAFF_ROLE_ID):
            approvedEmbed.add_field(name="User", value=f"<@{user.id}>", inline=True)
            approvedEmbed.add_field(name="Staff Member", value=f"<@{interaction.user.id}>", inline=True)
            approvedEmbed.add_field(name="** **", value="** **", inline=False)
            approvedEmbed.add_field(name="Minecraft Name", value=f"`{minecraft_name}`", inline=True)
            approvedEmbed.add_field(name="Client", value=f"`{client_type.name}`", inline=True)

            approvedEmbed.add_field(name="Thread", value=f"<#{interaction.channel.id}>", inline=False)

            approvedEmbed.set_thumbnail(url=f"{user.avatar}")
            approvedEmbed.timestamp = datetime.datetime.now()
            approvedEmbed.set_footer(text=f"User ID: {interaction.user.id}")

            logs = bot.get_channel(LOGS_CHANNEL_ID)
            await logs.send(embed=approvedEmbed)

            await interaction.response.send_message("Application Approved.", ephemeral=True)
            await interaction.channel.send(content=f"Application Approved. {message}")


            await interaction.channel.edit(
                 name=f"{minecraft_name} application ✅",
                 locked=True,
                 archived=True,
                 invitable=False
                )
            await user.edit(nick=minecraft_name)
            # await user.add_roles(MEMBER_ROLE_ID) # THIS IS BROKEN!!!!!!


        else:
            await interaction.response.send_message("You don't have permission to use that command.", ephemeral=True)

# ----------------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------------
# Text Commands
@bot.command()
async def purge(context, amount: int):
    if context.author.id == OWNER_ID:
        deleted = await context.channel.purge(limit=amount + 1)
        await context.send(f"Deleted {len(deleted) - 1} message(s).", delete_after=0.25)
    else:
        await context.reply(content="You can't use that command!", delete_after=2)

@bot.command()
async def sync(context):
        if context.author.id == OWNER_ID:
            await bot.tree.sync()
            print("Syncing...")
            await context.send("Command tree synced.")
            print("Synced.")
            await context.channel.purge(limit=2)
            
        else:
            await context.send(content="You must be the owner to use this command.", delete_after=2)

# ----------------------------------------------------------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for applications."))

    channel = bot.get_channel(APP_CHANNEL_ID)
    if channel:
        view = ApplicationView()
        await channel.send(embed=templateEmbed, view=view)




# Run the bot
load_dotenv()
bot.run(os.getenv("TOKEN"))
