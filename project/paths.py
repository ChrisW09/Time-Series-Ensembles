import os

print("Loading paths...")
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(ROOT_DIR, "results")
DATA_DIR = os.path.join(ROOT_DIR, "data")
SIMDATA_DIR = os.path.join(DATA_DIR, "simulations")

