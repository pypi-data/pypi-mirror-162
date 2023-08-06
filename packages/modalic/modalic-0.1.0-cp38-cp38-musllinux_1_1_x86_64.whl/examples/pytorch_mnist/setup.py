from setuptools import find_packages, setup

requirements = [
    "modalic>=0.1.0",
    "numpy>=1.22.4",
    "torch>=1.8.0",
    "torchvision>=0.12.0",
    "toml>=0.10.2",
]


def setup_package():
    __version__ = "0.1.0"

    setup(
        name="pytorch_mnist",
        description="Pytorch Federated Learning example classifying Hand-written.",
        authors="Modalic",
        version=__version__,
        install_requires=requirements,
        packages=find_packages(),
    )


if __name__ == "__main__":
    setup_package()
