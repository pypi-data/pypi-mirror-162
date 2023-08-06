import sys

# Client APIs for main frameworks
if "torch" in sys.modules:
    from modalic.api.torch import PytorchClient

if "tensorflow" in sys.modules:
    from modalic.api.tf import TfClient

# from modalic.client.trainer import Trainer

# Decorators
if "torch" in sys.modules:
    from modalic.api.torch import torch_train

if "tensorflow" in sys.modules:
    from modalic.api.tf import tf_train

# Configuration
from modalic.config import Conf

# Invoke Aggregation Server
from modalic.server.server import run_server

# Simulation API
from modalic.simulation import ClientPool
