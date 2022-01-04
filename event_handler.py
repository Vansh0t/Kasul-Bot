from data import guild_data, GuildData
from discord.utils import find




def init_events(bot):
    @bot.event
    async def on_ready():
        print("Ready. Initing queues...")
        for g in bot.guilds:
            guild_data[g.id]=GuildData(g.id, bot)
        print(str(len(bot.guilds))+" queues found")
    @bot.event
    async def on_guild_remove(guild):
        try:
            del guild_data[guild.id]
            print("Got removed from guild: " + str(guild.id))
        except Exception as e:
            print(e)
            pass
    @bot.event
    async def on_guild_join(guild):
        try:
            guild_data[guild.id] = GuildData(guild.id, bot)
            print("Successfully joined to guild: " + str(guild.id))
        except Exception as e:
            print(e)
            pass
    @bot.event
    async def on_voice_state_update(member, before, after):
        if member.id != bot.user.id:
            return
        g_id = member.guild.id
        g_data:GuildData = guild_data[g_id]
        
        if after.channel is None:
            print("left channel")
            if g_data.is_queue_persistent ==False:
                g_data.audio_queue.empty() 
            g_data.audio_player = None
            vc = find(lambda x: x.guild.id == g_id, bot.voice_clients)
            if vc:
                vc.cleanup()
        else:
            print("joined channel")

