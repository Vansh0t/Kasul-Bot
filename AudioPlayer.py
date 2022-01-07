from discord.ext.commands import Context
from discord_slash import SlashContext
from data import GuildData, AudioData
from discord import FFmpegOpusAudio
from discord.voice_client import VoiceClient
from utils import get_yt_timecode, get_yt_data_async
from asyncio import sleep


async def _try_send(ctx:Context or None, msg: str):
    try:
        if ctx:
            await ctx.send(msg)
    except:
        pass

class AudioPlayer:
    vc = None
    ctx = None
    bot = None
    g_data = None
    def __init__(self, bot, guild_data:GuildData, handler:Context or VoiceClient):
        if type(handler) is SlashContext:
            self.ctx = handler
            self.vc = handler.voice_client
        elif handler:
            self.vc=handler
        else:
            raise Exception('Invalid handler passed')
        self.bot = bot
        self.g_data = guild_data
    async def _next(self):
        self.g_data.queue_advance()
        await self.play_from_url(self.g_data.cur_audio.url, None, self.g_data.cur_audio)
        self.g_data.set_audio_started(self.g_data.cur_audio, self.g_data.cur_audio.time_offset)
    def _create_after(self):
        return lambda error: self.bot.loop.create_task(self._after(error))
    async def _after(self, error=None):
        if error:
            await _try_send(self.ctx, 'An error occured while playing the audio')
        if self.g_data.autoplay_next:
            await self._next()
        else:
            self.g_data.autoplay_next = True
    async def play_from_url(self, url, after=None, audio_data:AudioData=None, time_pos = None, silent=False)->AudioData:
        #if await _join_channel(ctx) == False:
        #    ctx.send('Unable to join voice channel')
        ctx = self.ctx
        vc = self.vc
        timecode = time_pos if time_pos else get_yt_timecode(url)

        if not after:
            after = self._create_after()
        
        if(timecode is not None and timecode> 86399):
            await _try_send(ctx, "Timecode must be less than 24 hours")
            return

        if not audio_data or not audio_data.url_internal:
            url_internal, title, length = await get_yt_data_async(url)
            audio_data = AudioData(url, url_internal, title, length, timecode)
        
        opus_audio = await FFmpegOpusAudio.from_probe(audio_data.url_internal, before_options=f"-ss {timecode} -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
        vc.play(opus_audio, after = after)
        if not silent:
            await _try_send(ctx, 'Now playing: **' + audio_data.title + '**')
        return audio_data
    
    async def stop_audio(self, autoplay_next:bool):
        if not self.vc.is_playing():
            if autoplay_next:
                await self._next()
            return
        self.g_data.autoplay_next = autoplay_next
        self.vc.stop()
        #sleep to make sure _after() is fired
        await sleep(0.1)

    def ensure_context(self, ctx):
        self.ctx = ctx