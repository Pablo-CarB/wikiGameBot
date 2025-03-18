import requests                  # sends the HTTP requests
from bs4 import BeautifulSoup    # is what can parse HTML

def get_wikipedia_links(url):
    # Send a GET request to the Wikipedia page
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    soup = soup.find_all('div',class_="mw-content-ltr mw-parser-output")[0]  # only looking at the relevant text tag
    soup = soup.find_all('a') # only looking at links

    # Find all hyperlinks
    links = []
    for link in soup:
        href = link.get('href')
        # Check if the link is a Wikipedia article
        if href and href.startswith('/wiki/') and ':' not in href:
            full_url = 'https://en.wikipedia.org' + href
            links.append(full_url)

    return links

def clean_wiki_link(link):
    partial = link[30:].replace("_"," ")
    if "#" in partial:
        partial = partial[partial.index("#")+1:]
    return partial


def clean_up_links(links):
    return map(clean_wiki_link , links)


url = 'https://en.wikipedia.org/wiki/Manifold_hypothesis' 
wikipedia_links = get_wikipedia_links(url)

# Print the results
for link in clean_up_links(wikipedia_links):
    print(link)
