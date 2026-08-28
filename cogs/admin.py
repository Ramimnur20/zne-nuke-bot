import json

import discord
from discord.ext import commands
from discord.ext.commands import BucketType, CommandOnCooldown, cooldown

from config import MOD_ROLE_ID, PREM, WHITELIST
from core.utils import load_premium_users


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
    @commands.has_role(MOD_ROLE_ID)
    @cooldown(1, 600, BucketType.user)
    async def modraid(self, ctx, *, message=None):
        if message is None:
            await ctx.send("use a message dumbass")
            return

        role = ctx.guild.get_role(MOD_ROLE_ID)
        if role is None:
            await ctx.send("role not found.")
            return

        await ctx.send(f"{message}\n<@&1415313470710349834>\n\nSent from {ctx.author.mention}")
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send("I don't have permission to delete messages.")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to delete message: {e}")

    @modraid.error
    async def modraid_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown. Try again in {int(error.retry_after)} seconds.")


async def setup(bot):
    await bot.add_cog(Admin(bot))
