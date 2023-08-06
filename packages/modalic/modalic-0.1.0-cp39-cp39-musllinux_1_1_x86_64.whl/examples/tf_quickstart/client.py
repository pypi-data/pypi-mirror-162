import argparse
import os
import sys

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf

import modalic


def create_arg_parser():
    r"""Get arguments from command lines."""
    parser = argparse.ArgumentParser(description="Client parser.")
    parser.add_argument(
        "--client_id", metavar="N", type=int, help="an integer specifing the client ID."
    )

    return parser


# Parsing the command-line arguments
arg_parser = create_arg_parser()
args = arg_parser.parse_args(sys.argv[1:])

# Modalic configuration
cfg = {
    "api": {"server_address": "[::]:8080"},
    "process": {"training_rounds": 5, "timeout": 5.0},
}
conf = modalic.Conf.create_conf(cfg, cid=args.client_id)


# wrap custom train function with modalic.tf_train
@modalic.tf_train(conf)
def train(model, x_train, y_train):
    model.fit(x_train, y_train, batch_size=32, epochs=1)
    return model


def main():
    # Load the MobileNetV2 and CIFAR-10 dataset
    model = tf.keras.applications.MobileNetV2((32, 32, 3), classes=10, weights=None)
    model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])

    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

    train(model, x_train, y_train)


if __name__ == "__main__":
    main()
