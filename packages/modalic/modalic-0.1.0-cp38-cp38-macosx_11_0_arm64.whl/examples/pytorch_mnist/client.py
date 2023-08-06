import argparse
import sys

import torch
import torch.nn as nn
from data import Dataloader, load_partition_data_mnist

import modalic


def create_arg_parser():
    r"""Get arguments from command lines."""
    parser = argparse.ArgumentParser(description="Client parser.")
    parser.add_argument(
        "--client_id", metavar="N", type=int, help="an integer specifing the client ID."
    )

    return parser


class CNN(nn.Module):
    r"""simple 2D CNN model for classification."""

    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(
                in_channels=1,
                out_channels=16,
                kernel_size=5,
                stride=1,
                padding=2,
            ),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, 5, 1, 2),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.out = nn.Linear(32 * 7 * 7, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = x.view(x.size(0), -1)
        output = self.out(x)
        return output, x


class Trainer(object):
    r"""Trainer class object to perform the Learning.

    :param device: (torch.device) Model running device. GPUs are recommended for model training and inference.
    :param dataset: (data.Dataloader) Custom Dataloader object.
    :param epochs: (int) Epochs hyperparameter.
    """

    def __init__(
        self,
        device: torch.device,
        dataset: Dataloader,
        epochs: int = 1,
    ):
        self.device = device
        self.dataset = dataset
        self.epochs = epochs

        self.trainloader = torch.utils.data.DataLoader(
            self.dataset, batch_size=32, shuffle=True
        )

        self.model = CNN()
        self.loss = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)

    def train(self):
        self.model.train()

        running_loss = 0.0
        for epoch in range(0, self.epochs):
            for i, (images, labels) in enumerate(self.trainloader):
                self.optimizer.zero_grad()
                output, _ = self.model.forward(images)

                loss = self.loss(output, labels.long())
                loss.backward()
                self.optimizer.step()
                running_loss += loss.item()

        return self.model, running_loss / len(self.trainloader)


def main():
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args(sys.argv[1:])

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    train_data, train_labels, test_data, test_labels = load_partition_data_mnist(
        num_splits=100
    )

    client = modalic.PytorchClient(
        Trainer(
            device,
            Dataloader(
                train_data[args.client_id - 1], train_labels[args.client_id - 1]
            ),
        ),
        args.client_id,
        conf={
            "api": {"server_address": "[::]:8080"},
            "process": {"training_rounds": 10, "timeout": 5.0},
        },
    )
    client.train()


if __name__ == "__main__":
    main()
