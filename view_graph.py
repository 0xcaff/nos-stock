import tensorflow as tf
import sys
from tensorflow.python.platform import gfile

with tf.Session() as sess:
    model_filename = sys.argv[1]
    with gfile.FastGFile(model_filename, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        g_in = tf.import_graph_def(graph_def)

log_directory = sys.argv[2]
train_writer = tf.summary.FileWriter(log_directory)
train_writer.add_graph(sess.graph)
