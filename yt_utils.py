from pytube import YouTube
from sys import argv
from contextlib import redirect_stdout
from json import dumps

if len(argv)!=2:
    raise Exception('Youtube video url is required')

def get_yt_data(url):
    yt = YouTube(url)
    vid = yt.streams.filter(only_audio=True, audio_codec='opus').last()
    url_internal = vid.url
    return dumps({'url_internal':url_internal, 'title':yt.title, 'length':yt.length})

result = get_yt_data(argv[1])
print(result)