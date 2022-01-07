import uuid
from utils import get_time_now, get_timedelta_since, get_timedelta_zero
from math import floor
from discord.utils import find
import os
from json import dump, load


QUEUE_MAX_SIZE = 100

guild_data = {}




class AudioData():
    url :str = None 
    url_internal:str = None
    title:str = None
    length:int = None
    time_offset:int = 0
    def __init__(self, url, url_internal, title, length, time_offset = 0) -> None:
        self.url = url
        self.url_internal=url_internal
        self.title = title
        self.length = length
        self.time_offset = time_offset
    def web_format(self):
        return (self.url, self.title)
    def to_json(self):
        return {'url':self.url, 'title':self.title, 'length': self.length}
        

class GuildData:
    is_queue_persistent = True
    __audio_queue = []
    id = -1
    cur_audio : AudioData = None
    audio_player = None
    audio_started = None
    audio_paused_last = None
    audio_paused_sum = get_timedelta_zero()
    audio_length = 0
    audio_offset = 0
    autoplay_next = True
    web_id:str
    bot = None
    def __init__(self, guild_id, bot):
        self.id = guild_id
        self.web_id = uuid.uuid4().hex
        self.bot = bot
    def queue_append(self, audio_data:AudioData):
        if len(self.__audio_queue) >= QUEUE_MAX_SIZE:
            raise QueueSizeMax()
        #the last audio is already playing, insert new right before it
        if len(self.__audio_queue)>0 and self.cur_audio and self.cur_audio.title == self.__audio_queue[-1].title:
            self.__audio_queue.insert(-1, audio_data)
        else:
            self.__audio_queue.append(audio_data)
        self.store_queue()
    def queue_insert(self, audio_data):
        if len(self.__audio_queue) >= QUEUE_MAX_SIZE:
            raise QueueSizeMax()
        self.__audio_queue.insert(0, audio_data)
        self.store_queue(self)
    def queue_move(self, audio_data:AudioData, index):
        if audio_data in self.__audio_queue:
            from_index = self.__audio_queue.index(audio_data)
            audio_data = self.__audio_queue.pop(from_index)
            self.__audio_queue.insert(index, audio_data)
            self.store_queue()
    def queue_move_index(self, from_index, to_index):
        if from_index == to_index:
            return
        audio_data = self.__audio_queue.pop(from_index)
        self.__audio_queue.insert(to_index, audio_data)
        self.store_queue()
    def queue_remove_index(self, from_index):
        self.__audio_queue.pop(from_index)
        self.store_queue()
    def queue_advance(self):
        self.cur_audio = None
        if len(self.__audio_queue) == 0:
            raise QueueIsEmpty()
        first_audio = self.__audio_queue.pop(0)
        self.cur_audio = first_audio
        self.__audio_queue.append(first_audio)
        self.store_queue()
        return first_audio
    def queue_back(self):
        
        if len(self.__audio_queue) == 0:
            raise QueueIsEmpty()
        last_audio = self.__audio_queue.pop()
        if last_audio.title == self.cur_audio.title:
            self.queue_insert(last_audio)
        last_audio = self.__audio_queue[-1]
        self.cur_audio = last_audio
        self.store_queue()
        return last_audio
    def queue_clear(self):
        self.__audio_queue.clear()
        self.store_queue()
    def get_queue(self):
        return self.__audio_queue.copy()
    def get_queue_json(self):
        return list(map(lambda o: o.to_json(), self.__audio_queue))
    def get_queue_len(self):
        return len(self.__audio_queue)
    #transfer cur_audio init here
    def set_audio_started(self, audio_data, sec_offset=0):
        self.cur_audio = audio_data
        self.audio_started = get_time_now()
        self.audio_paused_last = None
        self.audio_paused_sum = get_timedelta_zero()
        self.audio_length = audio_data.length
        self.audio_offset = sec_offset
    def set_audio_stopped(self):
        self.audio_started = None
        self.audio_paused_last = None
        self.cur_audio = None
        self.audio_paused_last = None
        self.audio_paused_sum = get_timedelta_zero()
        self.audio_length = 0
        self.audio_offset = 0
    def set_audio_paused(self):
        self.audio_paused_last = get_time_now()
    def set_audio_resumed(self):
        if self.audio_paused_last is None:
            return
        self.audio_paused_sum+= get_timedelta_since(self.audio_paused_last) 
        self.audio_paused_last = None
    def get_playtime(self):
        playtime = (get_time_now(self.audio_offset) - self.audio_started - self.audio_paused_sum).total_seconds()
        playtime = floor(playtime)
        return playtime if self.audio_started is not None else None
    def get_cur_audio_web(self):
        return self.cur_audio.web_format() if self.cur_audio else None
    def get_audio_player(self, handler):
        from AudioPlayer import AudioPlayer
        if not self.audio_player:
            self.audio_player = AudioPlayer(self.bot, self, handler)
        return self.audio_player
    def store_queue(self):
        if self.is_queue_persistent:
            if not os.path.exists('guild_data'):
                os.mkdir('guild_data')
            with open(os.path.join('guild_data', f'g_{self.id}.json'), 'w+') as f:
                dump(self.get_queue_json(), f, indent=4, ensure_ascii=False)
    def load_queue(self):
        if self.is_queue_persistent:
            if os.path.exists(os.path.join('guild_data', f'g_{self.id}.json')):
                with open(os.path.join('guild_data', f'g_{self.id}.json'), 'r') as f:
                    queue = load(f)
                    for x in queue:
                        self.__audio_queue.append(AudioData(x['url'], None, x['title'], x['length']))
    



class QueueSizeMax(Exception):
    pass

class QueueIsEmpty(Exception):
    pass

def get_guild_data(guild_id)->GuildData:
    return guild_data[guild_id]

def get_guild_data_web(guild_web_id)->GuildData:
    return find(lambda x: x.web_id == guild_web_id, guild_data.values())




