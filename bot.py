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


@client.tree.command(name="like", description="Send like to Free Fire UID")
@app_commands.describe(uid="Enter Free Fire UID", region="Enter Server Region (e.g. BD)")
async def like(interaction: discord.Interaction, uid: str, region: str):
    import aiohttp

    # চ্যানেল রেজিস্টার চেক
    

    if not uid.isdigit():
        await interaction.response.send_message("❌ Invalid UID! Example: `/like 123456789`", ephemeral=True)
        return

    await interaction.response.defer()

    url = f"https://like-api2.vercel.app/like?uid={uid}&server_name={region}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    await interaction.followup.send(f"❌ API returned bad status: {resp.status}")
                    return

                data = await resp.json()

                status = data.get("status")
                nickname = data.get("PlayerNickname")
                uid = data.get("UID")
                likes_before = data.get("LikesbeforeCommand")
                likes_added = data.get("LikesGivenByAPI")
                likes_after = data.get("LikesafterCommand")

                if status == 1:
                    info = (
                        f"```┌ FREE FIRE LIKE ADDED\n"
                        f"├─ Nickname: {nickname}\n"
                        f"├─ Likes Before: {likes_before}\n"
                        f"├─ Likes Added: {likes_added}\n"
                        f"└─ Likes After: {likes_after}\n"
                        f"UID: {uid}```"
                    )
                    embed = discord.Embed(
                        title="🔥 Free Fire Like Added!",
                        description=info,
                        color=discord.Color.purple()
                    )
                    embed.set_thumbnail(url=interaction.user.display_avatar.url)
                    embed.set_image(url="https://i.imgur.com/ajygBes.gif")
                    embed.set_footer(text="📌 Dev </> GAMER SABBIR")
                    await interaction.followup.send(embed=embed)
                    return

                elif status == 2:
                    await interaction.followup.send(
                        f"⚠️ No new likes were added.\n```Nickname: {nickname}\nUID: {uid}\nLikes: {likes_after}```"
                    )
                    return

                else:
                    await interaction.followup.send("⚠️ Unexpected response. Please try again later.")

    except Exception as e:
        short_error = str(e)
        if len(short_error) > 1900:
            short_error = short_error[:1900] + "..."
        await interaction.followup.send(f"❌ Error:\n```{short_error}```", ephemeral=True)


bot.run(TOKEN)
