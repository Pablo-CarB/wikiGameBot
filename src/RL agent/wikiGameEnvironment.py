
import torch
from torch import nn
import torch.functional as F
import numpy as np

import networkx as nx
import random

import sys                       
sys.path.append("./src")     
from wikiLinkRetrieval import clean_wiki_link
from searchAlgorithms import phrase_to_vec

class WikiEnvironment:
    def assign_nodes(self,init_node : str = None, target_node : str = None):
        self.visited = []
        if (init_node is None) or not (self.graph.has_node(init_node)):
            if self.graph.has_node(init_node) is None:
                print(f"start article {init_node} doesn't exist in the graph! choosing random article")   
            self.current_node = random.choice(list(self.graph.nodes))
            print(f"start article --> {self.current_node}")
        else:
            self.current_node = init_node
            print(f"start article --> {self.current_node}")

        if (target_node is None) or not (self.graph.has_node(target_node)):
            if self.graph.has_node(target_node) is None:
                print(f"target article {target_node} doesn't exist in the graph! choosing random article")   
            self.target_node = random.choice(list(self.graph.nodes))
            print(f"target article --> {self.target_node}")
        else:
            self.target_node = target_node
            print(f"target article --> {self.target_node}")

    def __init__(self,
                 G : nx.DiGraph,
                 embedder,
                 init_node : str = None,
                 target_node : str = None,
                 seed : int = None,
                 success_reward: float = 1000.0,
                 step_loss: float = -2.0,
                 similarity_threshold: float = 0.6,
                 similarity_scale_factor: float = 2):
        
        self.seed = seed
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.graph = G
        self.embedder = embedder
        self.success_reward = success_reward
        self.step_loss = step_loss
        self.similarity_threshold = similarity_threshold
        self.similarity_scale_factor = similarity_scale_factor
        self.visited = []
        self.assign_nodes(init_node,target_node)

    def get_state(self):
        return {'path' : list(map(self.embedder,self.visited)),
         'current article' : self.embedder(self.current_node),
         'target article' : self.embedder(self.target_node)}
        
    def get_actions(self):
        return list(map(self.embedder,self.graph.neighbors(self.current_node)))
    
    def step(self,model_output):
        output_norm = np.linalg.norm(model_output)
        def cosine_sim(adjacent_vec):
            adjacent_norm = np.linalg.norm(adjacent_vec)
            return np.dot(model_output,adjacent_vec)/(adjacent_norm*output_norm)
        
        max_similarity = -1
        most_similar = None
        for adj in self.get_actions():
            if cosine_sim(self.embedder(adj)) < max_similarity:
                most_similar = adj
                max_similarity = cosine_sim(self.embedder(adj))

        self.visited.append(self.current_node)
        self.current_node = adj

        similarity_reward = self.step_loss*(1/(1+np.exp(self.similarity_scale_factor(max_similarity-self.similarity_threshold))))-0.5*self.step_loss

        state = self.get_state()
        isdone = True if (self.current_node == self.target_node) or (len(self.graph.neighbors(self.current_node)) == 0) else False
        reward = self.success_reward + similarity_reward  if isdone else self.step_loss + similarity_reward

        return [state, reward, isdone]
        
    def reset(self,init_node : str = None, target_node : str = None):
        self.visited = []
        self.assign_nodes(init_node,target_node)