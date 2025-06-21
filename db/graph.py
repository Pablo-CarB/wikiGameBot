import networkx as nx            # used for building graphs
from networkx import DiGraph
import sys                       # used for interacting w/ system
sys.path.append("./")            # adds wikiLinkRetrieval to path
import wikiLinkRetrieval as wiki # used for finding wikipedia links
from typing import Set           # just needed for signatures/type hinting     
from copy import deepcopy        # used for copying the list
import pickle                    # stores graph
import asyncio
import time
import aiohttp


#slowest parts
# 1. collecting adjacent articles
# 2. copy list over
# 3. making current
# 4. adding nodes to wiki graph
# 5. adding edges to wiki graph 
# addings stuff to s2 ~ 0 seconds

# it take 0.10873603820800781 seconds to run sprawl
# it take 5.245208740234375e-06 seconds to make the current
# it take 4.76837158203125e-06 seconds to run add the nodes to the wikiGraph
# it take 0.1086571216583252 seconds to collect the articles
# it take 2.86102294921875e-06 seconds to make the edge lists
# it take 0.0 seconds to add stuff to s2
# it take 1.1920928955078125e-06 seconds to add the edges to the wikiGraph
# it take 3.790855407714844e-05 seconds to copy the list over


async def get_links_batch(urls, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_single(session, url):
        async with semaphore:
            async with session.get(url) as response:
                return url, await response.text()
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_single(session, url) for url in urls]
        return await asyncio.gather(*tasks)
    
def sprawl(starts: Set[str],iterations: int) -> DiGraph:
    """given a set of starting urls to wikipedia articles 

    Args:
        starts (Set[str]): a set of starting nodes
        iterations (int): the number of layers away from the starting articles to expand

    Returns:
        _type_: _description_
    """
    wikiGraph = nx.DiGraph()

    s1 = starts
    s2 = set()

    while (iterations > 0) and (len(s1) != 0):
        
        for url in s1:
            article_name = wiki.clean_wiki_link(url)
            current = (article_name, url)

            wikiGraph.add_node(current)
            adj = wiki.(url)

            edges = [(wiki.clean_wiki_link(adj_article),adj_article) for adj_article in adj]

            s2.update(adj)
            
            wikiGraph.add_edges_from([(current,e) for e in edges])

        s1 = s2
        s2 = set()

        iterations -= 1
    return wikiGraph

# Some influential wikipedia lists
most_referenced = "https://en.wikipedia.org/wiki/Wikipedia:Most-referenced_articles"
countries =  "https://simple.wikipedia.org/wiki/List_of_countries"
disciplines = "https://en.wikipedia.org/wiki/Outline_of_academic_disciplines"

# start_set = set(most_referenced,countries,disciplines)
start_func = time.time()
G = sprawl(set({"https://en.wikipedia.org/wiki/Repatriation_of_Ashanti_Gold_Regalia_from_the_UK_to_Ghana"}),4)
end_func = time.time()

with open('wikiGraph2.pickle', 'wb') as file:
        pickle.dump(G, file)

######################## async approach #########################

async def link_producer(session: aiohttp.ClientSession, url_queue: asyncio.Queue, 
                       result_queue: asyncio.Queue, semaphore: asyncio.Semaphore) -> None:
    while True:
        try:
            url = await asyncio.wait_for(url_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
        except:
            break
            
        async with semaphore:  # Limit requests to batch size
            links = await wiki.get_adj_wiki(session, url)
            await result_queue.put((url, links))
        
        url_queue.task_done()

async def graph_builder(result_queue: asyncio.Queue, wikiGraph: nx.DiGraph, 
                       processed_urls: set, next_layer: set):
    while True:
        try:
            url, links = await result_queue.get()
            
            article_name = wiki.clean_wiki_link(url)  # Your function
            current = (article_name, url)
            wikiGraph.add_node(current)
            
            edges = [(wiki.clean_wiki_link(link), link) for link in links]
            wikiGraph.add_edges_from([(current, e) for e in edges])
            
            # Track what we've processed and what's next
            processed_urls.add(url)
            next_layer.update(links)
            
            result_queue.task_done()
            
        except asyncio.CancelledError:
            break


async def sprawl(starts : Set[str], iterations : int, HTTPBatch : int = 20) -> DiGraph:

    wikiGraph = nx.DiGraph()

    current_layer = starts
    processed_urls = set()

    semaphore = asyncio.Semaphore(HTTPBatch)

    async with aiohttp.ClientSession() as session:
        for i in range(iterations):
            if not current_layer:
                break

            print(f"Processing layer {iteration + 1} with {len(current_layer)} URLs")
            urls_to_check = current_layer-processed_urls
            if not urls_to_check:
                break
                
            url_queue = asyncio.Queue()
            result_queue = asyncio.Queue()
            next_layer = set()

            for url in urls_to_check:
                await url_queue.put(url)

            producers = [
                asyncio.create_task(link_producer(session, url_queue, result_queue, semaphore))
                for _ in range(min(HTTPBatch, len(urls_to_check)))
            ]

            consumer = asyncio.create_task(
                graph_builder(result_queue, wikiGraph, processed_urls, next_layer)
            )

            await url_queue.join()

            await result_queue.join()

            for p in producers:
                p.cancel()
            consumer.cancel()

            current_layer = next_layer

    return wikiGraph

async def main():
    starts = {"https://en.wikipedia.org/wiki/Repatriation_of_Ashanti_Gold_Regalia_from_the_UK_to_Ghana"}

    wikiGraph = await sprawl(starts,3,)

asyncio.run(main())