# Import pkgs
from pathlib import Path
import numpy as np
import pandas as pd
import trueskill

# Constants
NUM_COMPARISONS_PER_QUESTION = 5  # TODO: Should this be passed or in a common dict?
DATA_DIR = Path.cwd().parent.joinpath(
    "data"
)  # Assuming running from rankpy/ (equal level to data/)


# Functions
def check_symmetry(m):
    # https://stackoverflow.com/questions/42908334/checking-if-a-matrix-is-symmetric-in-numpy
    return np.allclose(m, m.T, equal_nan=True)


def calc_r2(y_bar, ranks, comparisons_):
    """
    :Info: Calculates r-squared based upon the average flows, number of comparisons, and ranking.
    :param y_bar: list-like (i.e. avg_flow)
    :param ranks: numpy array
    :param comparisons_:DataFrame
    :return float
    """

    num = []  # numerator
    den = []  # denominator
    Y_bar = y_bar.fillna(0).to_numpy()  # avg_flow, but modified for use in the denominator
    NUM_OPTS = len(Y_bar)

    for i in range(NUM_OPTS):
        for j in range(i+1, NUM_OPTS):
            num += [(ranks[j]-ranks[i])*(comparisons_[i,j])]
            den += [Y_bar[i,j]*(comparisons_[i,j])]

    numerator = np.square(np.linalg.norm(num, ord=2))               
    denominator = np.square(np.linalg.norm(den, ord=2))

    return np.around(numerator/denominator, 2)


def hodge_rank(flows_, comparisons_, use_unweighted_comparisons=True, show_r2=True):
    """
    :Info: Given two matrices of (1) net flows between pairs and (2) total number of comparisons,
            produce a Hodge ranking.  
            Ensure that each matrix shares indices and column headers (within and across matrices).
    :param flows_:DataFrame
    :param comparisons_:DataFrame
    :param use_unweighted_comparisons:bool (True if comparisons matrix should only indicate adjacency as binary)
    :param show_r2:bool (True if r^2 should be displayed)
    :return options_with_hodge_rank:DataFrame
    """
    THRESHOLD_R2 = 0.33  # Could make this a passed parameter

    # TODO: ensure that README explains variable mappings (e.g. delta_naught, Y_bar)
    # FUTURE: Allow flows & comparisons to be passed as numpy matrix (vs DataFrame)

    # Check that comparisons matrix is symmetric
    if not check_symmetry(comparisons_):
        print(comparisons_)
        raise ValueError("Comparisons matrix is not symmetric")

    # Ensure that indices and columns (across both matrices) are the same
    if not ((flows_.columns.values == comparisons_.columns.values).all() 
        & (flows_.index.values == comparisons_.index.values).all()
        & (flows_.columns.values == comparisons_.index.values).all()):
        print(flows_.columns.values)
        print(comparisons_.columns.values)
        print(flows_.index.values)
        print(comparisons_.index.values)
        raise ValueError("Passed matrices have unmatched columns and indices.")

    # Divide flow (i.e. net pair preferences) by comparisons (i.e. weights) to get average flow
    # avg_flow = flows_.div(comparisons_, fill_value=0)  # i.e. Y_bar (Eq. 9) from Jiang paper
    ## We should ask for average flow as input, not raw flow
    avg_flow = flows_

    if use_unweighted_comparisons:  # Cap values at 1 (i.e. binary adjacency matrix)
        comparisons = np.where(comparisons_ > 1, 1, comparisons_)
    else:  # e.g. use an aggreate number of comparisons
        comparisons = comparisons_.to_numpy()
    
    delta_naught = -1*comparisons  # delta naught s (i.e. Eq. #25 in Jiang et al)
    np.fill_diagonal(delta_naught, comparisons.sum(axis=1)) # Need to fill i=j with sum of weights for each option
    mp_inv_delta_naught = np.linalg.pinv(delta_naught)  # Moore-Penrose pseudo-inverse (in case divide by 0)
    mp_inv_delta_naught = -1 * mp_inv_delta_naught  # Need to negate to get correct sign

    # Note net_flows will give equal weight to option pairs ranked once and those ranked many times
    net_flows = avg_flow.fillna(0).sum(axis=0)  # Use axis=0 (rows) to ensure highest ranked is positive edge weight; nee y_binary

    hodge_ranks = np.matmul( net_flows, mp_inv_delta_naught)  # (i.e s_star (Eq. 26) -- the Hodge ranking calculation)

    options_with_hodge_rank = pd.DataFrame({'option':avg_flow.index.values, 'hodge_rank':hodge_ranks}).sort_values(by='hodge_rank', ascending=False)

    if show_r2:
        r2 = calc_r2(avg_flow, hodge_ranks, comparisons)

        if r2 < THRESHOLD_R2:
            print(f"WARNING: r^2 is {r2} (which is lower than the threshold of {THRESHOLD_R2}.  This suggests the rank order may not be accurate representation of underlying data.")
        else:
            print(f"The r^2 is {r2} (which is higher than the threshold of {THRESHOLD_R2}.  This suggests the rank order does well at explaining underlying data.")

    return options_with_hodge_rank


