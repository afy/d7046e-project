# Not final; using to test imports using venv.

import sys
print(sys.version)

import torch, torchvision
from segment_anything import SamPredictor, sam_model_registry

print("Libraries work!")

