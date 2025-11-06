
#------------------------------------------- DELETES GUILD COMMANDS --------------------------------------------


# import os, requests
# from dotenv import load_dotenv
# load_dotenv()

# TOKEN = os.getenv("DISCORD_TOKEN")
# APP_ID = os.getenv("APPLICATION_ID")
# GUILD_ID = os.getenv("GUILD_ID")

# url = f"https://discord.com/api/v10/applications/{APP_ID}/guilds/{GUILD_ID}/commands"

# # This replaces all guild commands with an empty list
# r = requests.put(
#     url,
#     headers={"Authorization": f"Bot {TOKEN}"},
#     json=[]
# )

# print("Status:", r.status_code)
# print("Response:", r.text)

# -------------------------------------------------------------------------------------------------------------

# import os, requests
# from dotenv import load_dotenv
# load_dotenv()

# TOKEN = os.getenv("DISCORD_TOKEN")
# APP_ID = os.getenv("APPLICATION_ID")

# url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"

# # Clear global commands
# r = requests.put(url, headers={"Authorization": f"Bot {TOKEN}"}, json=[])

# print("✅ Global commands cleared.")
# print("Status:", r.status_code, r.text)



#------------------------------------------    DELETES GLOBAL COMMANDS  ------------------------------------------------

# import os, requests
# from dotenv import load_dotenv
# load_dotenv()

# TOKEN = os.getenv("DISCORD_TOKEN")
# APP_ID = os.getenv("APPLICATION_ID")  # <- This must be the App ID for your current LaterBot

# url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"

# r = requests.put(
#     url,
#     headers={"Authorization": f"Bot {TOKEN}"},
#     json=[]
# )

# print("✅ Global commands cleared.")
# print("Status:", r.status_code, r.text)

