import requests                  # sends the HTTP requests
from bs4 import BeautifulSoup    # is what can parse HTML
from typing import List,Dict     # just needed for signatures/type hinting            


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
        raise ConnectionError(f"Could not retrieve page \n error code : ")
        
    soup = BeautifulSoup(response.content, "html.parser")

    # only look at divs with the correct tag 
    content_divs = soup.find_all("div",class_="mw-parser-output") 
    if not content_divs:
        return []

    # only look at the paragraphs and tables in the divs (ignores bibliography and other sections)
    paragraphs = []
    tables = []
    for div in content_divs:
        paragraphs.extend(div.find_all('p'))
        tables.extend(div.find_all('table'))


    # collect links
    links = set()
    for p in paragraphs + tables:
        # remove in text citations
        for citation in p.find_all(['sup','span'], class_=['reference', 'mw-cite-backlink']):
            citation.decompose()

        # only admit links that link to full articles not sections
        for link_tag in p.find_all('a',href=True):
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
        
    partial = url[30:]
    if "#" in partial:
        partial = partial[partial.index("#")+1:]
    return partial

def clean_up_links(urls : List[str]) -> List[str]:
    return map(clean_wiki_link,urls)


def construct_dictionary(urls : List[str]) -> Dict[str,str]:
    """
        Given a list wikipedia urls will create a dictionary mapping between the the relevant title of the page,
        and the actual url

        Args:
            links (List[str]): the list of wikipedia urls

        Returns:
            Dict[str,str]: The relevant title of the link
    """

    link_term_map  = {}
    for link in urls:
        link_term_map.update({clean_wiki_link(link):link})
    return link_term_map

