import os, json, urllib.parse, requests, threading
from flask import Flask, redirect, request
from requests.auth import HTTPBasicAuth
from discord.ext import commands
from dotenv import load_dotenv
import discord

# === Load environment ===
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
JIRA_URL = os.getenv("JIRA_URL")
EMAIL = os.getenv("EMAIL")
API_TOKEN = os.getenv("API_TOKEN")
PROJECT_ID = os.getenv("PROJECT_ID")
PROJECT_KEY = os.getenv("PROJECT_KEY")
ISSUE_TYPE_ID = os.getenv("ISSUE_TYPE_ID")
BOARD_ID = os.getenv("BOARD_ID")
SERVER_DOMAIN = os.getenv("SERVER_DOMAIN")

# === Discord bot setup ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === Register your command BEFORE on_ready ===
@bot.tree.context_menu(name="Later")
async def later_action(interaction: discord.Interaction, message: discord.Message):
    try:
        await interaction.response.defer(ephemeral=True)
    except discord.errors.NotFound:
        print("Interaction expired before defer()")
        return

    description = message.content or "No message content provided."
    summary = "Untitled Task"
    issue_url = create_jira_task(summary, description)
    if issue_url:
        redirect_url = f"http://{SERVER_DOMAIN}/jira?link={urllib.parse.quote(issue_url)}"
        await interaction.followup.send(f"Task created! [Open in Jira]({redirect_url})", ephemeral=True)
    else:
        await interaction.followup.send("Failed to create task.", ephemeral=True)

# === on_ready must come AFTER command definition ===
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    guild = discord.Object(id=GUILD_ID)
    # Sync to your guild for instant availability
    guild_commands = await bot.tree.sync(guild=guild)
    print(f"Synced {len(guild_commands)} guild commands to {guild.id}")

    # Also push globally (takes time but ensures persistence)
    global_commands = await bot.tree.sync()
    print(f"Synced {len(global_commands)} global commands.")

    print("All commands registered successfully.")


# === Flask server ===
app = Flask(__name__)

@app.route("/")
def home():
    return "Jira Redirect Service is running!"

@app.route("/jira")
def go_to_jira():
    jira_link = request.args.get("link")
    if not jira_link:
        return "Missing Jira link", 400
    return redirect(jira_link, code=302)

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# === Jira helper functions ===
def get_active_sprint_id():
    url = f"{JIRA_URL}/rest/agile/1.0/board/{BOARD_ID}/sprint?state=active"
    r = requests.get(url, auth=HTTPBasicAuth(EMAIL, API_TOKEN))
    data = r.json()
    try:
        return data["values"][0]["id"]
    except (KeyError, IndexError):
        return None
    
def create_jira_task(summary, description):
    sprint_id = get_active_sprint_id()
    url = f"{JIRA_URL}/rest/api/3/issue"
    auth = HTTPBasicAuth(EMAIL, API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    payload = {
        "fields": {
            "project": {"id": PROJECT_ID},
            "summary": summary[:255],
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": description}]}
                ]
            },
            "issuetype": {"id": ISSUE_TYPE_ID},
        }
    }

    if sprint_id:
        payload["fields"]["customfield_10020"] = sprint_id

    r = requests.post(url, auth=auth, headers=headers, data=json.dumps(payload))
    if r.status_code == 201:
        issue_key = r.json()["key"]
        return f"{JIRA_URL}/browse/{issue_key}"
    else:
        return f"Error {r.status_code}: {r.text}"


# === Start both ===
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(TOKEN)

