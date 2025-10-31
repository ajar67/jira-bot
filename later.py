import os
import sqlite3
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dateparser import parse
import discord
from discord import app_commands, InteractionType, ui
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()

# --- DB setup ---
conn = sqlite3.connect("later.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id TEXT,
    collaborators TEXT,
    channel_id TEXT,
    message_link TEXT,
    note TEXT,
    remind_at TEXT,
    visibility TEXT
)
""")
conn.commit()





# --- Modal for note & time ---
class LaterModal(ui.Modal, title="Save for Later"):
    #
    note = ui.TextInput(label="Note (optional)", style=discord.TextStyle.paragraph, required=False)
    #do we want to use regex to split time from original message 
    remind_time = ui.TextInput(label="When should I remind you? (e.g. tomorrow 3pm)", required=True)
    #maybe we want to have drop down list of who we want to also share with
    collaborators = ui.TextInput(label="Tag collaborators (optional, comma separated @names)", required=False)

    def __init__(self, interaction, message_link):
        super().__init__()
        self.interaction = interaction
        self.message_link = message_link

    async def on_submit(self, interaction: discord.Interaction):
        # parse reminder time
        parsed = parse(self.remind_time.value, settings={"PREFER_DATES_FROM": "future"})
        if not parsed:
            await interaction.response.send_message("Could not understand that time.", ephemeral=True)
            return

        # format collaborators
        collaborators = self.collaborators.value.strip()
        visibility = "shared" if collaborators else "private"

        # save task
        c.execute("""
        INSERT INTO tasks (creator_id, collaborators, channel_id, message_link, note, remind_at, visibility)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(interaction.user.id),
            collaborators,
            str(interaction.channel_id),
            self.message_link,
            self.note.value.strip(),
            parsed.isoformat(),
            visibility
        ))
        conn.commit()
        task_id = c.lastrowid

        # schedule reminder
        scheduler.add_job(send_reminder, "date", run_date=parsed, args=[task_id])
        await interaction.response.send_message(
            f"Task saved for **{parsed.strftime('%Y-%m-%d %H:%M:%S')} UTC**.\n[Jump to message]({self.message_link})",
            ephemeral=True
        )






async def send_reminder(task_id):
    c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = c.fetchone()
    if not task:
        return

    _, creator_id, collaborators, channel_id, link, note, remind_at, visibility = task
    user = await client.fetch_user(int(creator_id))
    reminder_text = f"⏰ **Reminder:** [Go to message]({link})\n📝 {note or '(no note)'}"

    try:
        if visibility == "private":
            await user.send(reminder_text)
        else:
            channel = await client.fetch_channel(int(channel_id))
            mention_str = ", ".join(collaborators.split(",")) if collaborators else f"<@{creator_id}>"
            await channel.send(f"{mention_str} — {reminder_text}")
    except Exception as e:
        print("Could not send reminder:", e)
    finally:
        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    scheduler.start()

@client.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != InteractionType.application_command:
        return
    if interaction.data["name"] != "Later":
        return

    target_id = interaction.data.get("target_id")
    channel = await client.fetch_channel(interaction.channel_id)
    msg = await channel.fetch_message(target_id)
    message_link = f"https://discord.com/channels/{interaction.guild_id}/{interaction.channel_id}/{msg.id}"

    modal = LaterModal(interaction, message_link)
    await interaction.response.send_modal(modal)

client.run(TOKEN)
