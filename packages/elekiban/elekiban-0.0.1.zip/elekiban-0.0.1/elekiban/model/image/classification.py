from tensorflow.keras import Model, Input
from tensorflow.keras.layers import Dense, Conv2D, GlobalAveragePooling2D, MaxPool2D
import tensorflow_hub as hub


def get_simple_model(input_name, output_name, class_num, model_scale=1, image_size=[16, 16], input_channel=3):
    down_sampling_time = int(min(image_size) / 2) - 1
    filters = input_channel
    x = Input(shape=(None, None, input_channel))
    y = x
    for _ in range(down_sampling_time):
        filters = max(int(model_scale * filters * 2), 1)
        y = Conv2D(filters, 3, padding="same", activation="relu")(y)
        y = MaxPool2D(padding="same")(y)
    y = GlobalAveragePooling2D()(y)
    y = Dense(filters, activation="relu")(y)
    y = Dense(max((filters + class_num) / 2, 1), activation="relu")(y)
    y = Dense(class_num, activation="sigmoid" if class_num == 1 else "softmax")(y)
    return Model(inputs={input_name: x}, outputs={output_name: y}, name="img2class")


def get_efficient_net_v2(input_name, output_name, class_num, input_channel=3):
    x = Input(shape=(224, 224, input_channel))
    y = Conv2D(3, 1, padding="same")(x) if input_channel != 3 else x
    y = hub.KerasLayer("https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet1k_b0/feature_vector/2", trainable=True)(x)
    y = Dense(640, activation="relu")(y)
    y = Dense(int((640 + class_num) / 2), activation="relu")(y)
    y = Dense(class_num, activation="sigmoid" if class_num == 1 else "softmax")(y)
    return Model(inputs={input_name: x}, outputs={output_name: y}, name="img2class")
