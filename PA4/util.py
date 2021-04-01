# Utility Function for Record Linkage Assignment

THRESH1 = 0.8
THRESH2 = 1.0

def get_jw_category(j):
    '''
    Convert a Jaro-Winkler score into a categorical: low, medium, high
    using fixed thresholds.

    Inputs:
        j (double): value between 0 and 1 (inclusive)

    Returns: string
    '''

    if j < THRESH1:
        return "low"
    if j < THRESH2:
        return "medium"
    return "high"
