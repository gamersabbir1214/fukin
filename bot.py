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

@bot.command()
async def runremote(ctx, *, arg):
    try:
        args = dict(item.split(":") for item in arg.split(" ") if ":" in item)
        server_name = args.get("server_name")
        message = args.get("message")

        if not server_name or not message:
            await ctx.send("Usage: /runremote server_name: <name> message: <text>")
            return

        if server_name not in REMOTE_SERVERS:
            await ctx.send(f"Unknown server: {server_name}")
            return

        guild_id, channel_id = REMOTE_SERVERS[server_name]
        guild = bot.get_guild(int(guild_id))
        if not guild:
            await ctx.send("Guild not found or bot is not in that server.")
            return

        channel = guild.get_channel(int(channel_id))
        if not channel:
            await ctx.send("Channel not found.")
            return

        # এখানে শুধু message পাঠাচ্ছি, author tag ছাড়াই
        await channel.send(message)
        await ctx.send("Message sent successfully.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

bot.run(TOKEN)
