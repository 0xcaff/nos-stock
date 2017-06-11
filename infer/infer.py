#!/usr/bin/env python3

import time
from sys import argv

import cv2
import tensorflow as tf

MODEL_PATH = argv[1]
LABELS_PATH = argv[2]
VIDEO_PATH = argv[3]

LABEL_LINES = [line.rstrip() for line
    in tf.gfile.GFile(LABELS_PATH)]

def main(_):
    # Import Model
    with tf.gfile.FastGFile(MODEL_PATH, 'rb') as model_file:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(model_file.read())
        _ = tf.import_graph_def(graph_def, name='')

    # Initialize Session
    sess = tf.Session()

    # Setup Network
    output_tensor = sess.graph.get_tensor_by_name('final_result:0')
    input_tensor = sess.graph.get_tensor_by_name("Cast:0")

    # Initialize Video Processing
    capture = cv2.VideoCapture(VIDEO_PATH)
    frame_number = 0

    while capture.isOpened():
        start_time = time.perf_counter()
        # Read Frame
        ret, frame = capture.read()
        frame_number = frame_number + 1

        if not ret:
            print("Failed to read file.")
            break

        print("Frame Number: {}".format(frame_number))
        print(frame)

        # Infer Frame
        predictions = sess.run(output_tensor, {input_tensor: frame})

        # Print Prediction
        prediction = predictions[0]
        for idx, label in enumerate(LABEL_LINES):
            print("{}: {:.2f}".format(label, prediction[idx]))

        end_time = time.perf_counter()
        print("Took {:.2f} seconds".format(end_time - start_time))
        print("")

    if frame_number == 0:
        print("Failed to read file.")

    capture.release()
    sess.close()

if __name__ == "__main__":
    tf.app.run(main=main, argv=[argv[0]] + argv[2:])
