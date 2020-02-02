import math

from util import sort_count_pairs

def count_tokens(tokens):
    '''
    Counts each distinct token (item or entity) in a list of tokens

    Inputs:
        tokens: list of tokens (must be hashable/comparable)

    Returns: list (token, number of occurrences).
    '''
    i = 0
    count = {}
    while i < len(tokens): #Please use a for loop next time.
        token = tokens[i]
        n = count.get(token, 0)
        count[token] = n + 1
        i += 1
    return list(count.items())

def find_top_k(tokens, k):
    '''
    Find the k most frequently occurring tokens

    Inputs:
        tokens: list of tokens (must be hashable/comparable)
        k: a non-negative integer

    Returns: sorted list of the top k tuples
    '''

    # Error checking (DO NOT MODIFY)
    err_msg = "In find_top_k, k must be a non-negative integer"
    assert k >= 0, err_msg
    list_top_tokens = sort_count_pairs(count_tokens(tokens))
    if k > len(list_top_tokens):
        return list_top_tokens
    else:
        return list_top_tokens[0:k]


def find_min_count(tokens, min_count):
    '''
    Find the tokens that occur at least min_count times

    Inputs:
        tokens: a list of tokens (must be hashable/comparable)
        min_count: integer

    Returns: sorted list of tuples
    '''
    count_list = count_tokens(tokens)
    min_list = []
    for key, value in count_list:
        if value >= min_count:
            min_list.append((key, value))
    return sort_count_pairs(min_list)

def get_freq(token, docs):
    '''
    Count the number of docs that contains given token.

    Inputs;
        token: a token
        docs: a list of lists of tokens

    Returns: int
    '''
    freq = 0
    for i in docs:
        c = 0 #whether token exist in a doc
        for j in i:
            if j == token:
                c = 1
                break
        freq += c
    return freq


def rank_𝗍𝖿_𝗂𝖽𝖿(doc, docs):
    '''
    For a document in a list of documents, rank their tokens in order of tf_idf.

    Inputs:
        doc: a list of tokens
        docs: a list of lists of tokens

    Returns: list of tokens
    '''
    count = sort_count_pairs(count_tokens(doc))
    max_freq = count[0][1]
    tf_idf = []
    for i in count:
        tf = 0.5 + 0.5 * i[1] / max_freq
        idf = math.log(len(docs) / get_freq(i[0], docs))
#Recomputes the number of documents a word occurs in for every word (or every unique word) in every document.]
#Your code delivers the expected result. However, you called get_freq() on all tokens in a document. 
#Please note that the idf score is unique for every unique token, no matter in which document the token is. As a result, you might want to only loop through the entire documents once and find the idf score for all unique tokens altogether.

        tf_idf.append((i[0], tf * idf))
    tf_idf = sort_count_pairs(tf_idf)
    doc_salient = [i[0] for i in tf_idf]
    return doc_salient

def find_most_salient(docs, k):
    '''
    Find the k most salient tokens in each document

    Inputs:
        docs: a list of lists of tokens
        k: integer

    Returns: list of sorted list of tokens
     (inner lists are in decreasing order of tf-idf score)
    '''
    err_msg = "In find_most_salient, k must be a non-negative integer"
    assert k >= 0, err_msg
    most_salient = []
    for doc in docs:
        if doc == []:
            most_salient.append([])
        else:
            doc_salient = rank_𝗍𝖿_𝗂𝖽𝖿(doc, docs)
            if k > len(doc_salient):
                most_salient.append(doc_salient)
            else:
                most_salient.append(doc_salient[0:k])
#[See Design Penalty: Should have applied a function from basic_algorithms.py instead of re-writing that functionality (once)]
#You might find the function find_top_k() useful instead of lines 132-135.

    return most_salient