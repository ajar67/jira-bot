# import os, requests # type: ignore
# from dotenv import load_dotenv
# load_dotenv()

# TOKEN = os.getenv("DISCORD_TOKEN")
# APP_ID = os.getenv("APPLICATION_ID")
# GUILD_ID = os.getenv("GUILD_ID")

# url = f"https://discord.com/api/v10/applications/{APP_ID}/guilds/{GUILD_ID}/commands"

# command = {
#     "name": "Later",
#     "type": 3,
# }

# headers = {"Authorization": f"Bot {TOKEN}"}
# r = requests.post(url, headers=headers, json=command)
# print(r.status_code, r.text)
