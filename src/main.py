import searchAlgorithms as search
from gensim.models import KeyedVectors
import time
import wikiLinkRetrieval as wiki
from pathlib import Path
from sentence_transformers import SentenceTransformer

start_link = "https://en.wikipedia.org/wiki/Biology"
target_link = "https://en.wikipedia.org/wiki/Humphry_Davy"

print("####################### BFS PATH #######################")
bfs_path = search.bfs_paths(start_link, target_link)

print("####################### Word2Vec VECTOR SEARCH #######################")
word2vec_model = KeyedVectors.load(str(Path("./models/word2vec/wiki-news-300d-1M.kv").resolve()),mmap='r')
start_vec_time = time.time()
vec_path = search.word2vec_search(start_link, target_link, word2vec_model)
end_vec_time = time.time()
print("####################### Word2Vec VECTOR PATH #######################")
print(wiki.format_path(vec_path))
print(f"Word2Vec TIME : {end_vec_time-start_vec_time}")
print(f"Word2Vec JUMPS: {len(vec_path)}")

search.bfs

# print("####################### SENTENCE TRANSFORMER VECTOR SEARCH #######################")
# sentence_transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
# print(type(sentence_transformer_model))
# start_vec_time = time.time()
# vec_path = search.transformer_search(start_link, target_link, sentence_transformer_model)
# end_vec_time = time.time()
# print("####################### SENTENCE TRANSFORMER VECTOR PATH #######################")
# print(wiki.format_path(vec_path))
# print(f"SENTENCE TRANSFORMER TIME : {end_vec_time-start_vec_time}")
# print(f"SENTENCE TRANSFORMER TIME: {len(vec_path)}")
