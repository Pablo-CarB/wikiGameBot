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
    
    response = requests.get(url)
    
    if response.status_code != 200:
        raise ConnectionError("Failed to retrieve the webpage!")

    soup = BeautifulSoup(response.content, "html.parser")
    content_divs = soup.find_all("div",class_="mw-parser-output")     # only looking at the relevant text tag
    reference_divs = soup.find_all("div", class_="reflist")           # the references section
    further_reading_divs = soup.find_all("div", class_="refbegin")    # the further reading section

    # combine references and further reading to create a list of sections to exclude
    exclusion_list = reference_divs+further_reading_divs

    # purge the document from the undesired sections
    for tag in exclusion_list:
        tag.decompose()

    # collect every tag with 
    page_links = []
    for div in content_divs:
        page_links.extend(div.find_all('a')) # all of the links in the main text

    # verify the hyperlinks and collect them
    links = []
    for link in page_links:
        href = link.get("href")
        # Check if the link is a wikipedia article
        if href and href.startswith("/wiki/") and ":" not in href:
            full_url = "https://en.wikipedia.org" + href
            if full_url not in links:
                links.append(full_url)

    return links


def clean_wiki_link(link : str) -> str:
    """
        Given a link to a wikipedia page will extract the relevant title of the page, if the link points 
        to a specific section of the page will use the title of that section. 

        Args:
            link (str): the url of the wikipedia page

        Returns:
            str: The relevant title of the link
    """
        
    partial = link[30:]
    if "#" in partial:
        partial = partial[partial.index("#")+1:]
    return partial

def clean_up_links(links : List[str]) -> List[str]:
    return map(clean_wiki_link,links)


def construct_dictionary(links : List[str]) -> Dict[str,str]:
    """
        Given a list wikipedia urls will create a dictionary mapping between the the relevant title of the page,
        and the actual url

        Args:
            links (List[str]): the list of wikipedia urls

        Returns:
            Dict[str,str]: The relevant title of the link
    """

    link_term_map  = {}
    for link in links:
        link_term_map.update({clean_wiki_link(link):link})
    return link_term_map

