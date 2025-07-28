## [[Invite Bot]](https://discord.com/oauth2/authorize?client_id=1397280746946822354&permissions=1496930446352&integration_type=0&scope=applications.commands+bot)


## To-Do List
```diff
+ GREEN: IMPLEMENTED -> MAY BE UPDATED IN FUTURE
- RED: UNIMPLEMENTED -> PLANNED FOR FUTURE
! YELLOW: ON HOLD | MAY NOT BE IMPLEMENTED | IN PROGRESS

══════════════════════════════════════════════════════════════════════════════════════════

+ disallow members to apply

! re-whitelist button for members to get re-added [MAYBE]

+ edit old embed application message when bot start

! add try/except methods to things that can break [WIP]

- don't let people with open applications apply again 
-   (append user ID to list/json on button press, remove when denied)
-   check if a person has applied in the past, update thread to include #2, #3 etc

+ add way to whitelist people with no application thread ('/quick-apply')

- add statistics for each staff member that has accepted/denied and average time
-   timestamp comparison between start application and accept/deny application
-   user id tracking

+ Move embed message for application from constants.py to text file storage
+   '$reload' command to update the application file somehow

+ send whitelist commands to #mc-chat

- add ping role for 'available to accept'

! add ping after X hours as reminder to approve [MAYBE]

! split various functions into smaller or more generalized functions [WIP]
-   also do the same for the '/approve' and '/deny' commands -> remove lots of duplicate code

! look into using sqlite for storage instead -> better integration into existing barebones database? [WIP]

! soon might need to split slash_commands into individual files [MAYBE]

+ Add some way to update the whitelist_message.txt from a command without needing to directly access the file

- "cry about it" onmessage response dead server
-   1/50 chance of replying or something, and X hours cooldown after
```
</br>
</br>
</br>

keeping this for later
```python
with open('filename.json', 'r') as file:
    json_data = json.load(file)

json_data['some_id'][0]['embed'] = 'Some string'
with open('filename.json', 'w') as file:
    json.dump(json_data, file, indent=2)
```
