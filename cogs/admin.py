import json

import discord
from discord.ext import commands

from config import OWNER_ID, PREM, WHITELIST
from core.operation import leave_all_servers


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addprem")
    async def addprem(self, ctx):
        if ctx.author.id not in WHITELIST:
            await ctx.send("❌ no perms to use this.")
            return

        with open("data/premium.json", "r", encoding="utf-8") as f:
            premium_ids = json.load(f)

        role = ctx.guild.get_role(PREM)
        if not role:
            await ctx.send("❌ role not found")
            return

        found_count = 0
        added_count = 0

        for user_id in premium_ids:
            member = ctx.guild.get_member(user_id)
            if member:
                found_count += 1
                if role not in member.roles:
                    try:
                        await member.add_roles(role)
                        added_count += 1
                    except discord.Forbidden:
                        print("no perms or not found")

        await ctx.send(f"{found_count} from {len(premium_ids)} users found on the server")
        await ctx.send(f"adding {added_count} roles")
        await ctx.send(f"finished adding {added_count} roles")

    @commands.command()
    async def leave(self, ctx):
        if ctx.author.id != OWNER_ID:
            await ctx.send("❌ You are not authorized to use this command.")
            return
        await leave_all_servers()

async def setup(bot):
    await bot.add_cog(Admin(bot))
