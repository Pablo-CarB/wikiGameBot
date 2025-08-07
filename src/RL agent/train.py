# agent = WikiAgent(embedding_dim=word2vec_model.vector_size)
# num_epochs = 200
# num_episodes = 5
# max_steps_per_episode = 20
# gamma = 0.99

# node_set = set(country_graph.nodes)

# for epoch in range(1,num_epochs):

#     source = random.choice(node_set)
#     target = random.choice(node_set.difference(source))

#     for episode in range(num_epochs):

#         env.reset()
#         episode_reward = 0
#         done = False
#         step = 0

#         while not done and step < max_steps_per_episode:
            
#             state = env.get_state()
#             action = agent.get_action(state)
            
#             next_state, reward, done, info = env.step(action)

#             #Update both policy (actor) and value function (critic)
#             td_error = reward + gamma * agent.get_value(next_state) - agent.get_action(state)
#             critic_loss = td_error^2
#             actor_loss = -log_prob(action) * td_error
#             update_parameters(critic_loss + actor_loss)
                            
#             agent.update(state, action, reward, next_state, done)

#             state = next_state
#             episode_reward += reward
#             step += 1


###############################################################################################

from wikiGameEnvironment import WikiEnvironment
from agent import ActorNN,CriticNN
import networkx
from gensim.models import KeyedVectors
from pathlib import Path
import torch
import torch.optim as optim
import torch.nn.functional as F
from collections import deque
import numpy as np
import pickle

import sys                       
sys.path.append("./src")     
from wikiLinkRetrieval import clean_wiki_link
from searchAlgorithms import phrase_to_vec

def train_agent(env, actor, critic, episodes=1000, lr=3e-4):

    actor_optimizer = optim.Adam(actor.parameters(), lr=lr)
    critic_optimizer = optim.Adam(critic.parameters(), lr=lr)
    
    # Track training metrics
    episode_rewards = deque(maxlen=100)
    episode_lengths = deque(maxlen=100)
    
    for episode in range(episodes):
        # Reset environment
        env.reset()
        state = env.get_state()
        
        # Episode storage
        states, actions, rewards, log_probs, values = [], [], [], [], []
        done = False

        print(f"------------- episode {episode} -------------")
        
        while not done:
            # Convert state to tensors
            target_emb = torch.tensor(state['target article'], dtype=torch.float32).unsqueeze(0)
            current_emb = torch.tensor(state['current article'], dtype=torch.float32).unsqueeze(0)
            path_embs = torch.tensor(state['path'], dtype=torch.float32).unsqueeze(0) if state['path'] else torch.zeros(1, 0, len(state['target article']))
            
            # Get available actions
            action_embs = env.get_actions()
            if not action_embs:  # No actions available
                break
                
            action_embs_tensor = [torch.tensor(emb, dtype=torch.float32) for emb in action_embs]
            
            # Forward pass through networks
            action_probs = actor(target_emb, current_emb, path_embs, action_embs_tensor)
            value = critic(target_emb, current_emb, path_embs)
            
            # Sample action
            action_dist = torch.distributions.Categorical(action_probs)
            action_idx = action_dist.sample()
            log_prob = action_dist.log_prob(action_idx)
            
            # Take step in environment
            selected_action = action_embs[action_idx.item()]
            next_state, reward, done = env.step(selected_action)
            
            # Store trajectory
            states.append((target_emb, current_emb, path_embs, action_embs_tensor))
            actions.append(action_idx)
            rewards.append(reward)
            log_probs.append(log_prob)
            values.append(value)
            
            state = next_state
        
        # Calculate returns (rewards-to-go)
        returns = []
        R = 0
        for reward in reversed(rewards):
            R = reward + 0.99 * R  # gamma = 0.99
            returns.insert(0, R)
        returns = torch.tensor(returns, dtype=torch.float32)
        
        # Convert to tensors
        log_probs = torch.stack(log_probs)
        values = torch.stack(values).squeeze()
        
        # Calculate advantages
        advantages = returns - values.detach()
        
        # Actor loss (policy gradient with baseline)
        actor_loss = -(log_probs * advantages).mean()
        
        # Critic loss (MSE between predicted and actual returns)
        critic_loss = F.mse_loss(values, returns)
        
        # Update networks
        actor_optimizer.zero_grad()
        actor_loss.backward()
        actor_optimizer.step()
        
        critic_optimizer.zero_grad()
        critic_loss.backward()
        critic_optimizer.step()
        
        # Track metrics
        episode_reward = sum(rewards)
        episode_rewards.append(episode_reward)
        episode_lengths.append(len(rewards))
        
        # Print progress
        if episode % 100 == 0:
            avg_reward = np.mean(episode_rewards)
            avg_length = np.mean(episode_lengths)
            print(f"Episode {episode}, Avg Reward: {avg_reward:.2f}, Avg Length: {avg_length:.2f}")
    
    return actor, critic

# Usage example:
# Assuming you have initialized env, actor, and critic
# trained_actor, trained_critic = train_agent(env, actor, critic)

with open("src/RL agent/graphs/CountryGraphL2.pickle","rb") as f:
    country_graph : networkx.DiGraph = pickle.load(f)

print(len(list(country_graph.nodes)))
print(len(list(country_graph.edges)))
dead_ends = sum(1 for node in country_graph.nodes if country_graph.out_degree(node) == 0)
print(f"Dead ends: {dead_ends}/{len(country_graph.nodes)} ({dead_ends/len(country_graph.nodes)*100:.1f}%)")


# word2vec_model : KeyedVectors = KeyedVectors.load(str(Path("models/word2vec/wiki-news-300d-1M.kv").resolve()),mmap='r')

# env = WikiEnvironment(G=country_graph,
#                     embedder=lambda x : phrase_to_vec(clean_wiki_link(x),word2vec_model),
#                     seed= 22)
# actor = ActorNN(word2vec_model.vector_size)

# critic = CriticNN(word2vec_model.vector_size)

# train_agent(env,actor,critic)