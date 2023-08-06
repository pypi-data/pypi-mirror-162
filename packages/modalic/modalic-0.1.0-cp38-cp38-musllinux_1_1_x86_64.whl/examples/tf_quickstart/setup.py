from setuptools import find_packages, setup

requirements = [
    "modalic>=0.1.0",
    "tensorflow>=1.22.4",
]


def setup_package():
    __version__ = "0.1.0"

    setup(
        name="tf_quickstart",
        description="Tensorflow Federated Learning example classifying images.",
        authors="Modalic",
        version=__version__,
        install_requires=requirements,
        packages=find_packages(),
    )


if __name__ == "__main__":
    setup_package()
