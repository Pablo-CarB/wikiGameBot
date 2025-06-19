import requests                  # sends the HTTP requests
from bs4 import BeautifulSoup    # is what can parse HTML
from typing import List     # just needed for signatures/type hinting        
from urllib.parse import unquote # needed for correctly formatting articles names    


def get_wikipedia_links(url : str) -> List[str]:
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
        
    soup = BeautifulSoup(response.content, "html.parser")

    # only look at divs with the correct tag 
    content_divs = soup.find_all("div",class_="mw-parser-output") 
    if not content_divs:
        return []

    # collect links
    links = set()
    for element in content_divs:
        # remove in text citations
        for citation in element.find_all(['sup','span'], class_=['reference', 'mw-cite-backlink']):
            citation.decompose()

        # only admit links that link to full articles not sections
        for link_tag in element.find_all('a',href=True):
            link = link_tag['href']
            if(link.startswith('/wiki/') and 
               ":" not in link and
               "#" not in link):
                links.add('https://en.wikipedia.org' + link)

    return list(links) 

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

def format_path(path : List[str]) -> str:
    return " → ".join([clean_wiki_link(url) for url in path ])

def clean_wiki_links(urls : List[str]) -> List[str]:
    return map(clean_wiki_link,urls)
