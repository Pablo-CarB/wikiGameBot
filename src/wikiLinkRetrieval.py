import requests                       # sends the HTTP requests
from bs4 import BeautifulSoup         # is what can parse HTML
from typing import List,Set,Dict      # just needed for signatures/type hinting  
from _collections_abc import Callable # more type hinting    
from urllib.parse import unquote      # needed for correctly formatting articles names 
import asyncio                        # needed for concurrency
import aiohttp                        # needed for concurrent HTTP requests
import re                             # regex library

############################## Parsers/ HTML Wiki Link Extractors  ##############################

def extract_links(content: bytes) -> Set[str]:
    """Given the bytes of a wikipedia article will construct a set of urls pointing to other wikipedia
    pages found hyperlinked within the main text/content of the page. 
    This includes tables figures and other elements of the page but excludes in text citations and the bibliography. 

    Args:
        content (bytes): the content of the wikipedia page

    Returns:
        Set[str]: the set of wikipedia urls hyperlinked in the page
    """
    

    try:
        html = content.decode('utf-8', errors='ignore')
    except:
        return set()
    
    # find the main content div
    content_section_pattern = r'<div[^>]*class="[^"]*mw-parser-output[^"]*"[^>]*>'

    main_body = re.search(content_section_pattern, html ,re.VERBOSE)

    if not main_body:
        raise RuntimeError("unable to find main content section")

    end_section_patterns = [
        r'<h2[^>]*id="See_also"[^>]*>',           # See also
        r'<h2[^>]*id="References"[^>]*>',         # References  
        r'<h2[^>]*id="Further_reading"[^>]*>',    # Further reading
        r'<h2[^>]*id="External_links"[^>]*>',     # External links
        r'<h2[^>]*id="Notes"[^>]*>',              # Notes
        r'<h2[^>]*id="Bibliography"[^>]*>',       # Bibliography
        r'<div[^>]*class="[^"]*reflist[^"]*"[^>]*>' # References div (fallback)
    ]

    cutoff_point = len(html)

    for pattern in end_section_patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match and match.start() < cutoff_point:
            cutoff_point = match.start()
        
    main_content = html[main_body.start():cutoff_point]

    # if not main_body or not reference_section:
    #     raise RuntimeError(f"could not find appropriate wikipedia section")

    # take everything from the start of content div to the end of document (the start of the references section)
    # for capturing nested stuff
    

    # fyi flags are bits so adding them is bitwise OR
    # main_content = re.sub(div_reflist_pattern, '', main_content, flags=re.DOTALL | re.VERBOSE)

    sup_citation_pattern = r'<sup[^>]*>.*?</sup>'
    
    # fyi flags are bits so adding them is bitwise OR
    main_content = re.sub(sup_citation_pattern, '', main_content, flags=re.DOTALL | re.VERBOSE)

    # remove any sup tags that contain the reference class to remove in text citations
    span_citation_pattern = r'<span[^>]*class="[^"]*reference[^"]*"[^>]*>.*?</span>'

    main_content = re.sub(span_citation_pattern, '', main_content, flags=re.DOTALL | re.VERBOSE)
    
    # extract wiki links (ignores links with : or # cause they point to sections)
    wiki_link_pattern = r'href="(/wiki/[^":]+)"'
    wiki_links = re.findall(wiki_link_pattern, main_content, re.VERBOSE)
    
    cleaned_links = set()
    for link in wiki_links:
        if ':' not in link:  # Only exclude colon links (special pages)
            # Strip fragment (everything after #) to get base page
            base_link = link.split('#')[0]
            if base_link:  # Make sure we have something left after stripping
                cleaned_links.add('https://en.wikipedia.org' + base_link)
    return cleaned_links

############################## Adjacent Article Functions  ##############################

def get_adj_wiki(url : str, parser : Callable[[bytes],Set[str]] = extract_links) -> Set[str]:
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

    return parser(response.content)

async def async_get_adj_wiki(url :str, session : aiohttp.ClientSession, parser : Callable[[bytes],Set[str]] = extract_links) -> Set[str]:
    async with session.get(url) as response:
        content = await response.read()
        return {url : parser(content)}


async def async_get_adj_wikis_helper(urls : Set[str],batch_size : int = 20) -> Dict[str,Set[str]]:
    
    mapping : Dict[str,Set[str]] = {}

    semaphore = asyncio.Semaphore(batch_size)

    async def get_links(url):
        async with semaphore:
            return await async_get_adj_wiki(url,session)
        
    async with aiohttp.ClientSession() as session:
            tasks  = [get_links(url) for url in urls]
            
            # return exceptions so that whole thing doesn't fail if one url does
            results = await asyncio.gather(*tasks, return_exceptions=True) 

            return {k: v for r in results if isinstance(r, dict) for k, v in r.items()}
    
def get_adj_wiki_lists(urls : Set[str],batch_size : int = 20) -> Dict[str,Set[str]]:
    return asyncio.run(async_get_adj_wikis_helper(urls,batch_size))

############################## Helper Functions/Formatting Functions  ##############################

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

# most_referenced = "https://en.wikipedia.org/wiki/Wikipedia:Most-referenced_articles"
# countries =  "https://simple.wikipedia.org/wiki/List_of_countries"
# disciplines = "https://en.wikipedia.org/wiki/Outline_of_academic_disciplines"

# print(get_adj_wiki_lists(set({most_referenced,countries,disciplines})))
