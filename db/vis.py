import networkx as nx
import matplotlib.pyplot as plt
import pickle
from pyvis.network import Network

def create_from_pickle2(G):
    layout = nx.spring_layout(G)
    
    G2 = Network(height="1500px", width="1900px", bgcolor="#222222", font_color="white", directed=True)
    G2.from_nx(G, default_node_size=30)

    for node in G2.nodes:
        node_id = node["id"]
        if node_id in layout:
            node["x"], node["y"] = layout[node_id][0]*1000, layout[node_id][1]*1000

    G2.toggle_physics(False)
    G2.show_buttons(filter_=['physics'])
    G2.show("wikimap.html", notebook=False)

def create_from_pickle(G):
    
    # Create mapping from tuple nodes to string IDs
    node_mapping = {}
    for i, node in enumerate(G.nodes()):
        node_mapping[node] = str(i)
    
    # Convert the graph
    G_converted = nx.relabel_nodes(G, node_mapping)
    
    # Add the cleaned titles as labels for better visualization
    for old_node, new_node in node_mapping.items():
        cleaned_title = old_node[0]  # First element of tuple is cleaned title
        G_converted.nodes[new_node]['label'] = cleaned_title
        G_converted.nodes[new_node]['title'] = old_node[1]  # URL for hover info
    
    layout = nx.spring_layout(G_converted)
    print("Layout created")
    
    G2 = Network(height="1500px", width="1900px", bgcolor="#222222", font_color="white", directed=True)
    G2.from_nx(G_converted, default_node_size=30)
    
    for node in G2.nodes:
        node_id = node["id"]
        if node_id in layout:
            node["x"], node["y"] = layout[node_id][0]*1000, layout[node_id][1]*1000
    
    G2.toggle_physics(False)
    G2.show_buttons(filter_=['physics'])
    G2.show("wikimap.html", notebook=False)

# Usage:
# create_from_networkx_graph('wikiGraph2.pickle')

F = nx.Graph()
F.add_edges_from([(1,2),(2,3),(3,4),(4,5),(5,6),(6,1)])
create_from_pickle2(F)