#!/usr/bin/env python3

import subprocess
import sys

# see: https://unix.stackexchange.com/a/388148

def previewVideo(url, startTime, duration, outName="out.mkv"):

    ytdl = subprocess.run(['youtube-dl', '--youtube-skip-dash-manifest', '-g', url], capture_output=True, text=True)

    urls = ytdl.stdout.split("\n")
    videoURL = urls[0]
    audioURL = urls[1]

    # TODO: add option for uniq file
    #outName=`mktemp previewXXXX.mkv`

    subprocess.run(['ffmpeg', '-y', '-ss', startTime, '-i', videoURL, '-ss', startTime, '-i', audioURL, '-map', '0:v', '-map', '1:a', '-t', duration, '-c:v', 'libx264', '-c:a', 'aac', outName], capture_output=True, text=True)

    #subprocess.run(['mpv', outName])

def main():

    if len(sys.argv) < 2:
        sys.stderr.write('usage: %s URL [START] [DURATION]\n' % sys.argv[0])
        exit(1)

    start = sys.argv[2] if len(sys.argv) >= 3 else "0"
    duration = sys.argv[3] if len(sys.argv) >= 4 else "10"

    previewVideo(sys.argv[1], start, duration)

if __name__ == "__main__":
    main()
