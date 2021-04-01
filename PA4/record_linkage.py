# CS122: Linking restaurant records in Zagat and Fodor's data sets
#
# Antony Awad


import numpy as np
import pandas as pd
import jellyfish
import util


def create_dataframes():
    '''
    Initialize the csv files into two pandas dataframes, then use the links
    csv to find matches and build these into two 6 column dataframes.

    Output:
        zagat (dataframe object)
        fodors (dataframe object)
        matches (dataframe object)
        unmatches (dataframe object)
    '''
    zagat = pd.read_csv('zagat.csv', names=['z_Restaurant', 'z_City',
        'z_Address'], index_col=0)
    fodors = pd.read_csv('fodors.csv', names=['f_Restaurant', 'f_City',
        'f_Address'], index_col=0)
    known_links = pd.read_csv('known_links.csv', names=['Zagat_ID',
        'Fodors_ID'])

    matches = pd.concat([zagat.iloc[known_links['Zagat_ID']].reset_index
        (drop = True), fodors.iloc[known_links['Fodors_ID']].reset_index
        (drop = True)], axis = 1)

    unmatches = pd.concat([zagat.sample(1000, replace=True, random_state=1234).
        reset_index(drop = True), fodors.sample(1000, replace=True, 
        random_state=5678).reset_index(drop=True)], axis = 1)

    return zagat, fodors, matches, unmatches


def return_frequencies(matches, unmatches):
    '''
    Takes matches and unmatches dataframes and returns the frequency of their
    tuples being matches and unmatches.

    Input:
        matches (dataframe)
        unmatches (dataframe)
    Output:
        Matches and unmatches frequency dictionaries
    '''
    return determine_frequencies(matches), determine_frequencies(unmatches)


def determine_frequencies(values):
    '''
    Helper function for return_frequencies. Takes a dataframe, applies the
    jaro_winkler distance formula, turns these into values of low, medium,
    high, and then counts the frequency of that triple.

    Inputs:
        values (dataframe)
    Outputs:
        frequencies (dict): maps triples to relative frequencies
    '''
    frequencies = init_frequencies()

    for _, row in values.iterrows():
        name_cat = util.get_jw_category(jellyfish.jaro_winkler(
            row.z_Restaurant, row.f_Restaurant))
        city_cat = util.get_jw_category(jellyfish.jaro_winkler(
            row.z_City, row.f_City))
        address_cat = util.get_jw_category(jellyfish.jaro_winkler(
            row.z_Address, row.f_Address))
        frequencies[tuple([name_cat, city_cat, address_cat])] += 1
    total = sum(frequencies.values())
    return {k:float(v/total) for (k, v) in frequencies.items()}


def init_frequencies():
    '''
    Helper function for match_estimates. Initializes frequency dictionary
    with one of each kind of tuple (27 total).
    
    Output: frequency_count (dict)
    '''
    frequency_count = {}
    lst = ['low', 'medium', 'high']
    for i in lst:
        for j in lst:
            for k in lst:
                combo = tuple([i, j, k])
                frequency_count[combo] = 0
    return frequency_count


def sorter(match_frequencies, unmatch_frequencies, mu, lambda_):
    '''
    Function that uses the match and unmatch frequencies to sort tuples
    into three lists.

    Input:
        match_frequencies, unmatch_frequencies (dict): maps tuples to freq
        mu (float): maximum false positive rate
        lambda (float): maximum false negative rate
    Output: three sets of possible_tuples, match_tuples, unmatch_tuples
    '''
    possible_tuples = set()
    m_u_ratios = []
    ranked_lst = []
    
    for key, value in unmatch_frequencies.items():
        if value == 0:
            if match_frequencies[key] == 0:
                possible_tuples.add(key)
            else:
                ranked_lst.append(key)
        else:
            m_u_ratios.append(tuple([match_frequencies[key] / value, key]))
    m_u_ratios.sort(reverse=True)
    for _, triple in m_u_ratios:
        ranked_lst.append(triple)

    return create_sets(ranked_lst, possible_tuples, match_frequencies, 
                        unmatch_frequencies, mu, lambda_)


def create_sets(ranked_lst, possible_tuples, match_frequencies, 
                unmatch_frequencies, mu, lambda_):
    '''
    Helper function for sorter. Takes sorted ratios and partitions the tuples
    match_tuples, possible_tuples, and unmatch_tuples.

    Input:
        ranked_lst (lst): an intermediary sorted list
        possible_tuples (set)
        match_frequencies, unmatch_frequencies (dict): maps tuples to freq
        mu (float): maximum false positive rate
        lambda (float): maximum false negative rate
    Output: possible_tuples, match_tuples, unmatch_tuples (sets)
    '''
    match_tuples = set()
    unmatch_tuples = set()
    u_sum = 0
    for triple in ranked_lst:
        u_sum += unmatch_frequencies[triple]
        if u_sum > mu:
            break
        match_tuples.add(triple)
    m_sum = 0
    for triple in reversed(ranked_lst):
        m_sum += match_frequencies[triple]
        if m_sum > lambda_:
            break
        unmatch_tuples.add(triple)

    remaining1 = set(ranked_lst) - (match_tuples|unmatch_tuples)
    possible_tuples = possible_tuples|remaining1

    return possible_tuples, match_tuples, unmatch_tuples


