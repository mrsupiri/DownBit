import spotipy
import youtube_dl
import eyed3
from urllib.request import urlretrieve as download
from DownBit import *

sp = spotipy.Spotify(auth='')

results = sp.user_playlist_tracks('4G9wQldgTi2uWuI2i2yaWQ', '37i9dQZF1DXdxcBWuJkbcy')
tracks = results['items']
while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])

for i,item in enumerate(tracks):
    track = item['track']
    vid = track['id']
    track_name = track['name']
    artist_name = track['artists'][0]['name']
    album_name = track['album']['name']
    album_artist = track['album']['artists'][0]['name']
    image = track['album']['images'][0]['url']
    release_date = track['album']['release_date']
    print("{} - {} - {}".format(i, artist_name, track_name))
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'default_search': 'auto',
            'noplaylist': True,
            'source_address': '0.0.0.0',
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            data_ = ydl.extract_info("ytsearch:{} {} lyrics".format(artist_name, track_name),
                                     download=False)

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'outtmpl': '/root/Music/{} - {} [%(id)s].%(ext)s'.format(safe_filename(artist_name),
                                                                     safe_filename(track_name)),
            'continuedl': True,
            'default_search': 'auto',
            'noplaylist': True,
            'source_address': '0.0.0.0',
            'noprogress': True
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(data_['entries'][0]['webpage_url'])
            path = ydl.prepare_filename(data)

        if not os.path.exists(path):
            path = '.'.join(path.split('.')[:-1]) + '.mp3'
        if not os.path.exists(path):
            path = '.'.join(path.split('.')[:-1]) + '.acc'
        if not os.path.exists(path):
            path = '.'.join(path.split('.')[:-1]) + '.wav'

        if not os.path.exists(path):
            print('Audio File was not found')
            print('{}, {}, {}, {}, {}, {}, {}, {}'.format(vid, track_name, artist_name, album_name,
                                                          album_artist, image, album_artist,
                                                          release_date))
            continue

        dl_dir = "/tmp/{}-{}.jpg".format(safe_filename(track_name), safe_filename(artist_name))
        download(image, dl_dir)
        audio_file = eyed3.load(path)
        audio_file.tag.artist = u"{}".format(artist_name)
        audio_file.tag.album = u"{}".format(album_name)
        audio_file.tag.album_artist = u"{}".format(album_artist)
        audio_file.tag.title = u"{}".format(track_name)
        audio_file.tag.release_date = u"{}".format(release_date)
        audio_file.tag.images.set(3, open(dl_dir, "rb").read(), "image/jpeg", u"")
        audio_file.tag.save()

    except Exception as e:
        print(e)
