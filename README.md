# **wikiGameBot**

> [!WARNING]  
> This project is in progress and does not reflect the final results.

## Introduction

The objective of the [Wikipedia Game](https://en.wikipedia.org/wiki/Wikipedia:Wiki_Game) is to find the shortest path between two random articles by starting at one and clicking on the other articles hyperlinked within the page. At first it might seem like solving this programmatically is trivial, just by using BFS you can always find the actual shortest path between any two articles. 

*_However_* this isn't actually playing the game, this is calculating the shortest path which is an important distinction. When someone plays the game, every article they visit forms part of their path, and in most wikipedia game rulesets you may not use the back button on your browser (or that if you do it counts as a jump).

The goal of this project is to develop an agent that can genuinely play the game and efficiently find sufficiently good paths. 

## Approach
There are two things that the model needs to understand/learn to effectively play the game
1. the semantic relationships between words (specifically article titles) to understand if it is near or approaching the target article
2. the fact that it is traversing a graph, and the strategies related to that namely that
   - it isn't always the best strategy to go to the article with the most similar name to the target (can get lost down long paths)
   - sometimes it makes sense to choose a more ambiguous article because it is likely to be a "hub" article that has a lot of connections to other articles

Most of the classic path finding algorithms like A* and BFS are ruled out purely because they rely on being able to backtrack which in principle isn't possible because hyperlinks are one way connections (it also could be pretty inneficient). Another issue especially with A* is the lack of an admissable heurisitc, there simply isn't a realistic way of providing a useful heuristic on the Wikipedia graph.

One possibility is just using a greedy based approach that always chooses the most semantically similar aritcle. This is possible to implement and can work but falls flat when understanding graph traversal becomes important. Greedy based approaches often get lost and miss out on obvious strategic choices because of a slighltyl more similar but much more obscure article.

That leaves us with reinforcement learning as a possible approach. If we train a model on "useful" subgraphs of the Wikipedia graph centered on hub articles that are likely to come up then over succe 

## Results

## Installation/Setup

