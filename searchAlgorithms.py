from typing import List
import wikiLinkRetrieval as wiki
from gensim.models import KeyedVectors
import numpy as np
import heapq

def bfs(start : str,target : str) -> List[str]:
    """An implementation of BFS that plays the wikiGame, given the url for the start and end pages 

    Args:
        start (str): the url for the start page
        target (str): the url for the end page

    Returns:
        List[str]: the path from the start page to the end page
    """
    queue = [(start, [start])]
    seen = set()

    while queue:
        current,path = queue.pop(0)
        seen.add(current)

        if current == target:
            return path + [current]

        neighbours = wiki.get_wikipedia_links(current)

        if target in neighbours:
            return path + [target]

        for node in neighbours:
            if node not in seen:
                queue.append((node,path + [node]))
    return None
    

def phrase_to_vec(phrase: str, model: KeyedVectors, ) -> np.ndarray:
    """Given a string and a KeyedVectors model will attempt to find the phrase vector in the model
    and if it can't will average the available vectors from the words that make up the phrase. Will return
    the zero vector if none of the words inside of the phrase exist in the model and thus no average can be made.

    Args:
        phrase (str): the phrase being searched
        model (KeyedVectors): the vector embedding model

    Returns:
        np.ndarray: the final phrase vector being output
    """
    if phrase in  model:
        return model.get_vector(phrase)

    fragments = phrase.replace("_"," ").split(" ")
    vec = []

    for piece in fragments:
        try:
            if piece in model:
                vec.append(model.get_vector(piece))
            elif piece.lower() in model:
                vec.append(model.get_vector(piece.lower()))
            fragment_vec = model.get_vector(piece)
            return fragment_vec
        except KeyError:
            continue
    if vec != []:
        return np.mean(vec, axis=0)
    else:
        return np.zeros(model.vector_size)


def vecSimSearch(start : str,target : str, model : KeyedVectors) -> List[str]:
    """A greedy approach to the wikiGame which uses article name vector embeddings. The algorithm
    works by always traversing to the adjacent article whose name vector has the highest cosine similarity to
    the target article's name vector.

    Args:
        start (str): the url for the start page
        target (str): the url for the end page
        model (KeyedVectors): the vector embedding used

    Returns:
        List[str]: the path from the start page to the end page
    """
    start_vec = phrase_to_vec(wiki.clean_wiki_link(start),model)
    target_vec = phrase_to_vec(wiki.clean_wiki_link(target),model)
    target_norm = target_norm = np.linalg.norm(target_vec)

    # each element in the queue forms a tuple (distance_to_target, current_node, current_path)
    queue = []
    heapq.heappush(queue,(0, start, [start]))
    seen = set()

    while queue:
        distance,current,path = heapq.heappop(queue)

        # this check is also needed because several articles can have the same neighbour and
        # add it to the queue, then despite it being in the seen set it will still be popped out of the queue
        if current in seen:
            continue

        seen.add(current)

        if current == target:
            return path + [current]

        neighbours = wiki.get_wikipedia_links(current)

        if target in neighbours:
            return path + [target]
        

        for node in neighbours:
            if node not in seen:
                node_vec = phrase_to_vec(wiki.clean_wiki_link(node), model)

                node_norm = np.linalg.norm(node_vec)

                if node_norm*target_norm > 0:
                    cosine_sim = np.dot(node_vec,target_vec)/(node_norm*target_norm)
                else:
                    cosine_sim = 0

                heapq.heappush(queue,(-cosine_sim, node ,path + [current]))
    return None

def vecSimSearch2(start : str,target : str, model : KeyedVectors) -> List[str]:
    """A greedy approach to the wikiGame which uses article name vector embeddings. The algorithm
    works by always traversing to the adjacent article whose name vector has the highest cosine similarity to
    the target article's name vector.

    Args:
        start (str): the url for the start page
        target (str): the url for the end page
        model (KeyedVectors): the vector embedding used

    Returns:
        List[str]: the path from the start page to the end page
    """
    start_vec = phrase_to_vec(wiki.clean_wiki_link(start),model)
    target_vec = phrase_to_vec(wiki.clean_wiki_link(target),model)
    target_norm = target_norm = np.linalg.norm(target_vec)

    def target_cosine_sim(node_vec):
        node_norm = np.linalg.norm(node_vec)
        if node_norm*target_norm > 0:
            return np.dot(node_vec,target_vec)/(node_norm*target_norm)
        else:
            return 0

    # each element in the queue forms a tuple (distance_to_target, current_node, current_path)
    seen = set()
    path = []
    current = start

    while current != None:
        path.append(current)
        seen.add(current)

        if current == target:
            return path + [current]

        neighbours = wiki.get_wikipedia_links(current)

        if target in neighbours:
            return path + [target]
        
        max_sim = 0
        current = None
        for node in neighbours:
            if node not in seen:
                node_vec = phrase_to_vec(wiki.clean_wiki_link(node), model)
                node_sim = target_cosine_sim(node_vec)
                if max_sim == 0 or max_sim < node_sim:
                    max_sim = node_sim
                    current = node

    print("Dead end reached!")
    return path