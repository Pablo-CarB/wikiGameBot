import networkx as nx            # used for building graphs
from networkx import DiGraph
import sys                       # used for interacting w/ system
sys.path.append("./")            # adds wikiLinkRetrieval to path
import wikiLinkRetrieval as wiki # used for finding wikipedia links
from typing import Set           # just needed for signatures/type hinting     
from copy import deepcopy        # used for copying the list
import pickle                    # stores graph
    
def sprawl(starts: Set[str],iterations: int) -> DiGraph:
    """given a set of starting urls to wikipedia articles 

    Args:
        starts (Set[str]): a set of starting nodes
        iterations (int): the number of layers away from the starting articles to expand

    Returns:
        _type_: _description_
    """
    wikiGraph = nx.DiGraph()

    s1 = starts
    s2 = set()

    while (iterations > 0) and (len(s1) != 0):
        
        for url in s1:
            article_name = wiki.clean_wiki_link(url)
            current = (article_name, url)

            wikiGraph.add_node(current)
            adj = wiki.(url)

            edges = [(wiki.clean_wiki_link(adj_article),adj_article) for adj_article in adj]

            s2.update(adj)
            
            wikiGraph.add_edges_from([(current,e) for e in edges])

        s1 = s2
        s2 = set()

        iterations -= 1
    return wikiGraph

# Some influential wikipedia lists
most_referenced = "https://en.wikipedia.org/wiki/Wikipedia:Most-referenced_articles"
countries =  "https://simple.wikipedia.org/wiki/List_of_countries"
disciplines = "https://en.wikipedia.org/wiki/Outline_of_academic_disciplines"

# start_set = set(most_referenced,countries,disciplines)
start_func = time.time()
G = sprawl(set({"https://en.wikipedia.org/wiki/Repatriation_of_Ashanti_Gold_Regalia_from_the_UK_to_Ghana"}),4)
end_func = time.time()

with open('wikiGraph2.pickle', 'wb') as file:
        pickle.dump(G, file)