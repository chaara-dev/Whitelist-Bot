## [[Invite Bot]](https://discord.com/oauth2/authorize?client_id=1397280746946822354&permissions=1496930446352&integration_type=0&scope=applications.commands+bot)


## LIST OF THINGS TO ADD

- ~~disallow members to apply~~
- re-whitelist button for members to get re-added (maybe)
- '/close' command to close threads [threads timeout automatically after 1 hour or 24 hours]

- ~~edit old embed application message when bot start~~

- add try/except methods to things that can break

- don't let people with open applications apply again 
    - (append user ID to list on button press, remove when denied)
    - check if a person has applied in the past, update thread to include #2, #3 etc

- Add statistics for each staff member that has accepted/denied and average time
    - (timestamp comparison)

- /reload command to update the application file

</br>
</br>
</br>

keeping this for later
```
with open('filename.json', 'r') as file:
    json_data = json.load(file)

json_data['some_id'][0]['embed'] = 'Some string'
with open('filename.json', 'w') as file:
    json.dump(json_data, file, indent=2)
```
