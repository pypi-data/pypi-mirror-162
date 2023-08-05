import tensorflow_datasets as tfds
import tensorflow as tf
import numpy as np
from tensorflow_datasets.testing import mock_data
from importlib.machinery import SourceFileLoader


def check_MyModel(filename, path):
    try:
        # check if file contains the MyModel function
        model = SourceFileLoader(filename, f"{path}").load_module()
        model = model.MyModel(input_shape=(500, 500, 3), classes=10)
        return True, model

    except AttributeError:
        return (
            False,
            "Model file not provided as per docs: No function with name MyModel",
        )
    except TypeError:
        return (
            False,
            "Model file not provided as per docs: MyModel function receives no arguments",
        )
    except ValueError:
        return False, "Layers shape is not compatible with model input shape"


def is_model_supported(model_obj):
    tensorflow_supported_apis = (tf.keras.models.Sequential, tf.keras.Model)
    supported = isinstance(model_obj, tensorflow_supported_apis)
    if supported:
        # check if it of subclassing
        try:
            # Note that the `input_shape` property is only available for Functional and Sequential models.
            input_shape = model_obj.input_shape
            return True
        except AttributeError:
            return False


# function to check if layers used in tensorflow are supported
def layer_instance_check(model):
    for layer in model.layers:
        if not isinstance(layer, tf.keras.layers.Layer):
            return False
        return True


def mock_dataset(classes):
    num_examples = 5

    def as_dataset(self, *args, **kwargs):
        return tf.data.Dataset.from_generator(
            lambda: (
                {
                    "image": np.ones(shape=(500, 500, 3), dtype=np.uint8),
                    "label": classes,
                }
                for i in range(num_examples)
            ),
            output_types=self.info.features.dtype,
            output_shapes=self.info.features.shape,
        )

    with mock_data(as_dataset_fn=as_dataset):
        (ds_train, ds_test), ds_info = tfds.load(
            "beans",
            split=["train", "test"],
            shuffle_files=True,
            as_supervised=True,
            with_info=True,
        )

    ds_train = ds_train.map(normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
    ds_train = ds_train.batch(128)
    ds_train = ds_train.prefetch(tf.data.AUTOTUNE)

    return ds_train


def normalize_img(image, label):
    """Normalizes images: `uint8` -> `float32`."""
    return tf.cast(image, tf.float32) / 255.0, label


def small_training_loop(model, training_dataset):
    # try:
    print("in training loop",training_dataset)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy()],
    )
    model.summary()
    history = model.fit(training_dataset, epochs=1, verbose=1)
    #     return True
    # except Exception as e:
    #     print("exception in training small loop: e")
    #     return False
