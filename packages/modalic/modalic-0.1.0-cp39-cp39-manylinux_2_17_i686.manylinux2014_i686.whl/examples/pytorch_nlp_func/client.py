import os
import sys

import torch
from data import collate_batch, train_iter, vocab
from torch import nn
from torchtext.data.functional import to_map_style_dataset

import modalic

from . import create_arg_parser, get_project_root

# Parsing the .toml config
arg_parser = create_arg_parser()
args = arg_parser.parse_args(sys.argv[1:])

conf = modalic.Conf.from_toml(path=os.path.join(get_project_root(), "config.toml"))
conf.client_id = args.client_id


# Hyperparameters
EPOCHS = 1  # epoch
LR = 5  # learning rate
BATCH_SIZE = 64  # batch size for training


class TextClassificationModel(nn.Module):
    r"""."""

    def __init__(self, vocab_size, embed_dim, num_class):
        super(TextClassificationModel, self).__init__()
        self.embedding = nn.EmbeddingBag(vocab_size, embed_dim, sparse=True)
        self.fc = nn.Linear(embed_dim, num_class)
        self.init_weights()

    def init_weights(self):
        initrange = 0.5
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()

    def forward(self, text, offsets):
        embedded = self.embedding(text, offsets)
        return self.fc(embedded)


@modalic.train(conf=conf)
def train(model, dataloader, optimizer, criterion, scheduler, epochs: int = 1):
    model.train()
    total_acc, total_count = 0, 0

    for epoch in range(1, epochs + 1):
        for idx, (label, text, offsets) in enumerate(dataloader):
            optimizer.zero_grad()
            predicted_label = model(text, offsets)
            loss = criterion(predicted_label, label)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.1)
            optimizer.step()

            total_acc += (predicted_label.argmax(1) == label).sum().item()
            total_count += label.size(0)

            if idx % 250 == 0 and idx > 0:
                print(
                    "| epoch {:3d} | {:5d}/{:5d} batches "
                    "| accuracy {:8.3f}".format(
                        epoch, idx, len(dataloader), total_acc / total_count
                    )
                )
                total_acc, total_count = 0, 0

    return model


def main():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    num_class = len(set([label for (label, text) in train_iter]))
    vocab_size = len(vocab)
    emsize = 64

    model = TextClassificationModel(vocab_size, emsize, num_class).to(device)
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 1.0, gamma=0.1)

    train_dataset = to_map_style_dataset(train_iter)

    num_train = int(len(train_dataset) * 0.95)
    split_train_, split_valid_ = torch.utils.data.dataset.random_split(
        train_dataset, [num_train, len(train_dataset) - num_train]
    )

    train_dataloader = torch.utils.data.DataLoader(
        split_train_, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_batch
    )

    train(model, train_dataloader, optimizer, criterion, scheduler)


if __name__ == "__main__":
    main()
