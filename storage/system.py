from discord import app_commands

class CustomErrors():
    class UserIsNotStaff(app_commands.CheckFailure):
        pass # error to handle user missing staff role
    class InvalidCommandChannel(app_commands.CheckFailure):
        pass #error to handle command used in incorrect channel
    class UserIsNotOwner(app_commands.CheckFailure):
        pass #error to handle if command used by someone other than owner

class Constants():
    SERVER_ID = 121769661439279105 # BareBonesMP Discord Server ID
    OWNER_ID = 121769553603723265 # @nomanasendhelp ID
    BRICKY_ID = 624613879414259789 # @lostbrickplacer ID

    STAFF_ROLE_ID = 767810219882840114 # Staff (not Team) Role ID
    AVAILABLE_ROLE_ID = 1399423222713290914 # Applications Role
    MEMBER_ROLE_ID = 566792092983099405 # Members Role

    CHAT_CHANNEL_ID = 549297756431187968 # #mc-chat Channel
    APP_CHANNEL_ID = 0 # Wait and see for new channel or not
    LOGS_CHANNEL_ID = 586021406660362251 # #whitelist-archive Channel
    SUPPORT_CHANNEL_ID = 1115338787187331122 # #🔎|support Channel
    ROLE_CHANNEL_ID = 1383077869244387358 # #staff-resources Channel



class OldConstants():
    SERVER_ID = 1085767835495714888
    OWNER_ID = 624613879414259789

    STAFF_ROLE_ID = 1397108751579873371
    AVAILABLE_ROLE_ID = 1399281907027673138
    MEMBER_ROLE_ID = 1397367926440329216

    CHAT_CHANNEL_ID = 1397063461900648551
    APP_CHANNEL_ID = 1397078581435170917
    LOGS_CHANNEL_ID = 1397088020611596458
    SUPPORT_CHANNEL_ID = 1399520483795538021
    ROLE_CHANNEL_ID = 1399282269440442529
