import json
import networkx as nx
import json
import pandas as pd
import numpy as np
import pickle

import networkx as nx
from networkx.readwrite import json_graph
import json

with open("./src/RL agent/graphs/DisciplinesGraphL2.pickle", 'rb') as f:
    G = pickle.load(f)

# Convert the graph to node-link data
graph_data = json_graph.node_link_data(G)

# Save the data to a JSON file
with open('networkx_graph.json', 'w') as f:
    json.dump(graph_data, f, indent=4)

print("NetworkX graph saved to DisciplinesGraphL2.json")