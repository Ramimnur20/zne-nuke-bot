import asyncio
import os

from config import BLACKLISTED_GUILD_ID, OWNER_ID, TOKEN
from core.bot import bot
from core.operation import leave_all_servers
from core.utils import is_premium_user


if __name__ == "__main__":
    bot.remove_command("help")
    bot.run(TOKEN)
