import asyncio

import discord
from discord.ext import commands
from core.bot import bot
from core.utils import is_premium_user

from config import BLACKLISTED_GUILD_ID

@commands.command()
async def fakenitro(ctx):
    if ctx.guild and ctx.guild.id == BLACKLISTED_GUILD_ID:
        await ctx.reply("`this server is blacklisted`")
        return

    try:
        await ctx.message.delete()
    except:
        pass

    try:
        dm_channel = await ctx.author.create_dm()
        await dm_channel.send(
            "**:gift: Fake Nitro Setup**\n"
            "Please choose your method:\n\n"
            "🔹 `1` - Spam every channel\n"
            "🔹 `2` - Create giveaway channel with ghost pings (looks more real = more people joining)\n\n"
            "Reply with the number!"
        )

        def check(m):
            return m.author == ctx.author and m.channel == dm_channel and m.content in ["1", "2"]

        reply = await bot.wait_for("message", check=check, timeout=60)

        if reply.content == "1":
            method = "spam"
        elif reply.content == "2":
            method = "giveaway"
        else:
            return await dm_channel.send("❌ Invalid selection, setup aborted.")

        is_premium = is_premium_user(ctx.author.id)

        if is_premium:
            await dm_channel.send("You are a premium user! Please send your custom invite link or type `default` to use the standard link.")

            def link_check(m):
                return m.author == ctx.author and m.channel == dm_channel

            try:
                link_msg = await bot.wait_for("message", check=link_check, timeout=60)
                if link_msg.content.lower() == "default":
                    fake_link = "https://discord.gg/VSQzzAMVw3"
                else:
                    fake_link = link_msg.content.strip()
            except asyncio.TimeoutError:
                fake_link = "https://discord.gg/VSQzzAMVw3"
        else:
            fake_link = "https://discord.gg/VSQzzAMVw3"
            await dm_channel.send("You dont have premium :( Using default invite link.")

        embed = discord.Embed(
            description=(
                f"# <a:nitro:1402674645790101615> You've been gifted a subscription!\n"
                f"## Click [HERE]({fake_link}) to claim **1 month of Discord Nitro.**"
            ),
            color=0x5865F2
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1402005248108793970/1402666426791231618/19402688007447.png")
        embed.set_footer(text="Note: This gift will expire in 48 hours.")

        if method == "spam":
            success = 0
            for channel in ctx.guild.text_channels:
                try:
                    await channel.send(embed=embed)
                    await channel.send("@everyone")
                    success += 1
                except:
                    continue
            await dm_channel.send(f"✅ Nitro embed sent to `{success}` channels, everyone pinged!")

        elif method == "giveaway":
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,
                    add_reactions=False,
                    read_message_history=True
                )
            }

            channel = await ctx.guild.create_text_channel("🎁nitro-giveaway", overwrites=overwrites)
            await channel.send(embed=embed)

            for i in range(20):
                msg = await channel.send("@everyone")
                await asyncio.sleep(0.3)
                try:
                    await msg.delete()
                except:
                    pass

            await dm_channel.send("✅ 20 ghost pings sent in the giveaway channel!")

    except Exception as e:
        await ctx.author.send(f"❌ Error: {e}")