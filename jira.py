import os, json, urllib.parse, requests, discord, threading
from flask import Flask
from requests.auth import HTTPBasicAuth
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
JIRA_URL = os.getenv("JIRA_URL")
EMAIL = os.getenv("EMAIL")
API_TOKEN = os.getenv("API_TOKEN")
PROJECT_ID = os.getenv("PROJECT_ID")
PROJECT_KEY = os.getenv("PROJECT_KEY")
ISSUE_TYPE_ID = os.getenv("ISSUE_TYPE_ID")  
BOARD_ID = os.getenv("BOARD_ID") 
#CLOUD_RUN_BASE = os.getenv("CLOUD_RUN_BASE")


intents = discord.Intents.default()
intents.message_content = True  # required for reading message text
bot = commands.Bot(command_prefix="!", intents=intents)


def keep_alive():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return "Bot running!"

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=keep_alive, daemon=True).start()




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
        issue_url = f"{JIRA_URL}/jira/software/c/projects/{PROJECT_KEY}/boards/{BOARD_ID}?selectedIssue={issue_key}"
        return issue_url

    else:
        return f"Error {r.status_code}: {r.text}"



@bot.tree.context_menu(name="Later")
async def later_action(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer(ephemeral=True)
    description = message.content or "No message content provided."
    summary = "Untitled Task"
    issue_url = create_jira_task(summary, description)

    if issue_url:
        #redirect_url = f"{CLOUD_RUN_BASE}/jira?link={urllib.parse.quote(issue_url)}"
        redirect_url = f"https://jira-bot-fapf.onrender.com/jira?link={urllib.parse.quote(issue_url)}"

        await interaction.response.send_message(
            f"Task created! Redirecting… {redirect_url}"
        )
    else:
        await interaction.response.send_message(
            "Failed to create task.", ephemeral=True
        )


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()
    print("Synced commands.")
   

if __name__ == "__main__":
    bot.run(TOKEN)




