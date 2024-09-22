# vm-video-downloader
Download Vimeo videos easy v0.2<br/>
Authored by: [limontec](https://github.com/limontec)<br/>
Modified by: [Bartek20](https://github.com/Bartek20)

# Usage with slow download
Click on the "Open in Colab" button.
<a href="https://colab.research.google.com/github/limontec/vm-video-downloader/blob/master/VMVideoDownloader.ipynb" target="_parent\"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# Usage with fast download

### For Windows:
1. Download [ffmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip)
2. Extract downloaded zip file 
2. Put the script **vm-video-downloader.py** in the extracted folder (to the **bin** directory)
4. Run the script (shown below)

### For Linux:
1. sudo apt install ffmpeg
2. Run the script (shown below)

## Running script
```bash
# Provide required data while running script
python vm-video-downloader.py
```
```bash
# Provide required data before running script
python vm-video-downloader.py "[master|playlist].json url" "FILENAME"
```
```bash
# Provide list of urls
# List has following syntax:
# PLAYLIST_URL;FILENAME
python vm-video-downloader.py -p "list path"
```

# How to find the playlist.json?
Right click on the video > Inspect > Click on the Network tab > Play the video > Right click on "playlist.json?omit=..." > Copy the Request URL.
