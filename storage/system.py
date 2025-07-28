from discord import app_commands

class CustomErrors():
    class UserIsNotStaff(app_commands.CheckFailure):
        pass # error to handle user missing staff role
    class InvalidCommandChannel(app_commands.CheckFailure):
        pass #error to handle command used in incorrect channel
    class UserIsNotOwner(app_commands.CheckFailure):
        pass #error to handle if command used by someone other than owner

class Constants():
    SERVER_ID = 1085767835495714888
    OWNER_ID = 624613879414259789

    STAFF_ROLE_ID = 1397108751579873371
    MEMBER_ROLE_ID = 1397367926440329216

    CHAT_CHANNEL_ID = 1397063461900648551
    APP_CHANNEL_ID = 1397078581435170917
    LOGS_CHANNEL_ID = 1397088020611596458
    SUPPORT_CHANNEL_ID = 1399520483795538021