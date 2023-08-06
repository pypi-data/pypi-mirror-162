# Import libraries
from pathlib import Path
import pandas as pd
import numpy as np

# Constants
NUM_COMPARISONS_PER_QUESTION = 5  # 
DATA_DIR = Path.cwd().joinpath(
    "data"
)

# Functions
def create_flows_and_comparisons_from_raw(filename="raw_survey_data.csv", write_new_files=True, DATA_DIR=DATA_DIR):
    """
    :Info: Process the example raw data. 
            Converts multiple surveys into two matrices.
    :param filename:str
    :param write_new_files:bool
    :param DATA_DIR:Path to data directory
    :returns flow_matrix:DataFrame
    :returns comparison_matrix:DataFrame
    """
    raw_df = pd.read_csv(DATA_DIR.joinpath(filename), header=0)
    
    # Get values of header row, ignoring the first (empty) column
    UNIQ_OPTIONS = raw_df.columns[1:].unique()

    NUM_SURVEY_RESPONDENTS = len(raw_df)  # len does not include header row
    NUM_UNIQ_OPTIONS = len(UNIQ_OPTIONS)

    print(f"# of survey takers: {NUM_SURVEY_RESPONDENTS}\n# of unique options: {NUM_UNIQ_OPTIONS}")

    # Create matrix of respondents x unique option x unique option
    #   with eventual collapse to unique option x unique option. 
    #     When 2D, only use half the diagonal (i.e. across the diagonal is * -1).
    M = np.zeros((NUM_SURVEY_RESPONDENTS, NUM_UNIQ_OPTIONS, NUM_UNIQ_OPTIONS), dtype=int)

    # Add 2D counter matrix for number of comparisons between i, j (& j, i)
    num_comparisons_matrix = np.zeros((NUM_UNIQ_OPTIONS, NUM_UNIQ_OPTIONS), dtype=int)

    for p in range(NUM_SURVEY_RESPONDENTS):
        # If each respondent answered multiple questions, loop multiple groups of questions
        #   (e.g. for i in range(NUM_GROUPS):)  

        # Return the columns that were ranked, in order, for a particular respondent (in a particular group)
        tmp_cols = raw_df.iloc[p, 1:].dropna().sort_values().index.values
        
        num_ranked_in_group = len(tmp_cols)
        if num_ranked_in_group != NUM_COMPARISONS_PER_QUESTION:
            print(f"WARNING: Only {num_ranked_in_group} (of {NUM_COMPARISONS_PER_QUESTION}) options were ranked in {raw_df.iloc[p, 0]}.")

        # Determine the indices associated with the selected columns
        ranked_within_group = [int(raw_df.columns.get_loc(col)) for col in tmp_cols]
        # print(f"options: {ranked_within_group}")  # TMP
        indices = np.subtract(ranked_within_group, 1)  # Subtract 1 to deal with empty first column header
        # print(f"New indices: {indices}")  # TMP

        if M[p].trace() != 0:
            raise ValueError("Diagonal values should be 0")

        # Update the matrix
        #   For example, when there are 5 NUM_COMPARISONS_PER_QUESTION:
        #     Add 1 for all 1st -> {2,3,4,5} positions, 2nd -> {3/4/5}, 3rd -> {4, 5}, & 4->5
        #     Some respondents may rank fewer than max NUM_COMPARISONS_PER_QUESTION, so handle flexibly
        for j in range(num_ranked_in_group):  # When len() == 0, will not run
            M[p, indices[j], indices[j+1:]] += 1  # For higher ranked option "winners"
            M[p, indices[j+1:], indices[j]] -= 1  # For lower ranked option "losers"

            # num_comparisons_matrix notes how often pairs were ranked (independent of order)
            num_comparisons_matrix[indices[j], indices[j+1:]] += 1
            num_comparisons_matrix[indices[j+1:], indices[j]] += 1

    # When values >1 or <-1, normalize to 1/-1.
    #   This is to ensure each survey respondent is weighted equally.
    M = np.where(M > 1, 1, M)
    M = np.where(M < -1, -1, M)

    # Sum the rankings
    M_sum = np.sum(M, axis=0)

    # If values are to be normalized (i.e. NORM_FULL_M), 
    #   use the following code to ensure that all charge comparisons are {-1, 0, 1} 
    #   (as opposed to summation of prosecutor rankings for that charge pairing)
    NORM_FULL_M = False
    if NORM_FULL_M:
        M_sum = np.where(M_sum > 1, 1, M_sum)
        M_sum = np.where(M_sum < -1, -1, M_sum)

    # Confirm that the square matrix is anti-symmetric
    if (M_sum + M_sum.transpose()).sum().sum() != 0:
        raise ValueError("Matrix is not anti-symmetrical.  Sum of upper & lower diagonal is not 0.")

    # Create the resulting DataFrame from the aggregation of all prosecutor data (i.e. flatten)
    #   i.e. collapse 3D->2D, then specify indices and cols
    flow_matrix = pd.DataFrame(data = M_sum,  index = UNIQ_OPTIONS,  columns = UNIQ_OPTIONS)
    # flow_matrix.reset_index(inplace=True)

    # Create the resulting DataFrame from the times each thing was seen (i.e. flatten)
    comparison_matrix = pd.DataFrame(data = num_comparisons_matrix,  index = UNIQ_OPTIONS,  columns = UNIQ_OPTIONS)
    # comparison_matrix.reset_index(inplace=True)

    if write_new_files:
        flow_matrix.to_csv(DATA_DIR.joinpath("flow_matrix.csv"))
        comparison_matrix.to_csv(DATA_DIR.joinpath("comparison_matrix.csv"))

    return flow_matrix, comparison_matrix
