from data import GuildData
from time import sleep




def test_get_playtime():
    g_data = GuildData(0)
    g_data.set_audio_started(120)
    sleep(2)
    g_data.set_audio_started(120, 25)
    sleep(2)
    g_data.set_audio_paused()
    sleep(2)
    g_data.set_audio_resumed()
    sleep(2)
    assert g_data.get_playtime() == 29