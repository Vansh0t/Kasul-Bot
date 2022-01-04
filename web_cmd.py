from data import get_guild_data_web, QueueIsEmpty, AudioData, GuildData
from discord.utils import find
from utils import get_yt_data_async
from math import floor
import logging
import json

ROOT_ACCESS_SECRET = 'OkS1vGLyJBwokfat606CqNmqHBNZlfIy'
web_url = ''

bot = None

def set_bot(bot_):
    global bot
    bot = bot_

def get_context(web_id):
    g_data = get_guild_data_web(web_id)
    vc = find(lambda x: x.guild.id == g_data.id, bot.voice_clients)
    if not vc:
        raise Exception("Voice channel is not found")
    a_player = g_data.get_audio_player(vc)
    return g_data, a_player, vc

async def set_url(args):
    try:
        global web_url
        print(args)
        web_url = args['web_url']
        
        return json.dumps({'type':'result', 'data':{}})
    except Exception as e:
        print(e)
        return json.dumps({'type':'error', 'data':{}})

async def set_play_pos(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        pos = floor(int(args['pos'])) 
        audio_data = g_data.cur_audio
        await a_player.stop_audio(False)
        await a_player.play_from_url(audio_data.url, None, audio_data, time_pos=pos, silent=True)
        g_data.set_audio_started(audio_data, pos)
        result = json.dumps({'type':'result', 'data':{'playtime': g_data.get_playtime(), 'length':audio_data.length}})
        return result
    except Exception as e:
        print(e)
        error = json.dumps({'type':'error', 'message':'Unable to find voice channel. Invite with /join first'})
        return error

async def get_queue(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        #print(json.dumps({'type':'result', 'data':{'queue':g_data.get_queue()}}))
        result = json.dumps({'type':'result', 'data':{'queue':g_data.get_queue_json()}})
        return result
    except Exception as e:
        print(e)
        error = json.dumps({'type':'error', 'message':'Failed to find guild data'})
        return error

async def get_cur_audio(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        result = json.dumps({'type':'result', 'data':g_data.get_cur_audio_web()})
        return result
    except Exception as e:
        print(e)
        error = json.dumps({'type':'error', 'message':'Failed to find guild data'})
        return error

async def get_playing(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        result = json.dumps({'type':'result', 'data':{'cur_audio': g_data.get_cur_audio_web(),
                                                    'is_playing':vc.is_playing(), 
                                                    'is_paused':vc.is_paused(), 
                                                    'length':g_data.audio_length, 
                                                    'playtime':f'{g_data.get_playtime()}', 
                                                    'is_queue_persistent':g_data.is_queue_persistent}})
        return result
    except Exception as e:
        print(e)
        error = json.dumps({'type':'error', 'message':'Failed to find guild data'})
        return error

async def play(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        url = args['url']
        await a_player.stop_audio(False)
        audio_data= await a_player.play_from_url(url)
        g_data.queue_move(g_data.cur_audio, 0)
        g_data.set_audio_started(audio_data, audio_data.time_offset)
        result = json.dumps({'type':'result', 'data':{}})
        return result
    except Exception as e:
        print(e)
        error = json.dumps({'type':'error', 'message':'Unable to find voice channel. Invite with /join first'})
        return error

async def skip(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        await a_player.stop_audio(True)
        result = json.dumps({'type':'result', 'data':{'cur_audio':g_data.get_cur_audio_web(), 'length':g_data.cur_audio.length, 'queue':g_data.get_queue_json()}})
        return result
    except QueueIsEmpty as e:
        result = json.dumps({'type':'result', 'data':{'queue':[]}})
        return result
    except Exception as e:
        print(e)
        error = json.dumps({'type':'error', 'message':'Unable to skip'})
        return error

async def back(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        await a_player.stop_audio(False)
        g_data.queue_back()
        await a_player.play_from_url(g_data.cur_audio.url, audio_data=g_data.cur_audio)
        result = json.dumps({'type':'result', 'data':{'cur_audio':g_data.get_cur_audio_web(), 'length':g_data.cur_audio.length, 'queue':g_data.get_queue_json()}})
        return result
    except QueueIsEmpty as e:
        result = json.dumps({'type':'result', 'data':{'queue':[]}})
        return result
    except Exception as e:
        print(e)
        logging.exception('message')
        error = json.dumps({'type':'error', 'message':'Unable to skip'})
        return error

async def pause(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        vc.pause()
        g_data.set_audio_paused()
        result = json.dumps({'type':'result', 'data':f'{g_data.get_playtime()}'})
        return result
    except Exception as e:
        print(e)
        error = json.dumps({'type':'error', 'message':'Unable to skip'})
        return error

async def resume(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        vc.resume()
        g_data.set_audio_resumed()
        result = json.dumps({'type':'result', 'data':f'{g_data.get_playtime()}'})
        return result
    except Exception as e:
        print(e)
        error = json.dumps({'type':'error', 'message':'Unable to resume'})
        return error

async def enqueue(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        url = args['url']
        url_internal, title, length = await get_yt_data_async(url)
        audio_data = AudioData(url, url_internal, title, length)
        g_data.queue_append(audio_data)
        if (g_data.get_queue_len()==1 and g_data.cur_audio == None):    
            audio_data = await a_player.play_from_url(url, None, audio_data)
            g_data.set_audio_started(audio_data, audio_data.time_offset)
        result = json.dumps({'type':'result', 'data':{'queue':g_data.get_queue_json()}})
        return result
    except Exception as e:
        print(e)
        error = json.dumps({'type':'error', 'message':'Unable to find voice channel or youtube url is invalid. Invite with /join first'})
        return error

async def queue_move(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        from_index, to_index = args['from'], args['to']
        g_data.queue_move_index(from_index, to_index)
        result = json.dumps({'type':'result', 'data':{'queue':g_data.get_queue_json()}})
        return result
    except Exception as e:
        print(e)
        error = json.dumps({'type':'error', 'message':'Unable to execute command'})
        return error

async def queue_remove(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        from_index = args['from']
        g_data.queue_remove_index(from_index)
        result = json.dumps({'type':'result', 'data':{'queue':g_data.get_queue_json()}})
        return result
    except Exception as e:
        print(e)
        error = json.dumps({'type':'error', 'message':'Unable to execute command'})
        return error

async def queue_keep(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        value = args['value']
        g_data.is_queue_persistent = value
        result = json.dumps({'type':'result', 'data':{'is_queue_persistent':g_data.is_queue_persistent}})
        return result
    except Exception as e:
        print(e)
        error = json.dumps({'type':'error', 'message':'Unable to execute command'})
        return error

async def queue_clear(args):
    try:
        g_data, a_player, vc = get_context(args['web_id'])
        g_data.queue_clear()
        result = json.dumps({'type':'result', 'data':{'queue':g_data.get_queue_json()}})
        return result
    except Exception as e:
        print(e)
        error = json.dumps({'type':'error', 'message':'Unable to execute command'})
        return error

CMD_CALLBACKS = {
    'set_url': set_url,
    'get_queue': get_queue,
    'get_cur_audio': get_cur_audio,
    'play':play,
    'enqueue':enqueue,
    'skip':skip,
    'back':back,
    'pause':pause,
    'resume':resume,
    'get_playing':get_playing,
    'set_play_pos':set_play_pos,
    'queue_move':queue_move,
    'queue_remove':queue_remove,
    'queue_keep':queue_keep,
    'queue_clear':queue_clear
}

async def process_cmd(cmd, args):
    return await CMD_CALLBACKS[cmd](args)

    
