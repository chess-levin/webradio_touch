import vlc
import time

def getData(url):
    Instance = vlc.Instance()
    player = Instance.media_player_new()
    Media = Instance.media_new(url)
    Media.get_mrl()
    player.set_media(Media)
    player.play()
    prev = ""
    while True:
        time.sleep(1)
        m = Media.get_meta(12) # vlc.Meta 12: 'NowPlaying',
        if m != prev:
            print("Now playing", m)
            prev = m
    return player.audio_get_track_description()

print(getData("http://icecast.radiobremen.de/rb/bremeneins/live/mp3/128/stream.mp3"))