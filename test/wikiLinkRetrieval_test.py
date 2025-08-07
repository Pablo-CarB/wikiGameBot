import pytest
import sys
from typing import Dict,Tuple,Set
sys.path.append("./src/")

from wikiLinkRetrieval import (
    extract_links, clean_wiki_link, format_path
)

class TestExtractLinks:

    @pytest.fixture
    def load_htmls(self) -> Dict[str,Tuple[bytes,Set[str]]]:

        sipsi_answer = {"https://en.wikipedia.org/wiki/Clarinet","https://en.wikipedia.org/wiki/Single-reed_instrument",
                           "https://en.wikipedia.org/wiki/Turkish_folk_music","https://en.wikipedia.org/wiki/Turkey",
                           "https://en.wikipedia.org/wiki/Onomatopoeia","https://en.wikipedia.org/wiki/Reed_(plant)",
                           "https://en.wikipedia.org/wiki/Tone_hole","https://en.wikipedia.org/wiki/Aegean_Region",
                           "https://en.wikipedia.org/wiki/Time_signature","https://en.wikipedia.org/wiki/Timbre",
                           "https://en.wikipedia.org/wiki/Uilleann_pipes","https://en.wikipedia.org/wiki/Circular_breathing",
                           "https://en.wikipedia.org/wiki/Diplica","https://en.wikipedia.org/wiki/Dili_tuiduk",
                           "https://en.wikipedia.org/wiki/Musical_instrument_classification","https://en.wikipedia.org/wiki/Woodwind_instrument",
                           "https://en.wikipedia.org/wiki/Hornbostel%E2%80%93Sachs","https://en.wikipedia.org/wiki/Range_(music)",
                           "https://en.wikipedia.org/wiki/Musical_instrument","https://en.wikipedia.org/wiki/Arghul","https://en.wikipedia.org/wiki/B%C3%BClban",
                           "https://en.wikipedia.org/wiki/Dozaleh","https://en.wikipedia.org/wiki/Arghul","https://en.wikipedia.org/wiki/Launeddas",
                           "https://en.wikipedia.org/wiki/Mijwiz","https://en.wikipedia.org/wiki/Pilili","https://en.wikipedia.org/wiki/Zummara"}

        rusty_breasted_nunlet_answer = {
            "https://en.wikipedia.org/wiki/Conservation_status","https://en.wikipedia.org/wiki/Least_Concern","https://en.wikipedia.org/wiki/IUCN_Red_List",
            "https://en.wikipedia.org/wiki/Taxonomy_(biology)","https://en.wikipedia.org/wiki/Eukaryote","https://en.wikipedia.org/wiki/Animal",
            "https://en.wikipedia.org/wiki/Chordate","https://en.wikipedia.org/wiki/Bird","https://en.wikipedia.org/wiki/Piciformes",
            "https://en.wikipedia.org/wiki/Nonnula","https://en.wikipedia.org/wiki/Binomial_nomenclature","https://en.wikipedia.org/wiki/Johann_Baptist_von_Spix",
            "https://en.wikipedia.org/wiki/Near-passerine","https://en.wikipedia.org/wiki/Bucconidae","https://en.wikipedia.org/wiki/Argentina",
            "https://en.wikipedia.org/wiki/Brazil","https://en.wikipedia.org/wiki/Colombia","https://en.wikipedia.org/wiki/Ecuador",
            "https://en.wikipedia.org/wiki/Guyana","https://en.wikipedia.org/wiki/Paraguay","https://en.wikipedia.org/wiki/Peru","https://en.wikipedia.org/wiki/Suriname",
            "https://en.wikipedia.org/wiki/Venezuela","https://en.wikipedia.org/wiki/French_Guiana","https://en.wikipedia.org/wiki/Gerlof_Mees",
            "https://en.wikipedia.org/wiki/Frank_Chapman_(ornithologist)","https://en.wikipedia.org/wiki/Kenneth_Carroll_Parkes","https://en.wikipedia.org/wiki/Philip_Sclater",
            "https://en.wikipedia.org/wiki/W._E._Clyde_Todd","https://en.wikipedia.org/wiki/Lore_(anatomy)","https://en.wikipedia.org/wiki/The_Guianas","https://en.wikipedia.org/wiki/Amazon_River",
            "https://en.wikipedia.org/wiki/Orinoco_River","https://en.wikipedia.org/wiki/Rio_Negro_(Amazon)","https://en.wikipedia.org/wiki/Forest",
            "https://en.wikipedia.org/wiki/V%C3%A1rzea_forest","https://en.wikipedia.org/wiki/Secondary_forest","https://en.wikipedia.org/wiki/Paran%C3%A1_(state)",
            "https://en.wikipedia.org/wiki/Gallery_forest","https://en.wikipedia.org/wiki/Amazonia","https://en.wikipedia.org/wiki/Igap%C3%B3",
            "https://en.wikipedia.org/wiki/Arthropod","https://en.wikipedia.org/wiki/Mixed-species_foraging_flock","https://en.wikipedia.org/wiki/Misiones_Province",
            "https://en.wikipedia.org/wiki/IUCN"

        }

        cornet_answer = {
            "https://en.wikipedia.org/wiki/Organ_stop","https://en.wikipedia.org/wiki/Organ_pipe","https://en.wikipedia.org/wiki/Flue_pipe",
            "https://en.wikipedia.org/wiki/Cornett", "https://en.wikipedia.org/wiki/Sesquialtera_(organ_stop)","https://en.wikipedia.org/wiki/Mixture_(organ_stop)",

        }

        # answer_map structure
        # (name_of_article : (content_of_article ,{adjacent_article_links}))
        answer_map = {}
        for path_answer_pair in [("test/fixtures/Sipsi.html",sipsi_answer),
            ("test/fixtures/Rusty breasted nunlet.html",rusty_breasted_nunlet_answer),
            ("test/fixtures/Cornet.html", cornet_answer)]:
            path = path_answer_pair[0]
            with open(path,'r') as file:
                content = file.read().encode('utf-8')
                answer_map.update({path.replace("test/fixtures/","").replace(".html","") : (content,path_answer_pair[1])})
        return answer_map

    def test_sipsi(self,load_htmls):
        sipsi_info = load_htmls["Sipsi"]
        assert sipsi_info[1] == extract_links(sipsi_info[0])

    # tests interpreting section links and not reading tables
    def test_cornet(self,load_htmls):
        cornet_info = load_htmls["Cornet"]
        assert cornet_info[1] == extract_links(cornet_info[0])

    # tests figures and wikipedia links in references sections
    def test_rusty(self,load_htmls):
        rusty_info = load_htmls["Rusty breasted nunlet"]
        assert rusty_info[1] == extract_links(rusty_info[0])

