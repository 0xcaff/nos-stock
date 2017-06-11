nos-stock
=========
A collection of scripts which automates the discovery of P-Nos point frames.
Install dependencies before using any of these scripts.

    pip install -r requirements.txt

`train.py`
----------
Using data from `point_frames.txt`, retrains google's inception model for
detecting P-Nos point frames.

Run the following to download training videos, slice them up and feed them to
inception. This will take < 5GB of disk space, lots of time, processing power
and memory.

    python train.py

You can view the preformance of the network with

    tensorboard --logdir /tmp/retrain_logs

`train.py` will create the following directory structure:

    ├── output
    │   ├── labels.txt
    │   └── network.pb
    │
    ├── videos
    │   ├── video-id.mp4
    │   ├── video-id.mp4.frames
    │   │   ├── nos
    │   │   │   └── number.jpg
    │   │   └── non-nos
    │   │       └── number.jpg
    │   └── ...
    │
    └── frames
        ├── nos
        │   └── video-id.mp4.frames.number.jpg (symlink)
        └── non-nos
            └── video-id.mp4.frames.number.jpg (symlink)

The product of the training is `output/network.pb`.


`on_message.py`
--------------
Downloads a video file and searches for the P-Nos point frames. It can be
invoked manually with the video id of the video to infer or with a PubSubHubbub
message payload passed to standard input. Check out [`push-sub`][push-sub] for
a PubSubHubbub daemon.

In order for `on_message.py` to work, you need to build `infer` by running
`make` from `infer/`.

`view_graph.py`
--------------
A script for emitting `tensorboard` viewable logs for a given tensorflow graph.
Run it with the following arguments:

    python view_graph.py <model file> <tensorboard log output>

Now you can view the logs using:

    tensorboard --logdir <tensorboard log output>

`infer/`
-------
A C++ program for getting video frames and feeding through the network. We are
using a native program here for better preformance when reading video frames.

[push-sub]: https://github.com/0xcaff/sub/tree/master/push-sub
