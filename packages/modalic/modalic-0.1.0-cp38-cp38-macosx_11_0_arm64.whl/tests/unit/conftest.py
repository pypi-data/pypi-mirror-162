#  Copyright (c) modalic 2022. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import pytest
import tensorflow as tf
import torch


def get_torch_model_definition():
    r"""
    Defines a PyTorch model class that inherits from ``torch.nn.Module``.
    This method can be invoked within a pytest fixture to define the model class in the ``__main__`` scope.
    """

    # pylint: disable=W0223
    class SubclassedModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(4, 1)

        def forward(self, x):
            # pylint: disable=arguments-differ
            y_pred = self.linear(x)
            return y_pred

    return SubclassedModel


@pytest.fixture(scope="module")
def torch_model():
    r"""
    A custom PyTorch model inheriting from ``torch.nn.Module`` whose class is defined in the
    "__main__" scope.
    """
    model_class = get_torch_model_definition()
    model = model_class()
    # train_model(model=model, data=data)
    yield model


# Tensorflow section
def get_keras_model_definition_sequential_api():
    r"""
    Defines a Keras model class that inherits from ``tf.keras.Model`` based on
    Model Sub-Classing API.
    """

    seq_model = tf.keras.models.Sequential(
        [
            tf.keras.layers.Flatten(input_shape=(32, 32, 3)),
            tf.keras.layers.Dense(3000, activation="relu"),
            tf.keras.layers.Dense(1000, activation="relu"),
            tf.keras.layers.Dense(10),
        ]
    )

    return seq_model


def get_keras_model_definition_functional_api():
    r"""
    Defines a Keras model class that inherits from ``tf.keras.Model`` based on
    Model Sub-Classing API.
    """
    input_dim = (32, 32, 3)
    output_dim = 10
    input = tf.keras.Input(shape=(input_dim))

    # Block 1
    x = tf.keras.layers.Conv2D(32, 3, strides=2, activation="relu")(input)
    x = tf.keras.layers.MaxPooling2D(3)(x)
    x = tf.keras.layers.BatchNormalization()(x)

    # Now that we apply global max pooling.
    gap = tf.keras.layers.GlobalMaxPooling2D()(x)

    # Finally, we add a classification layer.
    output = tf.keras.layers.Dense(output_dim)(gap)

    # bind all
    func_model = tf.keras.Model(input, output)

    return func_model


def get_keras_model_definition_subclass_api():
    r"""
    Defines a Keras model class that inherits from ``tf.keras.Model`` based on
    Model Sub-Classing API.
    """

    class SubclassedModel(tf.keras.Model):
        def __init__(self):
            super().__init__()
            self.conv1 = tf.keras.layers.Conv2D(32, 3, strides=2, activation="relu")
            self.max1 = tf.keras.layers.MaxPooling2D(3)
            self.bn1 = tf.keras.layers.BatchNormalization()

            self.dense = tf.keras.layers.Dense(5)

        def call(self, input_tensor, training=False):
            x = self.conv1(input_tensor)
            x = self.max1(x)
            x = self.bn1(x)

            return self.dense(x)

    return SubclassedModel


@pytest.fixture(scope="module")
def sub_keras_model():
    r"""
    A custom tf keras model inheriting from ``tf.keras.Model`` whose class is defined in the
    "__main__" scope and based on the Sub-Classing API.
    """
    model_class = get_keras_model_definition_subclass_api()
    model = model_class()

    yield model


@pytest.fixture(scope="module")
def seq_keras_model():
    r"""
    A custom tf keras model inheriting from ``tf.keras.Model`` whose class is defined in the
    "__main__" scope and based on the Sequential API.
    """
    yield get_keras_model_definition_sequential_api()
