import networkx as nx            # used for building graphs
from networkx import DiGraph     # typing for graph output
import sys                       # used for interacting w/ system
sys.path.append("./src")         # adds wikiLinkRetrieval to path
import wikiLinkRetrieval as wiki # used for finding wikipedia links
from typing import Set           # just needed for signatures/type hinting     
import pickle                    # stores graph
import time
    
def sprawl(starts: Set[str],iterations: int) -> nx.DiGraph:
    """given a set of starting urls to wikipedia articles will essentially perform bfs for the specified number of iterations 
    scraping the graph data and storing it in a networkx digraph. On the last layer will perform one last iteration only adding
    edges that point to urls already in the graph (this is to reduce the number of articles with no out degree)

    Args:
        starts (Set[str]): a set of starting article urls
        iterations (int): the number of layers away from the starting articles to expand

    Returns:
        wikiGraph (nx.DiGraph): a subgraph of the wikipedia graph
    """
    wikiGraph = nx.DiGraph()

    s = starts
    original_iterations = iterations

    while (iterations > 0) and (len(s) != 0):

        
        adjacency_dict = wiki.get_adj_wiki_lists(s)

        for key in adjacency_dict.keys():
            wikiGraph.add_edges_from([(key, adj) for adj in adjacency_dict.get(key)])

        s.clear()
        
        for value in adjacency_dict.values():
             s|=value

        iterations -= 1
        del adjacency_dict

    final_layer_nodes = set(s)
    final_adjacency = wiki.get_adj_wiki_lists(final_layer_nodes)
    
    # on the last layer add all of the edges that connect the last layer to any nodes already in the graph
    # this stops the majority of node from being childless/leafs because the graph size grows expenoential w.r.t to layer
    for key in final_adjacency.keys():
        internal_links = [adj for adj in final_adjacency[key] if wikiGraph.has_node(adj)]
        wikiGraph.add_edges_from([(key, adj) for adj in internal_links])

    return wikiGraph

# Some influential wikipedia lists
most_referenced = "https://en.wikipedia.org/wiki/Wikipedia:Most-referenced_articles"
countries =  "https://simple.wikipedia.org/wiki/List_of_countries"
disciplines = "https://en.wikipedia.org/wiki/Outline_of_academic_disciplines"

# start_set = set(most_referenced,countries,disciplines)
start_time = time.time()
G = sprawl(set({countries}),3)
print(time.time()-start_time)
print(len(G.nodes))
with open('CountryGraphL3.pickle', 'wb') as file:
        pickle.dump(G, file)
