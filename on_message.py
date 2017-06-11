#!/usr/bin/env python3

from lxml import etree
import sys
from pytube import YouTube

VIDEOS_DIRECTORY = os.realpath("videos")

def get_info(input):
    tree = etree.parse(sys.stdin)
    root = tree.getroot()
    video_id = root.find('//yt:videoId', root.nsmap).text
    return video_id

def on_downloaded(video_id, filepath):
    # The file is downloaded, run inference.
    # TODO: Do this

if __name__ == '__main__':
    if len(sys.argv) != 0:
        video_id = sys.argv[0]
    else:
        video_id = get_info(sys.stdin)

    # Download
    yt = YouTube("http://www.youtube.com/watch?v="+video_id)
    yt.filename = video_id
    video = yt.get(extension='mp4', resolution='360p')
    filename = "{0}.{1}".format(video.filename, video.extension)
    filepath = os.path.join(VIDEOS_DIRECTORY, filename)
    if not os.path.isfile(filepath):
        # Download if needed
        video.download(VIDEOS_DIRECTORY,
            on_finish=lambda path: on_downloaded(video_id, path))
    else:
        on_downloaded(video_id, filepath)

