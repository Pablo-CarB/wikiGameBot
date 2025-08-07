import torch
from torch import nn
import torch.functional as F
import numpy as np
import wikiLinkRetrieval as wiki
import networkx as nx
import random

class ActorNN(nn.Module):
    def __init__(self,embedding_dim : int ,hidden_dim : int =256):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim

        self.embed_proj = nn.Linear(embedding_dim, hidden_dim)
        
        self.path_encoder = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
                
        self.strategy_net = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim), # *3 because target + current + path embedding
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        self.score_action = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )

    def forward(self, target_emb, current_emb, path_embs, action_embs_list):
        batch_size = target_emb.shape[0]
        
        target_hidden = self.embed_proj(target_emb)  # (batch_size, hidden_dim)
        current_hidden = self.embed_proj(current_emb)  # (batch_size, hidden_dim)
        
        if path_embs.shape[1] == 0:
            path_context = torch.zeros(batch_size, self.hidden_dim, device=target_emb.device)
        else:
            path_encoded, (hidden_state, _) = self.path_encoder(path_embs)
            path_context = hidden_state[-1]
        
        state_context = torch.cat([target_hidden, current_hidden, path_context], dim=1)
        state_context = self.state_encoder(state_context)
        
        action_scores = []
        for action_emb in action_embs_list:
            action_hidden = self.embed_proj(action_emb.unsqueeze(0))
            
            if batch_size > 1:
                action_hidden = action_hidden.repeat(batch_size, 1)
            
            state_action = torch.cat([state_context, action_hidden], dim=1)
            
            score = self.action_scorer(state_action)
            action_scores.append(score)
        
        if action_scores:
            action_scores = torch.cat(action_scores, dim=1)
        else:
            action_scores = torch.empty(batch_size, 0, device=target_emb.device)
        
        if action_scores.shape[1] > 0:
            action_probs = F.softmax(action_scores, dim=1)
        else:
            action_probs = action_scores
            
        return action_probs
    
class CriticNN(nn.Module):
    def __init__(self, embedding_dim, hidden_dim=256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embedding_dim * 3, hidden_dim), # *3 because target + current + path embedding
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1) 
        )
        
    def forward(self, target_emb, current_emb, path_embs):
        path_summary = path_embs.mean(dim=1) 
        state = torch.cat([target_emb, current_emb, path_summary], dim=1)
        return self.net(state)

