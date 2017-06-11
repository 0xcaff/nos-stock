#!/usr/bin/env python3

import sys
import os.path
import subprocess
from lxml import etree
from pytube import YouTube

def realpath(end):
    return os.path.join(SOURCE_DIR, end)

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOS_DIR = realpath("videos")

def get_info(input):
    tree = etree.parse(sys.stdin)
    root = tree.getroot()
    video_id = root.find('//yt:videoId', root.nsmap).text
    return video_id

def on_downloaded(filepath):
    # The file is downloaded, run inference.
    infer_output_file = filepath + ".infer.json"
    if os.path.exists(infer_output_file):
        return

    res = subprocess.run([
        realpath('infer/infer'),
            realpath('output/network-stripped.pb'),
            filepath, "30",
        ],

        # Write to file
        stdout=open(filepath + ".infer.json", 'wb'),
    )

if __name__ == '__main__':
    if len(sys.argv) != 0:
        video_id = sys.argv[1]
    else:
        video_id = get_info(sys.stdin)

    # Download
    yt = YouTube("https://www.youtube.com/watch?v=" + video_id)
    yt.filename = video_id

    video = yt.get(extension='mp4', resolution='360p')
    filename = "{0}.{1}".format(video.filename, video.extension)
    filepath = os.path.join(VIDEOS_DIR, filename)

    # Download if needed
    if not os.path.isfile(filepath):
        video.download(VIDEOS_DIR,
            on_finish=lambda path: on_downloaded(path))
    else:
        on_downloaded(filepath)

