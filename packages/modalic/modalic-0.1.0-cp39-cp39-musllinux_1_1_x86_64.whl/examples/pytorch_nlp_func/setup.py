from setuptools import find_packages, setup

requirements = [
    "modalic>=0.1.0",
    "numpy>=1.22.4",
    "torch>=1.8.0",
    "torchvision>=0.12.0",
    "torchtext>=0.12.0",
    "torchdata>=0.3.0",
    "toml>=0.10.2",
]


def setup_package():
    __version__ = "0.1.0"

    setup(
        name="pytorch_nlp_func",
        description="Pytorch Federated Learning example classifying text using the TorchText library.",
        authors="Modalic",
        url="https://pytorch.org/tutorials/beginner/text_sentiment_ngrams_tutorial.html",
        version=__version__,
        install_requires=requirements,
        packages=find_packages(),
    )


if __name__ == "__main__":
    setup_package()
