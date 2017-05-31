#!/usr/bin/env python3

import re
import os
import json
import math
import subprocess
from sys import argv
from pytube import YouTube
from tqdm import tqdm
from urllib import request
from random import randint

COMMENT_RE = re.compile(r"\/\/.*")
PROGRESS_BARS = {}
LAST_PROGRESS = {}

RETRAIN_REMOTE = "https://raw.githubusercontent.com/tensorflow/tensorflow/r1.2/tensorflow/examples/image_retraining/retrain.py"
RETRAIN_LOCAL = RETRAIN_REMOTE.split("/")[-1]

POINTS_FILE_NAME = "point_frames.txt"
VIDEOS_DIRECTORY = "videos"
FRAMES_DIRECTORY = "frames"

total_points_frames = 0
frames_per_video = 0

def main():
    # Remove Comments from JSON
    metadata_file_contents = ""
    with open(POINTS_FILE_NAME) as metadata_file:
        for line in metadata_file:
            metadata_file_contents += COMMENT_RE.sub("", line)

    # Parse JSON
    videos = json.loads(metadata_file_contents)

    # Directory where videos will be downloaded before being split into frames.
    yt = YouTube()

    # Count total P-Nos frames to balance data
    global total_points_frames
    for video in videos:
        points = video[1]
        if len(points) == 0:
            continue

        start, end = points[1]
        total_points_frames += end - start + 1

    print("Total P-Nos Frames: {}".format(total_points_frames))

    global frames_per_video
    frames_per_video = math.ceil(total_points_frames / len(videos))
    print("Non P-Nos Frames Per Video: {}".format(frames_per_video))

    # Download Videos
    for video in videos:
        video_id = video[0]
        points = video[1]

        yt.from_url("http://www.youtube.com/watch?v=" + video_id)
        yt.filename = video_id

        video = yt.get(extension='mp4', resolution='360p')

        filename = "{0}.{1}".format(video.filename, video.extension)
        filepath = os.path.join(VIDEOS_DIRECTORY, filename)
        if not os.path.isfile(filepath):
            # Download File if Needed
            video.download(VIDEOS_DIRECTORY,
                on_finish=lambda path: on_downloaded(video_id, path, points),
                on_progress=lambda received, size, start:
                    on_progress(video_id, received, size)
            )

        else:
            on_downloaded(video_id, filepath, points)

    # Transform Structure
    link_flat(input_directory=VIDEOS_DIRECTORY, output_directory=FRAMES_DIRECTORY)

    # Retrain network
    retrain(image_dir=FRAMES_DIRECTORY,
        output_graph='output/network.pb',
        output_labels='output/labels.txt')

def on_downloaded(video_id, path, points):
    # Teardown Progress Bar
    progress_bar = PROGRESS_BARS.get(video_id)
    if progress_bar is not None:
        progress_bar.close()
        del progress_bar
        del PROGRESS_BARS[video_id]

    frames_path = path + ".frames"
    if not os.path.isdir(frames_path):
        os.mkdir(frames_path)

        total_frames = get_frame_count(path)

        # Nos Positions
        start_nos, end_nos = -1, -1
        if len(points) != 0:
            start_nos, end_nos = points[1]

        # Get nos frames
        nos_path = os.path.join(frames_path, "nos")
        if not os.path.isdir(nos_path):
            os.mkdir(nos_path)

            if not start_nos <= 0:
                get_frames(path, nos_path,
                    [i for i in range(start_nos, end_nos+1)]
                )

        # Get Randon Non-nos frames.
        random_frames = []
        for i in range(frames_per_video):
            random_frame = 0
            while True:
                random_frame = randint(1, total_frames)
                if (start_nos <= 0 or 
                    random_frame < start_nos or
                    random_frame > end_nos):
                    break

            random_frames.append(random_frame)

        non_nos_path = os.path.join(frames_path, "non-nos")
        if not os.path.isdir(non_nos_path):
            os.mkdir(non_nos_path)
            get_frames(path, non_nos_path, random_frames)

def on_progress(video_id, received, size):
    # Get Progress Bar
    progress_bar = PROGRESS_BARS.get(video_id)
    if progress_bar is None:
        # Create Progress Bar
        progress_bar = tqdm(total=size)
        progress_bar.set_description(video_id)
        PROGRESS_BARS[video_id] = progress_bar

    # Update Progress Bar
    last_progress = LAST_PROGRESS.get(video_id)
    if last_progress is None:
        last_progress = 0

    progress_bar.update(received - last_progress)
    LAST_PROGRESS[video_id] = received

"""
Downloads (if necessary) and executes retrain.py.
"""
def retrain(image_dir, output_graph, output_labels):
    # Download retrain.py if needed
    if not os.path.isfile(RETRAIN_LOCAL):
        request.urlretrieve(RETRAIN_REMOTE, RETRAIN_LOCAL)

    subprocess.call([
        "python",
        os.path.join(".", RETRAIN_LOCAL),
        "--image_dir=" + image_dir,
        "--output_graph=" + output_graph,
        "--output_labels=" + output_labels,
    ])

"""
Returns the number of frames in a given input file's first video stream using
ffprobe.
"""
def get_frame_count(input_file):
    res = subprocess.run([
        "ffprobe", input_file,
            "-select_streams", "v",
            "-show_streams",
            "-print_format", "json"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=True
    )

    data = json.loads(res.stdout)
    return int(data['streams'][0]['nb_frames'])

"""
Extracts specified frames from input_file into output_dir using ffmpeg. Frames
are 1-indexed.
"""
def get_frames(input_file, output_dir, frames):
    # eq(n\,10)+eq(n\,11)
    frame_args = '+'.join(
        map(lambda frame_number: "eq(n,{})".format(frame_number), frames)
    )

    subprocess.call([
        "ffmpeg",
        "-i", input_file,
        "-vsync", "vfr",
        "-vf", "select='{}'".format(frame_args),
        os.path.join(output_dir, "%d.jpg")
    ])

"""
Takes this:

a/
  - item1/
    - 1
    - 2

  - item2
    - 3
    - 4 

b/
  - item1/
    - 1
    - 2

  - item2
    - 3
    - 4 

and turns it into this:

item1/
  - a.1
  - a.2
  - b.1
  - b.2

item2/
  - a.3
  - a.4
  - b.3
  - b.4
"""
def link_flat(input_directory, output_directory):
    for folder in dirs(input_directory):
        folder_path = os.path.join(input_directory, folder)

        for category in dirs(folder_path):
            category_path = os.path.join(folder_path, category)

            to_path = os.path.join(output_directory, category)
            os.makedirs(to_path, exist_ok=True)

            for item in files(category_path):
                fro = os.path.join(category_path, item)
                name = "{}.{}".format(folder, item)

                to = os.path.join(to_path, name)
                os.symlink(os.path.abspath(fro), to)

"""
Yields for every folder in the provided directory.
"""
def dirs(directory):
    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)
        if not os.path.isdir(full_path):
            continue

        yield file

"""
Yields for every file in the provided directory.
"""
def files(directory):
    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)
        if not os.path.isfile(full_path):
            continue

        yield file

if __name__ == "__main__":
    main()

# TODO: Save output list