def create_match_df(zagat, fodors, possible_tuples, match_tuples, 
                    unmatch_tuples, block_on_city):
    '''
    Goes through every combination of rows between the zagat and fodors 
    dataframes and determines whether the rows are matches, unmatches, or 
    possible matches and constructs correspondent dataframes.

    Input:
        zagat, fodors (dataframes)
        possible_tuples, match_tuples, unmatch_tuples (sets): contain
            correspondent tuples that add up to 27 total
        block_on_city (bool): whether or not to block on city
    Output:
        (matches_df, possible_matches_df, unmatches_df) 3-tuple of dataframe
            objects
    '''
    master_dict = {'possible_lst_z':[], 'possible_lst_f':[], 'match_lst_z':[],
        'match_lst_f':[], 'unmatch_lst_z':[], 'unmatch_lst_f':[]}
    for i, z_row in zagat.iterrows():
        for j, f_row in fodors.iterrows():
            if block_on_city is True:
                if z_row.z_City == f_row.f_City:
                    master_dict = create_index_lists(z_row, f_row, 
                        possible_tuples, match_tuples, unmatch_tuples, 
                        master_dict, i, j)
            else:
                master_dict = create_index_lists(z_row, f_row, 
                    possible_tuples, match_tuples, unmatch_tuples, 
                    master_dict, i, j)

    matches_df = final_constructor(zagat, fodors,
        master_dict['match_lst_z'], master_dict['match_lst_f'])
    possible_matches_df = final_constructor(zagat, fodors,
        master_dict['possible_lst_z'], master_dict['possible_lst_f'])
    unmatches_df = final_constructor(zagat, fodors,
        master_dict['unmatch_lst_z'], master_dict['unmatch_lst_f'])

    return (matches_df, possible_matches_df, unmatches_df)


def final_constructor(zagat, fodors, indexZ, indexF):
    '''
    Helper function for create_match_df. Takes the dataframes and lists of
    the appropriate indices and brings them together into one dataframe.

    Input:
        zagat, fodors (dataframe objects)
        indexZ, indexF (lst): list of indices for zagat and fodors
    Output: concatenated dataframe with 6 columns
    '''
    return pd.concat([zagat.iloc[indexZ].reset_index(drop = True), 
        fodors.iloc[indexF].reset_index(drop = True)], axis = 1)


def create_index_lists(z_row, f_row, possible_tuples, match_tuples, 
                        unmatch_tuples, master_dict, i, j):
    '''
    Helper function for create_match_df. Takes rows of zagat and fodors and 
    assigns their respective indices to lists dependent on their match 
    relation.

    Input:
        z_row, f_row (row objects)
        possible_tuples, match_tuples, unmatch_tuples (lst): lists of 
            correspondent tuples
        i, j (int): indices
    Output:
        master_dict (dict): maps list name to list of indices
    '''
    name_cat = util.get_jw_category(jellyfish.jaro_winkler(
        z_row.z_Restaurant, f_row.f_Restaurant))
    city_cat = util.get_jw_category(jellyfish.jaro_winkler(z_row.z_City, 
        f_row.f_City))
    address_cat = util.get_jw_category(jellyfish.jaro_winkler(z_row.z_Address, 
        f_row.f_Address))
    current_triple = tuple([name_cat, city_cat, address_cat])
    if current_triple in possible_tuples:
        master_dict['possible_lst_z'].append(i)
        master_dict['possible_lst_f'].append(j)
    elif current_triple in match_tuples:
        master_dict['match_lst_z'].append(i)
        master_dict['match_lst_f'].append(j)
    elif current_triple in unmatch_tuples:
        master_dict['unmatch_lst_z'].append(i)
        master_dict['unmatch_lst_f'].append(j)

    return master_dict
    

def find_matches(mu, lambda_, block_on_city=False):
    '''
    Master function that creates initial dataframes, analyzes them for matches,
    possible matches, and unmatches, then creates three final dataframes.

    Input:
        mu (float): maximum false positive rate
        lambda (float): maximum false negative rate
        block_on_city (bool): indicate whether to block on city or not
    Output:
        3-tuple containing dataframes matches, possible matches, and unmatches
    '''
    zagat, fodors, matches, unmatches = create_dataframes()
    match_frequencies, unmatch_frequencies = return_frequencies(matches, 
        unmatches)
    possible_tuples, match_tuples, unmatch_tuples = sorter(match_frequencies,
        unmatch_frequencies, mu, lambda_)

    return create_match_df(zagat, fodors, possible_tuples, match_tuples, 
                            unmatch_tuples, block_on_city)
                                                        ###GRADER COMMENT:
                                                        #Great job on this!
if __name__ == '__main__':
    matches, possibles, unmatches = \
        find_matches(0.005, 0.005, block_on_city=True)

    print("Found {} matches, {} possible matches, and {} "
          "unmatches with no blocking.".format(matches.shape[0],
                                               possibles.shape[0],
                                               unmatches.shape[0]))
