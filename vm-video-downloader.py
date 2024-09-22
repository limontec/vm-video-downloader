import os
import sys
import base64
import requests
import subprocess
from tqdm import tqdm

#For Windows:
#Download ffmpeg https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
#Put the script in the folder: C:\user\Downloads\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin
#For Linux:
#sudo apt install ffmpeg
#Run the script with: python vm-video-downloader.py
#Inspired by https://gist.github.com/alexeygrigorev/a1bc540925054b71e1a7268e50ad55cd?permalink_comment_id=5097364#gistcomment-5097364
#Script v0.2

class VimeoDownloader:
  def __init__(self, url, filename):
    if 'master.json' in url:
      url = url[:url.find('?')] + '?query_string_ranges=1'
      url = url.replace('master.json', 'master.mpd')
    self.url = url
    if not filename.endswith('.mp4'):
      filename += '.mp4'
    self.filename = filename
  def fetch(self, what, to, base):
    with open(to, 'wb') as file:
      init_segment = base64.b64decode(what['init_segment'])
      file.write(init_segment)
      for segment in tqdm(what['segments'], desc=to.replace('.mp4', '').upper(), bar_format='{desc}: {percentage:3.0f}% |{bar}| [{n_fmt}/{total_fmt}] '):
        segment_url = base + segment['url']
        resp = requests.get(segment_url, stream=True)
        if resp.status_code != 200:
          print('Segment not found:', segment_url)
          break
        for chunk in resp:
            file.write(chunk)
  def download(self):
    if 'master.mpd' in self.url:
      subprocess.run(['youtube-dl', self.url, '-o', self.filename])
      return
    base_url = self.url[:self.url.rfind('/', 0, -26) + 1]
    content = requests.get(self.url).json()
    vid_heights = [(i, d['height']) for (i, d) in enumerate(content['video'])]
    vid_idx, _ = max(vid_heights, key=lambda _h: _h[1])
    audio_quality = [(i, d['bitrate']) for (i, d) in enumerate(content['audio'])]
    audio_idx, _ = max(audio_quality, key=lambda _h: _h[1])
    video = content['video'][vid_idx]
    audio = content['audio'][audio_idx]
    base_url = base_url + content['base_url']
    video_tmp_file = 'video.mp4'
    audio_tmp_file = 'audio.mp4'
    self.fetch(video, video_tmp_file, base_url + video['base_url'])
    self.fetch(audio, audio_tmp_file, base_url + audio['base_url'])
    command = ["ffmpeg", "-i", audio_tmp_file, "-i", video_tmp_file, "-c", "copy", self.filename]
    try:
      result = subprocess.run(command, capture_output=True, text=True, check=True)
      print(result.stdout)
    except subprocess.CalledProcessError as e:
      print(f"Error: {e}")
      print(f"Output error: {e.stderr}")
    os.remove(video_tmp_file)
    os.remove(audio_tmp_file)

DOWNLOAD_MODE = "PLAYLIST" if len(sys.argv) > 1 and sys.argv[1] == '-p' else "SINGLE"

if DOWNLOAD_MODE == 'SINGLE':
    try: DATA_URL = sys.argv[1]
    except: DATA_URL = input('Enter [master|playlist].json url: ')
    try: OUTPUT_FILENAME = sys.argv[2]
    except: OUTPUT_FILENAME = input('Enter output filename: ')

data = []
if DOWNLOAD_MODE == "SINGLE":
  data.append((DATA_URL, OUTPUT_FILENAME))
else:
  if len(sys.argv) < 3:
    print('No playlist data provided. Exiting...')
    sys.exit(1)
  if not os.path.exists(sys.argv[2]):
    print('Provided playlist file does not exist. Exiting...')
    sys.exit(1)
  with open(sys.argv[2], 'r') as file:
    for i, line in enumerate(file.readlines(), start=1):
      videoData = [arg.strip() for arg in line.split(';')]
      if len(videoData) != 2 or videoData[0] == '' or videoData[1] == '':
        print('Incorrect syntax in line', i)
        continue
      data.append(tuple(videoData))

for DATA_URL, OUTPUT_FILENAME in data:
  if DATA_URL == '' or OUTPUT_FILENAME == '':
    continue
  print(f"Downloading {OUTPUT_FILENAME}...")
  downloader = VimeoDownloader(DATA_URL, OUTPUT_FILENAME)
  downloader.download()
