import argparse

import modalic

parser = argparse.ArgumentParser(description="Server arguments.")
parser.add_argument("--cfg", type=str, help="configuration file (path)")

args = parser.parse_args()

modalic.run_server(args.cfg)
