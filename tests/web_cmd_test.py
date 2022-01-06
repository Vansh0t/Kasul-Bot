import pytest
import asyncio
import json
from bot_main import bot, BOT_TOKEN
import web_cmd
from data import guild_data

DEV_GUILD_ID = None
DEV_VOICE_CHANNEL = None
YOUTUBE_VIDEO_URL = None
dev_guild_web_id = None

def is_bot_response_success(resp):
    if isinstance(resp, str): 
        resp = json.loads(resp)
    if resp['type'] == 'result':
        return True
    return False

@pytest.fixture
def event_loop():
    loop = bot.loop
    yield loop
    

#@pytest.mark.asyncio
#async def test():
#    print('Test')
#    await asyncio.sleep(1)
#    return False

@pytest.mark.asyncio
async def tests(event_loop):
    bot.loop.create_task(bot.start(BOT_TOKEN))
    #wait for bot cache
    await bot.wait_until_ready()
    #wait for on_ready() event init
    await asyncio.sleep(1)
    
    dev_guild_web_id = guild_data[DEV_GUILD_ID].web_id

    cmd = await web_cmd.process_cmd('get_queue', {'web_id':dev_guild_web_id})
    assert is_bot_response_success(cmd)

    cmd = await web_cmd.process_cmd('get_cur_audio', {'web_id':dev_guild_web_id})
    assert is_bot_response_success(cmd)

    cmd= await web_cmd.process_cmd('play', {'web_id':dev_guild_web_id, 'url':YOUTUBE_VIDEO_URL, 'dev_voice_id': DEV_VOICE_CHANNEL})
    assert is_bot_response_success(cmd)
    await asyncio.sleep(4)

    cmd= await web_cmd.process_cmd('skip', {'web_id':dev_guild_web_id, 'url':YOUTUBE_VIDEO_URL, 'dev_voice_id': DEV_VOICE_CHANNEL})
    assert is_bot_response_success(cmd)

    cmd= await web_cmd.process_cmd('queue', {'web_id':dev_guild_web_id, 'url':YOUTUBE_VIDEO_URL, 'dev_voice_id': DEV_VOICE_CHANNEL})
    assert is_bot_response_success(cmd)
    await asyncio.sleep(3)

    cmd= await web_cmd.process_cmd('pause', {'web_id':dev_guild_web_id, 'url':YOUTUBE_VIDEO_URL, 'dev_voice_id': DEV_VOICE_CHANNEL})
    assert is_bot_response_success(cmd)
    await asyncio.sleep(2)

    cmd= await web_cmd.process_cmd('resume', {'web_id':dev_guild_web_id, 'url':YOUTUBE_VIDEO_URL, 'dev_voice_id': DEV_VOICE_CHANNEL})
    assert is_bot_response_success(cmd)
    await asyncio.sleep(2)



#def run_bot(loop):
#    try:
#        loop.run_until_complete(bot.start(BOT_TOKEN))
#    except KeyboardInterrupt:
#        loop.run_until_complete(bot.close())
#    finally:
#        loop.close()
    

#bot.loop.create_task(tests(event_loop))
#bot.run(BOT_TOKEN)