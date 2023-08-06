import argparse
from pathlib import Path


def get_project_root() -> Path:
    r"""Returns project root path."""
    return Path(__file__).parent


def create_arg_parser():
    r"""Get arguments from command lines."""
    parser = argparse.ArgumentParser(description="Client parser.")
    parser.add_argument(
        "--cfg", metavar="N", type=int, help="configuration file (path)"
    )
    parser.add_argument(
        "--client_id", metavar="N", type=int, help="an integer specifing the client ID."
    )

    return parser
