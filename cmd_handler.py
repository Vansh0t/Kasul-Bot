import asyncio
from discord.ext.commands import Context
from data import get_guild_data, QueueIsEmpty, AudioData
from discord_slash.utils.manage_commands import create_option
from utils import get_yt_data_async
from logging import exception
from configparser import ConfigParser

dev_guild_ids = None
dev_urls = None

try:
    dev_config = ConfigParser()
    dev_config.read('dev_config.ini')
    dev_guild_ids = [int(x) for x in dev_config['DEV']['Guilds'].split(',')]
    dev_urls = dev_config['DEV']['Videos'].split(',')
except:
    pass




def init_commands(slash, bot):

    async def _join_channel(ctx: Context):
        if(ctx.voice_client is None):
            try:
                await ctx.author.voice.channel.connect()
                await ctx.send("Hi!")
                return True
            except Exception as e:
                exception('message')
                return False
        return True
        
    @slash.slash(name="ping",
                description="Sends ping to test bot's condition",
                #guild_ids = dev_guild_ids
                )
    async def ping(ctx: Context):
        await ctx.send('pong')
    @slash.slash(name="play",
                description="Priority fast play audio from url. Doesn't add to the queue.",
                #guild_ids = dev_guild_ids,
                options=[
                    create_option(
                      name="url",
                      description="Youtube video url.",
                      option_type=3,
                      required=True
                    )
                ],
                )
    async def play(ctx: Context, url):
        try:
            if await _join_channel(ctx) == False:
                await ctx.send('Unable to join the voice channel') 
                return
            g_data = get_guild_data(ctx.guild.id)
            a_player = g_data.get_audio_player(ctx)
            a_player.ensure_context(ctx)
            await a_player.stop_audio(False)
            audio_data = await a_player.play_from_url(url)
            g_data.queue_move(g_data.cur_audio, 0)
            g_data.set_audio_started(audio_data, audio_data.time_offset)
        except Exception as e:
            exception('message')
            await ctx.send("Unable to execute command!")
    @slash.slash(name="enqueue",
                description="Add an audio from url to the queue. If queue was empty starts playing.",
                options=[
                    create_option(
                      name="url",
                      description="Youtube video url.",
                      option_type=3,
                      required=True
                    )
                ],
                #guild_ids = dev_guild_ids
                )
    async def enqueue(ctx: Context, url):
        try:
            if await _join_channel(ctx) == False:
                await ctx.send('Unable to join voice channel') 
                return
            g_data = get_guild_data(ctx.guild.id)
            msg = await ctx.send('Requesting audio data...')
            url_internal, title, length = await get_yt_data_async(url)
            audio_data = AudioData(url, url_internal, title, length)
            g_data.queue_append(audio_data)
            await msg.edit(content=f'**{title}** added to the queue')
            if (g_data.get_queue_len()==1 and g_data.cur_audio == None):
                a_player = g_data.get_audio_player(ctx)
                a_player.ensure_context(ctx)
                audio_data = await a_player.play_from_url(url, audio_data=audio_data)
                g_data.set_audio_started(audio_data, audio_data.time_offset)
        except Exception as e:
            exception('message')
            await ctx.send("Unable to execute command!")
    @slash.slash(name="join",
                description="Join the bot to the voice channel of the caller.",
                #guild_ids = dev_guild_ids
                )
    async def join(ctx: Context):
        if await _join_channel(ctx) == False:
            await ctx.send('Unable to join the voice channel.')  
        else:
            #apply context for web controls
            g_data = get_guild_data(ctx.guild.id)
            g_data.get_audio_player(ctx)
            q_len = g_data.get_queue_len()
            if q_len:   
                await ctx.send('Audio queue is loaded. You can /resume it now.')
    @slash.slash(name="leave",
                description="Disconnect the bot from the voice channel.",
                #guild_ids = dev_guild_ids
                )
    async def leave(ctx: Context):
        try:
            await ctx.voice_client.disconnect()
            await ctx.send("Bye!")
        except Exception as e:
            exception('message')
            await ctx.send("Not in the channel!")
    @slash.slash(name="resume",
                description="Resume paused audio or start playing the first from the queue.",
                #guild_ids = dev_guild_ids
                )
    async def resume(ctx: Context):
        try:
            if await _join_channel(ctx) == False:
                await ctx.send('Unable to join the voice channel.')  
            g_data = get_guild_data(ctx.guild.id)
            if ctx.voice_client.is_paused():
                ctx.voice_client.resume()
                g_data.set_audio_resumed()
                await ctx.send('Resumed')
            elif not ctx.voice_client.is_playing():
                a_player = g_data.get_audio_player(ctx)
                a_player.ensure_context(ctx)
                if not g_data.cur_audio:
                    g_data.queue_advance()
                audio_data = await a_player.play_from_url(g_data.cur_audio.url)
                g_data.set_audio_started(audio_data, audio_data.time_offset)
            else:
                await ctx.send("Nothing to resume")
        except Exception as e:
            exception('message')
            await ctx.send("Unable to execute command!")
    @slash.slash(name="pause",
                description="Pause the currently playing audio.",
                #guild_ids = dev_guild_ids
                )
    async def pause(ctx: Context):
        try:
            if ctx.voice_client.is_playing():
                ctx.voice_client.pause()
                g_data = get_guild_data(ctx.guild.id)
                g_data.set_audio_paused()
                await ctx.send('Paused')
            else:
                ctx.send("Nothing to pause")
        except Exception as e:
            exception('message')
            await ctx.send("Unable to execute command!")
    @slash.slash(name="skip",
                description="Skip the currently playing audio.",
                #guild_ids = dev_guild_ids
                )
    async def skip(ctx: Context):
        try:
            g_data = get_guild_data(ctx.guild.id)
            a_player = g_data.get_audio_player(ctx)
            await a_player.stop_audio(True)
            await ctx.send('Skipped')
        except QueueIsEmpty:
            await ctx.send('Skipped')
        except Exception as e:
            exception('message')
            await ctx.send("Unable to execute command!")
    @slash.slash(name="back",
                description="Play previous audio from the queue.",
                #guild_ids = dev_guild_ids
                )
    async def back(ctx: Context):
        try:
            g_data = get_guild_data(ctx.guild.id)
            a_player = g_data.get_audio_player(ctx)
            await a_player.stop_audio(False)
            g_data.queue_back()
            await ctx.send('Playing previous')
            await a_player.play_from_url(g_data.cur_audio.url, audio_data=g_data.cur_audio)
        except QueueIsEmpty:
            await ctx.send('Queue is empty')
        except Exception as e:
            exception('message')
            await ctx.send("Unable to execute command!")

    @slash.slash(name="clear_queue",
                description="Clear the queue. Doesn't stop currently playing audio. To clear with stop use stop_clear_queue",
                #guild_ids = dev_guild_ids
                )
    async def clear_queue(ctx: Context):
        try:
            g_data = get_guild_data(ctx.guild.id)
            g_data.queue_clear()
            await ctx.send('Queue cleared')
        except Exception as e:
            exception('message')
            await ctx.send("Unable to execute command!")
    
    @slash.slash(name="stop_clear_queue",
                description="Clear the queue and stop any playing audio.",
                #guild_ids = dev_guild_ids
                )
    async def stop_clear_queue(ctx: Context):
        try:
            g_data = get_guild_data(ctx.guild.id)
            g_data.queue_clear()
            g_data.cur_audio = None
            ctx.voice_client.stop()
            await ctx.send('Queue stopped and cleared')
        except Exception as e:
            exception('message')
            await ctx.send("Unable to execute command!")

    @slash.slash(name="list_queue",
                description="Shows the current queue.",
                #guild_ids = dev_guild_ids
                )
    async def list_queue(ctx: Context):
        try: 
            g_data = get_guild_data(ctx.guild.id)
            now_playing = f'{g_data.cur_audio.title} | {g_data.cur_audio.url}' if g_data.cur_audio else 'Nothing'
            reply = f'Now playing: {now_playing}\n'
            counter = 0
            for audio in g_data.get_queue():
                counter+=1
                reply += f'{counter}. **{audio.title}** | {audio.url}\n'
            await ctx.send(reply)
        except Exception as e:
            exception('message')
            await ctx.send("Unable to execute command!")
    @slash.slash(name="keep_queue",
                description="Should the audio queue be kept after bot leaves a channel",
                options=[
                    create_option(
                      name="bool_value",
                      description="Keep the queue?",
                      option_type=5,
                      required=True
                    )
                ],
                guild_ids = dev_guild_ids
                )
    async def keep_queue(ctx: Context, bool_value):
        try: 
            g_data = get_guild_data(ctx.guild.id)
            g_data.is_queue_persistent = bool_value
            await ctx.send(f"Keep queue set to {bool_value}")
        except Exception as e:
            exception('message')
            await ctx.send("Unable to execute command!")
    @slash.slash(name="web",
                description="Get url from web controls",
                #guild_ids = dev_guild_ids
                )
    async def web(ctx: Context):
        try: 
            g_data = get_guild_data(ctx.guild.id)
            from web_cmd import web_url
            if not web_url:
                await ctx.send("Web controls url not found. Did you launch web controls?")
                return
            if not await _join_channel(ctx):
                await ctx.send("Unable to join your voice channel. It is required in order to use web controls")
                return
            await ctx.send(f"Web controls url: {web_url}/{g_data.web_id}")
        except Exception as e:
            exception('message')
            await ctx.send("Unable to execute command!")
    if dev_guild_ids:
        @slash.slash(name="dev_fill_queue",
                    description="Fill queue for development",
                    guild_ids=dev_guild_ids,
                    )
        async def dev_fill_queue(ctx: Context):
            try: 
                for url in dev_urls:
                    await enqueue.invoke(ctx, url)
                    await asyncio.sleep(0.5)
                await web.invoke(ctx)
            except Exception as e:
                exception('message')
                await ctx.send("Unable to execute command!")


        