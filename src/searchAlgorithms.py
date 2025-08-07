from typing import List, overload
import wikiLinkRetrieval as wiki
from gensim.models import KeyedVectors
from sentence_transformers import SentenceTransformer
import numpy as np

# use this to find the length of the optimal path, does not actually play the game
def bfs_length(source : str,target : str) -> int:
    """An implementation of BFS for wikipedia articles that calculates the shortest path length,
    given the source and target pages as urls. Will return -1 if no path exists.

    Args:
        source (str): the url for the start page
        target (str): the url for the end page

    Returns:
        int: the length of the optimal path
    """
    queue = [(source, [source])]
    seen = set()

    while queue:
        current,path = queue.pop(0)
        seen.add(current)

        if current == target:
            return path + [current]

        neighbours = wiki.get_adj_wiki(current)

        if target in neighbours:
            return path + [target]

        for node in neighbours:
            if node not in seen:
                queue.append((node,path + [node]))
    return None

# use this to find the all of the optimal paths, does not actually play the game
def bfs_paths(source : str,target : str) -> List[str]:
    """An implementation of BFS for wikipedia articles that calculates all of the optimal paths,
    given the source and target pages as urls. Will return an empty list if no path exists.

    Args:
        source (str): the url for the start page
        target (str): the url for the end page

    Returns:
        List[str]: the list of all optimal paths between the source and target articles
    """
    opt_paths = []
    opt_length = 0

    queue = [(source, [source])]
    seen = set()

    while queue:
        current,path = queue.pop(0)
        seen.add(current)

        neighbours = wiki.get_adj_wiki(current)

        if opt_length !=0 and len(path) > opt_length:
            return opt_paths

        if target in neighbours:
            path_target = path+ [target]

            if opt_length == 0:
                opt_length = len(path_target)
                print(wiki.format_path(path_target))
                opt_paths.append(path_target)
                continue
            elif len(path_target) == opt_length:
                opt_paths.append(path_target)
                print(wiki.format_path(path_target))
                continue

        for node in neighbours:
            if node not in seen:
                queue.append((node,path + [node]))
    return []


################################################ Word2Vec Search ################################################

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

# first implementation that actually plays the game
def word2vec_search(start : str,target : str, model : KeyedVectors) -> List[str]:
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
    target_vec = phrase_to_vec(wiki.clean_wiki_link(target),model)
    target_norm = np.linalg.norm(target_vec)

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

        neighbours = wiki.get_adj_wiki(current)

        if target in neighbours:
            return path + [target]
        
        max_sim = -1
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

################################################ Transformer Search ################################################


# first implementation that actually plays the game
def transformer_search(start : str,target : str, model : SentenceTransformer) -> List[str]:
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
    target_vec = model.encode(wiki.clean_wiki_link(target))
    target_norm = np.linalg.norm(target_vec)

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
        print(wiki.clean_wiki_link(current))
        path.append(current)
        seen.add(current)

        if current == target:
            return path + [current]

        neighbours = wiki.get_adj_wiki(current)

        if target in neighbours:
            return path + [target]
        
        max_sim = -1
        current = None

        for node in neighbours:
            if node not in seen:
                node_vec = model.encode(wiki.clean_wiki_link(node))
                node_sim = target_cosine_sim(node_vec)
                if max_sim == 0 or max_sim < node_sim:
                    max_sim = node_sim
                    current = node

    print("Dead end reached!")
    return path