from flask import Flask,render_template,request,escape,send_from_directory,send_file #send_file,send_from_directory
import youtube_dl
import lyricsgenius as lg
import os
from spleeter.separator import Separator
from dotenv import load_dotenv
# from google.cloud import storage
# from keys import keys
# from boto.s3.connection import S3Connection

## use when running locally:
# load_dotenv()
# api_key = os.getenv('GENIUS_API_KEY')
##
# api_key = keys.get('GENIUS_API_KEY')
# api_key = GENIUS_API_KEY

## use when unning on google cloud:
api_key = os.environ.get('GENIUS_API_KEY', 'default value')
##
# s3 = S3Connection(os.environ['GENIUS_API_KEY'])
genius = lg.Genius(api_key)

# storage_client = storage.Client()
# bucket = storage_client.bucket(CLOUD_STORAGE_BUCKET)

app = Flask(__name__)


@app.route("/", methods=['GET'])
def index():
    yt_url = request.args.get("yt_url","")
    artist = request.args.get("artist","")
    song = request.args.get("song","")
    split_audio_tag=""

    if yt_url:
        split_audio_tag = youtube_to_split_audio(yt_url)
        print('split audio tag:',split_audio_tag)

    if artist and song:
        lyrics = getlyrics(artist,song) ###

    else:
        lyrics = ""

    return ("""<form action="" method="get">
                Artist: <input type="text" name="artist">
                Song: <input type="text" name="song">
                YouTube URL: <input type="text" name="yt_url">
                <input type="submit" value="Go">
              </form>"""+"Lyrics: "+lyrics+split_audio_tag) #+ split_audio_tag)


def getlyrics(artist,song):
    try:
        artist = genius.search_artist(artist, max_songs=1)
        song = artist.song(song)
        return song.lyrics
    except:
        return "invalid input"


def youtube_to_split_audio(yt_url):
    # video_url = input("please enter youtube video url:")
    video_info = youtube_dl.YoutubeDL().extract_info(
        url = yt_url,download=False
        )
    filename = f"{video_info['title']}.mp3"
    options={
        'format': 'bestaudio/best',
        # 'quality': 7,
        'keepvideo':False,
        ### use when running locally
        # 'outtmpl':'./static/yt_mp3/'+filename,
        ###
        ### use when running on google
        'outtmpl':'/tmp/yt_mp3/'+filename
        # 'outtmpl':'/tmp/yt_mp3/'+filename
        ###
    }

    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])

    def split_vocals(mp3):
        separator = Separator('spleeter:2stems')
        ### use when running locally
        # separator.separate_to_file('./static/yt_mp3/'+mp3,
        #                             './static/split_audio/'+mp3)
        ### use when running on google
        separator.separate_to_file('/tmp/yt_mp3/'+mp3,
                                    '/tmp/split_audio/'+mp3)
        ###
    split_vocals(filename)

    ### use when running locally
    # filepath = './static/split_audio/'+filename+'/'+filename[:-4]+'/accompaniment.wav'
    ### use when running locally
    ###
    filepath = '/tmp/split_audio/'+filename+'/'+filename[:-4]+'/accompaniment.wav'
    ###
    global split_audio_tag
    split_audio_tag = '<audio controls> <source src="'+filepath+'" type="audio/wav"> </audio>'
    print('audio tag:',split_audio_tag)
    return split_audio_tag



if __name__ == "__main__":
    # load_dotenv()
    # app.run()
    # app.run(host="0.0.0.0", debug=True)
    app.run(host="127.0.0.1", port=8080, debug=True)
