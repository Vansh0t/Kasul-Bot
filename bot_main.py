from discord.ext.commands import Bot
from discord_slash import SlashCommand
from event_handler import init_events
from cmd_handler import init_commands
from web_cmd import set_bot
from local_bridge import local_server
from configparser import ConfigParser

bot = Bot('/')
slash = SlashCommand(bot, sync_commands=True)
init_events(bot)
init_commands(slash, bot)
set_bot(bot)





BOT_TOKEN = 'OTE5NTYyNDE5OTY0MTA4ODcy.YbXnPQ.fBHxjaiVBuc6xnXahqbzeD9_kks'



if __name__ == "__main__":
   parser = ConfigParser()
   parser.read('config.ini')
   ip = parser['LOCAL_SERVER']['Ip']
   port = parser['LOCAL_SERVER']['Port']
   bot.loop.create_task(local_server(ip, port))
   bot.run(BOT_TOKEN)