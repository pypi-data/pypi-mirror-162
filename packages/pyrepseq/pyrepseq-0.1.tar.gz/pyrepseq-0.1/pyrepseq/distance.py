from .main import aminoacids

import numpy as np

from scipy.spatial.distance import squareform

from Levenshtein import hamming as hamming_distance
from Levenshtein import distance as levenshtein_distance


def pdist(strings, metric=None, dtype=np.uint8, **kwargs):
    """Pairwise distances between collection of strings.
       (`scipy.spatial.distance.pdist` equivalent for strings)

    Parameters
    ----------
    strings : iterable of strings
        An m-length iterable.
    metric : function, optional
        The distance metric to use. Default: Levenshtein distance.
    dtype : np.dtype
        data type of the distance matrix, default: np.uint8

    Returns
    -------
    Y : ndarray
        Returns a condensed distance matrix Y.  For
        each :math:`i` and :math:`j` (where :math:`i<j<m`), where m is the number
        of original observations. The metric ``dist(u=X[i], v=X[j])``
        is computed and stored in entry 
        ``m * i + j - ((i + 2) * (i + 1)) // 2``.
    """
    if metric is None:
        metric = levenshtein_distance
    strings = list(strings)
    m = len(strings)
    dm = np.empty((m * (m - 1)) // 2, dtype=dtype)
    k = 0
    for i in range(0, m-1):
        for j in range(i+1, m):
            dm[k] = metric(strings[i], strings[j], **kwargs)
            k += 1
    return dm

def cdist(stringsA, stringsB, metric=None, dtype=np.uint8, **kwargs):
    """ Compute distance between each pair of the two collections of strings.
        (`scipy.spatial.distance.cdist` equivalent for strings)

    Parameters
    ----------
    stringsA : iterable of strings
        An mA-length iterable.
    stringsB : iterable of strings
        An mB-length iterable.
    metric : function, optional
        The distance metric to use. Default: Levenshtein distance.
    dtype : np.dtype
        data type of the distance matrix, default: np.uint8

    Returns
    -------
    Y : ndarray
        A :math:`m_A` by :math:`m_B` distance matrix is returned.
        For each :math:`i` and :math:`j`, the metric
        ``dist(u=XA[i], v=XB[j])`` is computed and stored in the
        :math:`ij` th entry.
    """
    if metric is None:
        metric = levenshtein_distance
    stringA = list(stringsA)
    stringB = list(stringsB)
    mA = len(stringA)
    mB = len(stringB)

    dm = np.empty((mA, mB), dtype=dtype)
    for i in range(0, mA):
        for j in range(0, mB):
            dm[i, j] = metric(stringA[i], stringB[j], **kwargs)
    return dm


def levenshtein_neighbors(x, alphabet=aminoacids):
    """Iterator over Levenshtein neighbors of a string x"""
    # deletion
    for i in range(len(x)):
        # only delete first repeated amino acid
        if (i > 0) and (x[i] == x[i-1]):
            continue
        yield x[:i]+x[i+1:]
    # replacement
    for i in range(len(x)):
        for aa in alphabet:
            # do not replace with same amino acid
            if aa == x[i]:
                continue
            yield x[:i]+aa+x[i+1:]
    # insertion
    for i in range(len(x)+1):
        for aa in alphabet:
            # only insert after first repeated amino acid
            if (i>0) and (aa == x[i-1]):
                continue
            # insertion
            yield x[:i]+aa+x[i:]

def hamming_neighbors(x, alphabet=aminoacids, variable_positions=None):
    """Iterator over Hamming neighbors of a string x.

    Parameters
    ----------
    alphabet : iterable of characters
    variable_positions: iterable of positions to be varied (default: all)
    """

    if variable_positions is None:
        variable_positions = range(len(x))
    for i in variable_positions:
        for aa in alphabet:
            if aa == x[i]:
                continue
            yield x[:i]+aa+x[i+1:]

def _flatten_list(inlist):
    return [item for sublist in inlist for item in sublist]

def next_nearest_neighbors(x, neighborhood, maxdistance=2):
    """Set of next nearest neighbors of a string x.

    Parameters
    ----------
    alphabet : iterable of characters
    neighborhood: neighborhood iterator
    maxdistance : go up to maxdistance nearest neighbor

    Returns
    -------
    set of neighboring sequences
    """
   
    neighbors = [list(neighborhood(x))]
    distance = 1
    while distance < maxdistance:
        neighbors_dist = []
        for x in neighbors[-1]:
            neighbors_dist.extend(neighborhood(x))
        neighbors.append(set(neighbors_dist))
        distance += 1
    return set(_flatten_list(neighbors))
 
def find_neighbor_pairs(seqs, neighborhood=hamming_neighbors):
    """Find neighboring sequences in a list of unique sequences.

    Parameters
    ----------
    neighborhood: callable returning an iterable of neighbors

    Returns
    -------
    list of tuples (seq1, seq2)
    """
    reference = set(seqs)
    pairs = []
    for x in set(seqs):
        for y in (set(neighborhood(x)) & reference):
            pairs.append((x, y))
        reference.remove(x)
    return pairs

def find_neighbor_pairs_index(seqs, neighborhood=hamming_neighbors):
    """Find neighboring sequences in a list of unique sequences.

    Parameters
    ----------
    neighborhood: callable returning an iterable of neighbors

    Returns
    -------
    list of tuples (index1, index2)
    """
    reference = set(seqs)
    seqs_list = list(seqs)
    pairs = []
    for i, x in enumerate(seqs):
        for y in (set(neighborhood(x)) & reference):
            pairs.append((i, seqs_list.index(y)))
    return pairs

def calculate_neighbor_numbers(seqs, neighborhood=levenshtein_neighbors):
    """Calculate the number of neighbors for each sequence in a list.

    Parameters
    ----------
    seqs: list of sequences
    neighborhood: function returning iterator over neighbors
    
    Returns
    -------
    integer array of number of neighboring sequences
    """
    reference = set(seqs)
    return np.array([len(set(neighborhood(seq)) & reference) for seq in seqs])

def _dist1(x, reference):
    """ Is the string x a Hamming distance 1 away from any of the kmers in the reference set"""
    for i in range(len(x)):
        for aa in aminoacids:
            if aa == x[i]:
                continue
            if x[:i]+aa+x[i+1:] in reference:
                return True
    return False

def _dist2(x, reference):
    """ Is the string x a Hamming distance 2 away from any of the kmers in the reference set"""
    for i in range(len(x)):
        for j in range(i+1, len(x)):
            for aai in aminoacids:
                if aai == x[i]:
                    continue
                si = x[:i]+aai+x[i+1:]
                for aaj in aminoacids:
                    if aaj == x[j]:
                        continue
                    if si[:j]+aaj+si[j+1:] in reference:
                        return True
    return False

def _dist3(x, reference):
    """ Is the string x a Hamming distance 3 away from any of the kmers in the reference set"""
    for i in range(len(x)):
        for j in range(i+1, len(x)):
            for k in range(j+1, len(x)):
                for aai in aminoacids:
                    if aai == x[i]:
                        continue
                    si = x[:i]+aai+x[i+1:]
                    for aaj in aminoacids:
                        if aaj == x[j]:
                            continue
                        sij = si[:j]+aaj+si[j+1:]
                        for aak in aminoacids:
                            if aak == x[k]:
                                continue
                            if sij[:k]+aak+sij[k+1:] in reference:
                                return True
    return False

def nndist_hamming(seq, reference, maxdist=4):
    """Calculate the nearest-neighbor distance by Hamming distance

    Parameters
    ----------
    seqs: list of sequences
    seq: sequence instance
    reference: set of referencesequences
    maxdist: distance beyond which to cut off the calculation (currently needs to be <=4)

    Returns
    -------
    distance of nearest neighbor 

    Note: This function does not check whether neighbors are of same length.
    """
    if maxdist>4:
        raise NotImplementedError
    if seq in reference:
        return 0
    if (maxdist==1) or _dist1(seq, reference):
        return 1
    if (maxdist==2) or _dist2(seq, reference):
        return 2
    if (maxdist==3) or _dist3(seq, reference):
        return 3
    return 4
