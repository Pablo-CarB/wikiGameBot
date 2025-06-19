import networkx as nx            # used for building graphs
from networkx import DiGraph
import sys                       # used for interacting w/ system
sys.path.append("./")            # adds wikiLinkRetrieval to path
import wikiLinkRetrieval as wiki # used for finding wikipedia links
from typing import Set           # just needed for signatures/type hinting     
from copy import deepcopy        # used for copying the list
import pickle

def sprawl(starts: Set[str],iterations: int):
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
        print(s1)
        for url in s1:
            current = (wiki.clean_wiki_link(url), url)
            print(wiki.clean_wiki_link(url))
            wikiGraph.add_node(current)

            adj = wiki.get_wikipedia_links(url)
            edges = [(wiki.clean_wiki_link(adj_article),adj_article) for adj_article in adj]

            for article in adj:
                s2.add(article)

            for e in edges:
                wikiGraph.add_edges_from([(current,e)])
        s1 = deepcopy(s2)
        s2.clear()
            
        iterations -= 1
    return wikiGraph

# Some influential wikipedia lists
most_referenced = "https://en.wikipedia.org/wiki/Wikipedia:Most-referenced_articles"
countries =  "https://simple.wikipedia.org/wiki/List_of_countries"
disciplines = "https://en.wikipedia.org/wiki/Outline_of_academic_disciplines"

# start_set = set(most_referenced,countries,disciplines)


with open('wikiGraph2.pickle', 'wb') as file:
        pickle.dump(sprawl(set({"https://en.wikipedia.org/wiki/Repatriation_of_Ashanti_Gold_Regalia_from_the_UK_to_Ghana"}),2), file)