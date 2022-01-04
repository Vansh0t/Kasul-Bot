import asyncio
from discord.ext.commands import Context
from data import get_guild_data, GuildData, QueueIsEmpty, AudioData
from discord_slash.utils.manage_commands import create_option
from utils import get_yt_data_async


dev_guild_ids = [919591541914353714, 598571406753660929, 927208182609219664]
dev_urls = ['https://www.youtube.com/watch?v=20sIhZLVJR4', 'https://www.youtube.com/watch?v=uxfoa23skHg', 'https://www.youtube.com/watch?v=2YTBgFmK_bs']



def init_commands(slash, bot):

    async def _join_channel(ctx: Context):
        if(ctx.voice_client is None):
            try:
                await ctx.author.voice.channel.connect()
                await ctx.send("Yo, KASULS!")
                return True
            except Exception as e:
                print(e)
                return False
        return True
        
    @slash.slash(name="ping",
                description="Sends ping to test bot's condition",
                guild_ids=dev_guild_ids,
                )
    async def ping(ctx: Context):
        await ctx.send('pong')
    @slash.slash(name="play",
                description="Priority fast play audio from url. Doesn't add to the queue.",
                options=[
                    create_option(
                      name="url",
                      description="Youtube video url.",
                      option_type=3,
                      required=True
                    )
                ],
                guild_ids=dev_guild_ids,
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
            print(e)
            await ctx.send("OOOPS, somebody is KASUL!")
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
                guild_ids=dev_guild_ids,
                )
    async def enqueue(ctx: Context, url):
        try:
            if await _join_channel(ctx) == False:
                await ctx.send('Unable to join voice channel') 
                return
            g_data = get_guild_data(ctx.guild.id)
            url_internal, title, length = await get_yt_data_async(url)
            #yt = YouTube(url)
            #vid = yt.streams.filter(only_audio=True, audio_codec='opus').last()
            #title = yt.title
            #length = yt.length
            audio_data = AudioData(url, url_internal, title, length)
            g_data.queue_append(audio_data)
            await ctx.send('Added to the queue')
            if (g_data.get_queue_len()==1 and g_data.cur_audio == None):
                a_player = g_data.get_audio_player(ctx)
                a_player.ensure_context(ctx)
                audio_data = await a_player.play_from_url(url)
                g_data.set_audio_started(audio_data, audio_data.time_offset)
        except Exception as e:
            print(e)
            await ctx.send("OOOPS, somebody is KASUL!")
    @slash.slash(name="join",
                description="Join the bot to the voice channel of the caller.",
                guild_ids=dev_guild_ids,
                )
    async def join(ctx: Context):
        if await _join_channel(ctx) == False:
            await ctx.send('Unable to join the voice channel. You are a KASUL.')  
        else:
            #apply context for web controls
            g_data = get_guild_data(ctx.guild.id)
            g_data.get_audio_player(ctx)
    @slash.slash(name="leave",
                description="Disconnect the bot from the voice channel.",
                guild_ids=dev_guild_ids,
                )
    async def leave(ctx: Context):
        try:
            await ctx.voice_client.disconnect()
            await ctx.send("Bye, KASULS!")
        except Exception as e:
            print(e)
            await ctx.send("I'm not in the channel, you damn KASUL!")
    @slash.slash(name="resume",
                description="Resume paused audio.",
                guild_ids=dev_guild_ids,
                )
    async def resume(ctx: Context):
        try:
            if ctx.voice_client.is_paused():
                ctx.voice_client.resume()
                g_data = get_guild_data(ctx.guild.id)
                g_data.set_audio_resumed()
                await ctx.send('Resumed')
            else:
                await ctx.send("Nothing to resume")
        except Exception as e:
            print(e)
            await ctx.send("OOOPS, somebody is KASUL!")
    @slash.slash(name="pause",
                description="Pause the currently playing audio.",
                guild_ids=dev_guild_ids,
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
            print(e)
            await ctx.send("OOOPS, somebody is KASUL!")
    @slash.slash(name="skip",
                description="Skip the currently playing audio.",
                guild_ids=dev_guild_ids,
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
            print(e)
            await ctx.send("OOOPS, somebody is KASUL!")
    @slash.slash(name="back",
                description="Play previous audio from the queue.",
                guild_ids=dev_guild_ids,
                )
    async def back(ctx: Context):
        try:
            g_data = get_guild_data(ctx.guild.id)
            a_player = g_data.get_audio_player(ctx)
            await a_player.stop_audio(False)
            g_data.queue_back()
            await a_player.play_from_url(g_data.cur_audio.url, audio_data=g_data.cur_audio)
            await ctx.send('Playing previous')
        except QueueIsEmpty:
            await ctx.send('Queue is empty')
        except Exception as e:
            print(e)
            await ctx.send("OOOPS, somebody is KASUL!")

    @slash.slash(name="clear_queue",
                description="Clear the queue. Doesn't stop currently playing audio. To clear with stop use stop_clear_queue",
                guild_ids=dev_guild_ids,
                )
    async def clear_queue(ctx: Context):
        try:
            g_data = get_guild_data(ctx.guild.id)
            g_data.queue_clear()
            await ctx.send('Queue cleared')
        except Exception as e:
            print(e)
            await ctx.send("OOOPS, somebody is KASUL!")
    
    @slash.slash(name="stop_clear_queue",
                description="Clear the queue and stop any playing audio.",
                guild_ids=dev_guild_ids,
                )
    async def stop_clear_queue(ctx: Context):
        try:
            g_data = get_guild_data(ctx.guild.id)
            g_data.queue_clear()
            g_data.cur_audio = None
            ctx.voice_client.stop()
            await ctx.send('Queue stopped and cleared')
        except Exception as e:
            print(e)
            await ctx.send("OOOPS, somebody is KASUL!")

    @slash.slash(name="list_queue",
                description="Shows the current queue.",
                guild_ids=dev_guild_ids,
                )
    async def list_queue(ctx: Context):
        try: 
            g_data = get_guild_data(ctx.guild.id)
            now_playing = f'{g_data.cur_audio.title} | {g_data.cur_audio.url}' if g_data.cur_audio != None else 'Nothing'
            reply = f'Now playing: {now_playing}\n'
            counter = 0
            for audio in g_data.get_queue():
                counter+=1
                reply += f'{counter}. **{audio.title}** | {audio.url}\n'
            await ctx.send(reply)
        except Exception as e:
            print(e)
            await ctx.send("OOOPS, somebody is KASUL!")
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
                guild_ids=dev_guild_ids,
                )
    async def keep_queue(ctx: Context, bool_value):
        try: 
            g_data = get_guild_data(ctx.guild.id)
            g_data.is_queue_persistent = bool_value
            await ctx.send(f"Keep queue set to {bool_value}")
        except Exception as e:
            print(e)
            await ctx.send("OOOPS, somebody is KASUL!")
    @slash.slash(name="web",
                description="Get url from web controls",
                guild_ids=dev_guild_ids,
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
            print(e)
            await ctx.send("OOOPS, somebody is KASUL!")
    
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
            print(e)
            await ctx.send("OOOPS, somebody is KASUL!")


        