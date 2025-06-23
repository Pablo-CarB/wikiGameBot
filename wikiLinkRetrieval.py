import requests                  # sends the HTTP requests
from bs4 import BeautifulSoup    # is what can parse HTML
from typing import List,Set      # just needed for signatures/type hinting        
from urllib.parse import unquote # needed for correctly formatting articles names 
import asyncio                   # needed for concurrency
import aiohttp                   # needed for concurrent HTTP requests
import re                        # regex library


def extract_links_bs(content : bytes) -> Set[str] :
    """Given the bytes of a wikipedia article will construct a set of urls pointing to other wikipedai pages found hyperlinked within the main text/content of the page. This includes tables figures and other elements of the page but excludes in text citations and the bibliography. This function uses BeautifulSoup to parse html making it but it is slower than extract_links_regex.

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
        # remove reflist section
        for reflist_div in content_div.select('div.reflist'):
            reflist_div.decompose()

        # remove in text citations
        for citation in content_div.select('sup.reference, span.mw-cite-backlink'):
            citation.decompose()

        # collect links
        for link in content_div.select('a[href^="/wiki/"]'):
                #print(f"link {link} in div{content_div.attrs}")
                href = link.get('href')
                if href and ':' not in href and '#' not in href:
                    links.add('https://en.wikipedia.org' + href)

    return links

def extract_links_regex(content: bytes) -> Set[str]:
    """Given the bytes of a wikipedia article will construct a set of urls pointing to other wikipedai pages found hyperlinked within the main text/content of the page. This includes tables figures and other elements of the page but excludes in text citations and the bibliography. This function uses regex pattern matching and is potentially more unstable than extract_links_bs().

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

    content_section_pattern = r"""
    <div                # start of the div tag
    [^>]*               # the closing of the div tag and any attributes before the mw-parser-output class
    class="             # starting the classes attribute
    [^"]*               # match any character that isn't " to match any other classes before mw-parser-output
    mw-parser-output    # the content class for wikipedia articles
    [^"]*               # match any character that isn't " to match any other classes after mw-parser-output
    "                   # close class atribute
    [^>]*               # match any character that isn't > to find any other attributes
    >                   # closing the div tag
    """

    start_match = re.search(content_section_pattern, html ,re.VERBOSE)
    if not start_match:
        return set()
    
    # take everything from the start of content div to end of document for capturing nested stuff
    main_content = html[start_match.start():]

    div_reflist_pattern = r"""
    <div    # start of opening sup tag
    [^>]*   # match any number of characters that aren't >    
    class="
    [^"]*
    reflist
    [^"]*
    "
    [^>]*
    >       # close opening sup tag
    .*?     # (non-greedy/lazy creating individual matches for nested elements)
    </div>  # closing sup tag
    """
    
    # fyi flags are bits so adding them is bitwise OR
    main_content = re.sub(div_reflist_pattern, '', main_content, flags=re.DOTALL | re.VERBOSE)

    sup_citation_pattern = r"""
    <sup    # start of opening sup tag
    [^>]*   # match any number of characters that aren't >    
    >       # close opening sup tag
    .*?     # (non-greedy/lazy creating individual matches for nested elements)
    </sup>  # closing sup tag
    """
    
    # fyi flags are bits so adding them is bitwise OR
    main_content = re.sub(sup_citation_pattern, '', main_content, flags=re.DOTALL | re.VERBOSE)

    # remove any sup tags that contain the reference class to remove in text citations
    span_citation_pattern = r"""
    <span             # start of opening sup tag
    [^>]*             # match any amount of anything that isn't > to catch any attributes before class
    class="           # start class attribute
    [^"]*             # match anything that isn't " to catch any other classes before reference
    reference         # reference class marks in text citations
    [^"]*             # match anything that isn't " to catch any other classes after reference
    "                 # close class attribute
    [^>]*             # match any amount of anything that isn't > to capture any attributes after class
    >                 # close the opening sup tag
    .*?               # match any thing lazily to catch nested content
    </span>           # close span tag
    """

    main_content = re.sub(span_citation_pattern, '', main_content, flags=re.DOTALL | re.VERBOSE)
    
    # extract wiki links
    wiki_link_pattern = r"""
    href="(/wiki/  # start of href 
    [^":#]*        # match any character that isn't " : or # to not count any urls that link to article sections
    )"             # finish the href attribute
    """
    wiki_links = re.findall(wiki_link_pattern, main_content, re.VERBOSE)
    
    return {'https://en.wikipedia.org' + link for link in wiki_links if link}


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

    return extract_links_opt(response.content)

async def async_get_adj_wiki(url :str, session : aiohttp.ClientSession) -> Set[str]:
    async with session.get(url) as response:
        content = await response.read()
        return extract_links_opt(content)


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