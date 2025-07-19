import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # মেসেজ পড়ার অনুমতি

bot = commands.Bot(command_prefix="!", intents=intents)

# তোমার remote সার্ভার ও চ্যানেল ID গুলো এখানে বসাবে
REMOTE_SERVERS = {
    "server1": (1373917931167289414, 1387869893025857737),  # (guild_id, channel_id)
    "server2": (1389385737786495098, 1389385739141120062),
}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="runremote", description="Send a message to another server channel")
@app_commands.describe(server_name="Target server short name", message="Message to send")
async def runremote(interaction: discord.Interaction, server_name: str, message: str):
    await interaction.response.defer(thinking=True)

    if server_name not in REMOTE_SERVERS:
        await interaction.followup.send(f"❌ Server `{server_name}` not found.")
        return

    guild_id, channel_id = REMOTE_SERVERS[server_name]
    guild = bot.get_guild(guild_id)
    if guild is None:
        await interaction.followup.send(f"❌ Bot is not in the guild/server `{server_name}`.")
        return

    channel = guild.get_channel(channel_id)
    if channel is None:
        await interaction.followup.send(f"❌ Channel not found in server `{server_name}`.")
        return

    try:
        await channel.send(f"[Remote message from {interaction.user}]: {message}")
        await interaction.followup.send(f"✅ Message sent to `{server_name}`.")
    except Exception as e:
        await interaction.followup.send(f"⚠️ Failed to send message: {e}")

bot.run(TOKEN)
