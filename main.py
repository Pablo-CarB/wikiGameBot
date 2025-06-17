import searchAlgorithms as search
from gensim.models import KeyedVectors
import time
import wikiLinkRetrieval as wiki
from pathlib import Path

model = KeyedVectors.load(str(Path("models/wiki-news-300d-1M.kv").resolve()),mmap='r')

start_link = "https://en.wikipedia.org/wiki/Biology"
target_link = "https://en.wikipedia.org/wiki/Humphry_Davy"

print(wiki.get_wikipedia_links("https://en.wikipedia.org/wiki/List_of_United_States_senators_from_Massachusetts"))


# print("####################### BFS SEARCH #######################")
# start_bfs_time = time.time()
# bfs_path = search.bfs(start_link, target_link)
# end_bfs_time = time.time()

# print("####################### BFS PATH #######################")
# print(bfs_path)
# print(f"BFS TIME : {end_bfs_time-start_bfs_time}")

# s="https://en.wikipedia.org/wiki/Derek_Jacobi_on_screen_and_stage"
# print(f"links {wiki.get_wikipedia_links(s)}")

# print("####################### EMBEDDED VECTOR SEARCH #######################")
# start_vec_time = time.time()
# vec_path = search.vecSimSearch2(start_link, target_link, model)
# end_vec_time = time.time()
# print("####################### EMBEDDED VECTOR PATH #######################")
# print(vec_path)
# print(f"VEC TIME : {end_vec_time-start_vec_time}")


# for i in range(0,20):
#     start_bfs_time = time.time()
#     bfs_path = search.bfs(start_link, target_link)
#     end_bfs_time = time.time()
#     print(f"time: {end_bfs_time-start_bfs_time} path: {bfs_path}")