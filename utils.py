import asyncio
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta, timezone
from sys import platform
from json import loads



def get_working_dir():
    import sys
    import os.path as path
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        app_path = sys._MEIPASS
    else:
        app_path = path.dirname(path.abspath(__file__))
    print(app_path)
    return app_path

#def get_yt_data(url):
#    yt = YouTube(url)
#    vid = yt.streams.filter(only_audio=True, audio_codec='opus').last()
#    url_internal = vid.url
#    return url_internal, yt.title, yt.length

async def get_yt_data_async(url):
    proc_exe = None
    if platform=='win32':
        proc_exe='win\\yt_utils.exe'
    else:
        proc_exe='linux/yt_utils'
    proc = await asyncio.create_subprocess_exec(
        proc_exe, url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if stdout:
        stdout_dec = loads(stdout)
        #print(f'Got subprocess stdout - {stdout_dec}')
        return tuple(stdout_dec.values())
    if stderr:
        stderr_dec = stderr.decode()
        print(f'Got yt_utils stderr - {stderr_dec}')
        return None
    #loop = get_running_loop()
    #prevents audio stream staggering when making blocking http, but youtube requests take more time due to process management
    #return await loop.run_in_executor(PROCESS_POOL_EXEC, partial(get_yt_data, url))

def get_yt_timecode(url):
    parsed_url = urlparse(url)
    parsed_query = parse_qs(parsed_url.query)
    if('t' in parsed_query):
        timecode = int(parse_qs(parsed_url.query)['t'][0].replace('s',''))
        return timecode
    return 0

def seconds_to_time(sec):
    if(sec is None):
        return '00:00:00'
    time_string = '{:02}:{:02}:{:02}'.format(sec // 3600, sec % 3600 // 60, sec % 60)
    return str(time_string)

def get_time_now(sec_offset=0):
    return datetime.now(timezone.utc) + timedelta(seconds=sec_offset)

def get_timedelta_since(since: datetime):
    return get_time_now() - since if since is not None else get_time_now()

def get_timedelta_zero():
    return timedelta()