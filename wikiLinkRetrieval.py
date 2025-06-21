import requests                  # sends the HTTP requests
from bs4 import BeautifulSoup    # is what can parse HTML
from typing import List,Set      # just needed for signatures/type hinting        
from urllib.parse import unquote # needed for correctly formatting articles names 
import asyncio                   # needed for concurrency
import aiohttp                   # needed for concurrent HTTP requests

def extract_links(content : bytes) -> Set[str] :
    """Given the bytes of a wikipedia article will construct a set of urls pointing to other wikipedai pages found hyperlinked within the main text/content of the page. This includes tables figures and other elements of the page but excludes in text citations and the bibliography.

    Args:
        content (bytes): the content of the wikipedia page

    Returns:
        Set[str]: the set of wikipedia urls hyperlinked in the page
    """

    try:
        soup = BeautifulSoup(content, "lxml")
    except:
        print("lxml not available using html.parser")
        soup = BeautifulSoup(content, "html.parser")

    # only look at divs with the correct tag 
    content_divs = soup.select("div.mw-parser-output") 
    if not content_divs:
        return set()

    links = set()
    for content_div in content_divs:
        for citation in content_div.select('sup.reference, span.mw-cite-backlink'):
            citation.decompose()

        # collect links
        for link in content_div.select('a[href^="/wiki/"]'):
                href = link.get('href')
                if href and ':' not in href and '#' not in href:
                    links.add('https://en.wikipedia.org' + href)

    return links

def get_adj_wiki(url : str) -> Set[str]:
    """
        Given a link to a wikipedia page, will construct a list of urls pointing to other wikipedai pages found
        hyperlinked within the main text

        Args:
            url (str): the url of the wikipedia page

        Raises:
            ConnectionError: if the wikipedia page cannot be acessed for any reason

        Returns:
            List[str]: a list of urls of the wikipedia pages hyperlinked within the text of the original wikipedia page
    """
    
    # try to establish connection
    try:
        response = requests.get(url)
    except Exception as e:
        print("request failed with exception:", e)
        raise ConnectionError(f"Could not retrieve page \nerror code : {e}")    

    return extract_links(response.content)

async def async_get_adj_wiki(url :str, session : aiohttp.ClientSession) -> Set[str]:
    async with session.get(url) as response:
        content = await response.read()
        return extract_links(content)


async def get_adj_wiki_lists(urls : Set[str],batch_size : int = 20) -> Set[str]:
    semaphore = asyncio.Semaphore(batch_size)

    async def get_links(url):
        async with semaphore:
            return await async_get_adj_wiki(url,session)
        
    async with aiohttp.ClientSession() as session:
            tasks  = [get_links(url) for url in urls]
            
            # return exceptions so that whole thing doesn't fail if one url does
            results = await asyncio.gather(*tasks, return_exceptions=True) 
            return set().union(*[r for r in results if isinstance(r, set)])
    

def clean_wiki_link(url : str) -> str:
    """
        Given a link to a wikipedia page will extract the relevant title of the page, if the link points 
        to a specific section of the page will use the title of that section. 

        Args:
            link (str): the url of the wikipedia page

        Returns:
            str: The relevant title of the link
    """
        
    partial = url.replace('https://en.wikipedia.org/wiki/',"")
    partial = unquote(partial)
    return partial.replace("_", " ")

def clean_wiki_links(urls : List[str]) -> List[str]:
    return map(clean_wiki_link,urls)

def format_path(path : List[str]) -> str:
    return " → ".join([clean_wiki_link(url) for url in path ])