class TestHelperFunc:

    ############################ Clean Link Tests ############################ 
    
    # single space
    def test_cleaning_link_example_1(self):
        assert clean_wiki_link("https://en.wikipedia.org/wiki/Pop_music") == "Pop music"

    # many spaces
    def test_cleaning_link_example_2(self):
        assert clean_wiki_link("https://en.wikipedia.org/wiki/Honorific_nicknames_in_popular_music") == "Honorific nicknames in popular music"

    # single word
    def test_cleaning_link_example_3(self):
        assert clean_wiki_link("https://en.wikipedia.org/wiki/Europe") == "Europe"

    # non english character Étude
    def test_cleaning_link_example_4(self):
        # the function should return the actual utf-8 word, not what is actually written in the URL 
        assert clean_wiki_link("https://en.wikipedia.org/wiki/%C3%89tude") == "Étude"

    ############################ Format Path Tests ############################
    
    def test_format_path_example_1(self):
        assert format_path(["https://en.wikipedia.org/wiki/Europe"]) == "Europe"

    def test_format_path_example_2(self):
        assert format_path([]) == ""

    def test_format_path_example_3(self):
        assert format_path(["https://en.wikipedia.org/wiki/Europe",
                            "https://en.wikipedia.org/wiki/Honorific_nicknames_in_popular_music",
                            "https://en.wikipedia.org/wiki/%C3%89tude",
                            "https://en.wikipedia.org/wiki/B%C3%BClban"]) == "Europe → Honorific nicknames in popular music → Étude → Bülban"
                                   


if __name__ == "__main__":
    pytest.main(["-vv",
                 "--capture=no"])