import requests                  # sends the HTTP requests
from bs4 import BeautifulSoup    # is what can parse HTML

def get_wikipedia_links(url):
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        raise ConnectionError("Failed to retrieve the webpage!")

    soup = BeautifulSoup(response.content, "html.parser")
    content_divs = soup.find_all("div",class_="mw-parser-output")  # only looking at the relevant text tag
    reference_divs = soup.find_all("div", class_="reflist")           # the references section
    further_reading_divs = soup.find_all("div", class_="refbegin")    # the further reading section


    exclusion_list = []
    if reference_divs is not None:
        exclusion_list.extend(reference_divs)
    if further_reading_divs is not None:
        exclusion_list.extend(further_reading_divs)

    for tag in exclusion_list:
        tag.decompose()

    page_links = []
    for div in content_divs:
        page_links.extend(div.find_all('a')) # all of the links in the main text

    # Find all hyperlinks
    links = []
    for link in page_links:
        href = link.get("href")
        # Check if the link is a Wikipedia article
        if href and href.startswith("/wiki/") and ":" not in href:
            full_url = "https://en.wikipedia.org" + href
            if full_url not in links:
                links.append(full_url)

    return links

def clean_wiki_link(link):
    partial = link[30:].replace("_"," ")
    if "#" in partial:
        partial = partial[partial.index("#")+1:]
    return partial

def clean_up_links(links):
    return map(clean_wiki_link,links)


def construct_dictionary(links):
    link_term_map  = {}
    for link in links:
        link_term_map.update({clean_wiki_link(link):link})
    return link_term_map


url = "https://en.wikipedia.org/wiki/Biology" 
wikipedia_links = get_wikipedia_links(url)

for term in clean_up_links(wikipedia_links):
    print(term)

