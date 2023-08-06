from pathlib import Path
import pandas as pd
from rankpy import rank

DATA_DIR = Path.cwd().joinpath(
    "data"
)

# Get matrices created by process_example.py
flows = pd.read_csv(DATA_DIR.joinpath("flow_matrix.csv"), header=0, index_col=0)
compares = pd.read_csv(DATA_DIR.joinpath("comparison_matrix.csv"), header=0, index_col=0)

def test_hodge_rank():
    print(rank.hodge_rank(flows, compares))