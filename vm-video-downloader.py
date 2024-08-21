import os
import sys
import base64
import requests
import subprocess
#For Windows:
#Download ffmpeg https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
#Put the script in the folder: C:\user\Downloads\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin
#For Linux:
#sudo apt install ffmpeg
#Run the script with: python vm-video-downloader.py
#Inspired by https://gist.github.com/alexeygrigorev/a1bc540925054b71e1a7268e50ad55cd?permalink_comment_id=5097364#gistcomment-5097364
#Script v0.1
from tqdm import tqdm

url = input('enter [master|playlist].json url: ')
file_name = input('enter output name: ')

if 'master.json' in url:
    url = url[:url.find('?')] + '?query_string_ranges=1'
    url = url.replace('master.json', 'master.mpd')
    print(url)
    subprocess.run(['youtube-dl', url, '-o', file_name])
    sys.exit(0)


def download(what, to, base):
    print('saving', what['mime_type'], 'to', to)
    with open(to, 'wb') as file:
        init_segment = base64.b64decode(what['init_segment'])
        file.write(init_segment)

        for segment in tqdm(what['segments']):
            segment_url = base + segment['url']
            resp = requests.get(segment_url, stream=True)
            if resp.status_code != 200:
                print('not 200!')
                print(segment_url)
                break
            for chunk in resp:
                file.write(chunk)
    print('done')


file_name += '.mp4'
base_url = url[:url.rfind('/', 0, -26) + 1]
content = requests.get(url).json()

vid_heights = [(i, d['height']) for (i, d) in enumerate(content['video'])]
vid_idx, _ = max(vid_heights, key=lambda _h: _h[1])

audio_quality = [(i, d['bitrate']) for (i, d) in enumerate(content['audio'])]
audio_idx, _ = max(audio_quality, key=lambda _h: _h[1])

video = content['video'][vid_idx]
audio = content['audio'][audio_idx]
base_url = base_url + content['base_url']

video_tmp_file = 'video.mp4'
audio_tmp_file = 'audio.mp4'

download(video, video_tmp_file, base_url + video['base_url'])
download(audio, audio_tmp_file, base_url + audio['base_url'])

command = ["ffmpeg", "-i", audio_tmp_file, "-i", video_tmp_file, "-c", "copy", file_name]

try:
    print("Joining video and audio...")
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stdout)  # Exibe a saída do comando
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
    print(f"Output error: {e.stderr}")

os.remove(video_tmp_file)
os.remove(audio_tmp_file)
