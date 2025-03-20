from typing import List
import queue
import wikiLinkRetrieval as wiki


global_dict = {}

def bfs(start : str,target : str) -> List[str]:
    queue = [(start, [start])]
    seen = set()

    while queue:
        current,path = queue.pop(0)
        seen.add(current)
        print(current)

        if current == target:
            return path + [current]
        
        neighbours = wiki.get_wikipedia_links(current)

        if target in neighbours:
            return path + [target]

        for node in neighbours:
            if node not in seen:
                queue.append((node,path + [node]))
    return None

    
path = bfs(start="https://en.wikipedia.org/wiki/Genetic_drift",target="https://en.wikipedia.org/wiki/Harmonic_series_(mathematics)")
print(path)


#print(path)
links = wiki.get_wikipedia_links("https://en.wikipedia.org/wiki/Biology")
print("https://en.wikipedia.org/wiki/Biology" in links)
print("https://en.wikipedia.org/wiki/Gestational_diabetes" in links)

