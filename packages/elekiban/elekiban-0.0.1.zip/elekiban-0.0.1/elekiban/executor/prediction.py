from cmath import pi
import os
import tensorflow as tf

from ..pipeline.pipe import AbstractPipe


def predict(model_path: os.PathLike,
            pipe: AbstractPipe,
            after_fn):

    model = tf.keras.models.load_model(model_path, compile=False)
    for i in range(pipe.data_num):
        after_fn(model.predict(pipe.generate([i])), i)
