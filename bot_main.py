from discord.ext.commands import Bot
from discord_slash import SlashCommand
from event_handler import init_events
from cmd_handler import init_commands
from web_cmd import set_bot
from local_bridge import local_server
from configparser import ConfigParser
from discord.errors import LoginFailure

bot = Bot('/')
slash = SlashCommand(bot, sync_commands=True)
#print(slash.commands)
init_events(bot)
init_commands(slash, bot)
set_bot(bot)




if __name__ == "__main__":
   parser = ConfigParser()
   parser.read('config.ini')
   ip = parser['LOCAL_SERVER']['Ip']
   port = parser['LOCAL_SERVER']['Port']
   token = parser['BOT']['Token']
   if not token:
      import os.path
      if os.path.exists('dev_config.ini'):
         print('dev_config.ini found, using Bot Token from it')
         parser.read('dev_config.ini')
         token = parser['DEV']['Token']
      else:
         print('Unable to find bot token. Please, enter it:')
         token = input()
         if token:
            parser['BOT']['Token'] = token
            with open('config.ini', 'w') as config:
               parser.write(config)
   bot.loop.create_task(local_server(ip, port))
   try:
      bot.run(token)
   except LoginFailure as e:
      print(f'Failed to login with discord: {e}')
      print(f'Check if your bot token is valid in config.ini')
   