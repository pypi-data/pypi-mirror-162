import numpy as np
import networkx as nx


def nodes_centrality_measures(A):

    """
    This function extracts from an adjacency matrix dictionaries of several centrality measures: "degree", "closeness", "eigenvector", "betweeness".

    Parameters
    ----------
        A : numpy.ndarray
            The graph adjacency matrix

    Returns
    --------
        (dictionary, dictionary, dictionary, dictionary,)
            A tuple of dictionaries matching in order: "degree", "closeness", "eigenvector", "betweeness".
    """

    G = nx.from_numpy_array(A)

    node_pageranks = nx.pagerank(G)
    node_degree = nx.degree_centrality(G)
    node_clos = nx.closeness_centrality(G)
    node_betw = nx.betweenness_centrality(G)

    return node_pageranks, node_degree, node_clos, node_betw
