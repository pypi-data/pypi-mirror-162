import gzip
import os
from typing import Any, Tuple

import numpy as np
import torch


def read_from_path(dir: str = "") -> Tuple[np.array, np.array, np.array, np.array]:
    r"""relies on The MNIST database of handwritten digits
    http://yann.lecun.com/exdb/mnist/
    """
    train_raw = gzip.open(os.path.join(dir, "train-images-idx3-ubyte.gz"), "r")
    test_raw = gzip.open(os.path.join(dir, "t10k-images-idx3-ubyte.gz"), "r")
    train_labels_raw = gzip.open(os.path.join(dir, "train-labels-idx1-ubyte.gz"), "r")
    test_labels_raw = gzip.open(os.path.join(dir, "t10k-labels-idx1-ubyte.gz"), "r")

    # Train data
    train_raw.read(16)
    buf = train_raw.read(60000 * 28 * 28)
    data = np.frombuffer(buf, dtype=np.uint8).astype(np.float32)
    train_data = data.reshape(60000, 1, 28, 28)

    # Test data
    test_raw.read(16)
    buf = test_raw.read(10000 * 28 * 28)
    data = np.frombuffer(buf, dtype=np.uint8).astype(np.float32)
    test_data = data.reshape(10000, 1, 28, 28)

    # Train labels
    train_labels_raw.read(8)
    buf = train_labels_raw.read(60000)
    train_labels = np.frombuffer(buf, dtype=np.uint8).astype(np.float32)

    # Test labels
    test_labels_raw.read(8)
    buf = test_labels_raw.read(10000)
    test_labels = np.frombuffer(buf, dtype=np.uint8).astype(np.float32)

    return (train_data, test_data, train_labels, test_labels)


def load_partition_data_mnist(num_splits: int = 10) -> Tuple[Any, Any, Any, Any]:
    r"""partition training set into same sized splits."""
    dir = os.path.abspath("data/MNIST/mnist/")
    train_data, test_data, train_labels, test_labels = read_from_path(dir)
    return (
        np.split(train_data, num_splits),
        np.split(train_labels, num_splits),
        test_data,
        test_labels,
    )


class Dataloader(torch.utils.data.Dataset):
    r"""Dataloader class object."""

    def __init__(self, data, labels):
        self.data = data
        self.labels = labels

    def __len__(self):
        return self.data.shape[0]

    def __getitem__(self, idx):
        return (self.data[idx], self.labels[idx])
