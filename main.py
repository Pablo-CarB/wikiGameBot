import searchAlgorithms as search
from gensim.models import KeyedVectors
import time
import wikiLinkRetrieval as wiki
from pathlib import Path

start_link = "https://en.wikipedia.org/wiki/Biology"
target_link = "https://en.wikipedia.org/wiki/Humphry_Davy"

# print(wiki.get_wikipedia_links("https://en.wikipedia.org/wiki/List_of_United_States_senators_from_Massachusetts"))


# print("####################### BFS SEARCH #######################")
# start_bfs_time = time.time()
# bfs_path = search.bfs(start_link, target_link)
# end_bfs_time = time.time()

print("####################### BFS PATH #######################")
bfs_path = search.bfs(start_link, target_link)
print(wiki.format_path(bfs_path))

# print("####################### EMBEDDED VECTOR SEARCH #######################")
# start_vec_time = time.time()
# vec_path = search.vecSimSearch2(start_link, target_link, model)
# end_vec_time = time.time()
# print("####################### EMBEDDED VECTOR PATH #######################")
# print(vec_path)
# print(f"VEC TIME : {end_vec_time-start_vec_time}")

# print(wiki.get_wikipedia_links("https://en.wikipedia.org/wiki/Charles_Darwin"))

model = KeyedVectors.load(str(Path("models/wiki-news-300d-1M.kv").resolve()),mmap='r')
start_bfs_time = time.time()
bfs_path = search.vecSimSearch2(start_link, target_link,model)
end_bfs_time = time.time()
print(f"####################### EMBEDDED VECTOR SEARCH #######################")
print(f"time: {end_bfs_time-start_bfs_time}")
print(wiki.format_path(bfs_path))
