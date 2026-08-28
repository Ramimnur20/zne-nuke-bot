from config import TOKEN
from core.bot import bot

if __name__ == "__main__":
    bot.remove_command("help")
    bot.run(TOKEN)
###############################