def get_list_of_tuples(data):
    """
    :Info: Takes a pre-filtered list of charges and TrueSkill ratings and tuples the ratings
    :param data: DataFrame
    :returns list (of tuples)
    """

    indices = data.index.values

    if len(data) == 5:
        tmp_tuple = data.loc[indices[0], "rating"]
        try:
            r1 = trueskill.Rating(tmp_tuple)
        except:
            r1 = trueskill.Rating(tmp_tuple[0])

        tmp_tuple = data.loc[indices[1], "rating"]
        try:
            r2 = trueskill.Rating(tmp_tuple)
        except:
            r2 = trueskill.Rating(tmp_tuple[0])

        tmp_tuple = data.loc[indices[2], "rating"]
        try:
            r3 = trueskill.Rating(tmp_tuple)
        except:
            r3 = trueskill.Rating(tmp_tuple[0])

        tmp_tuple = data.loc[indices[3], "rating"]
        try:
            r4 = trueskill.Rating(tmp_tuple)
        except:
            r4 = trueskill.Rating(tmp_tuple[0])

        tmp_tuple = data.loc[indices[4], "rating"]
        try:
            r5 = trueskill.Rating(tmp_tuple)
        except:
            r5 = trueskill.Rating(tmp_tuple[0])

        l = [(r1,), (r2,), (r3,), (r4,), (r5,)]
    else:
        raise ValueError(f"Unexpected number of ratings: {len(data)}")

    return l


def get_list_of_dicts(data):
    """
    :Info: Takes a pre-filtered list of charges and TrueSkill ratings and tuples the ratings
    :param data: DataFrame
    :returns list (of tuples)
    """

    num_comparisons = len(data)

    if num_comparisons != NUM_COMPARISONS_PER_QUESTION:
        raise ValueError(f"{NUM_COMPARISONS_PER_QUESTION} comparisons were not made.")

    l = []

    for i in data.index.values:
        l += [{i: data.loc[i, "rating"]}]

    return l


def get_list_of_tuples(data):
    """
    :Info: Takes a pre-filtered list of charges and TrueSkill ratings and tuples the ratings
    :param data: DataFrame
    :returns list (of tuples)
    """

    # from pandas.core.dtypes.common import (
    #     is_named_tuple
    # )

    indices = data.index.values

    # NOTE: (~isinstance(tmp_tuple, tuple)) does not work, nor does is_named_tuple

    if len(data) == 5:
        tmp_tuple = data.loc[indices[0], "rating"]
        try:
            r1 = trueskill.Rating(tmp_tuple)
        except:
            r1 = trueskill.Rating(tmp_tuple[0])

        tmp_tuple = data.loc[indices[1], "rating"]
        try:
            r2 = trueskill.Rating(tmp_tuple)
        except:
            r2 = trueskill.Rating(tmp_tuple[0])

        tmp_tuple = data.loc[indices[2], "rating"]
        try:
            r3 = trueskill.Rating(tmp_tuple)
        except:
            r3 = trueskill.Rating(tmp_tuple[0])

        tmp_tuple = data.loc[indices[3], "rating"]
        try:
            r4 = trueskill.Rating(tmp_tuple)
        except:
            r4 = trueskill.Rating(tmp_tuple[0])

        tmp_tuple = data.loc[indices[4], "rating"]
        try:
            r5 = trueskill.Rating(tmp_tuple)
        except:
            r5 = trueskill.Rating(tmp_tuple[0])

        l = [(r1,), (r2,), (r3,), (r4,), (r5,)]
    else:
        raise ValueError(f"Unexpected number of ratings: {len(data)}")

    return l

