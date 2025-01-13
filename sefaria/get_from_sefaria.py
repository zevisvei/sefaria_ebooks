from .sefaria_api import SefariaApi
from .utils import to_daf, to_gematria

class Book:
    def __init__(
            self, book_title: str, lang: str,
            he_title: str|None = None,
            categories: list|None = None,
            get_links: list|bool = False
            ) -> None:
        self.book_title = book_title
        self.metadata = {}
        self.lang = lang[:2]
        self.long_lang = lang
        self.book_content = []
        self.sefaria_api = SefariaApi()
        self.he_title = he_title
        self.categories = categories
        self.shape = self.sefaria_api.get_shape(self.book_title)
        self.is_complex = bool(self.shape[0].get("isComplex"))
        self.index = self.sefaria_api.get_index(self.book_title)
        self.is_complex_and_simple = bool(self.is_complex !=  bool(self.index["schema"].get("nodes")))
        self.get_links = get_links

    def get_metadata(self) -> dict[str, str]:
        era_dict = {
             "GN" : {"en":"Gaonim","he": "גאונים"},
             "RI" : {"en":"Rishonim", "he": "ראשונים"},
             "AH" : {"en":"Achronim", "he": "אחרונים"},
             "T" : {"en":"Tannaim", "he": "תנאים"},
             "T" : {"en":"Amoraim", "he": "אמוראים"},
             "CO" : {"en":"Contemporary", "he": "מחברי זמננו"}
            }
        authors = self.index.get("authors")
        if authors:
            self.metadata["authors"] = "&".join(authors)
        self.metadata["title"] = self.book_title if self.lang != "he" else self.he_title
        long_Desc = self.index.get(f"{self.lang}Desc")
        ShortDesc = self.index.get(f"{self.lang}ShortDesc")
        era = self.index.get("era")
        if long_Desc:
            self.metadata["comments"] = long_Desc
        elif ShortDesc:
            self.metadata["comments"] = ShortDesc
        categories = self.index.get("categories")
        if self.categories and self.lang == "he":
            self.metadata["tags"] = ",".join(self.categories)
        elif categories:
            self.metadata["tags"] = ",".join(categories)
        if era:
            era_in_dict = era_dict.get(era)
            if era_in_dict:
                self.metadata["series"] = era_in_dict[self.lang]
        self.metadata["language"] = self.lang
        return self.metadata

    def process_book(self) -> list:
        if self.is_complex:
            self.node_num = 0
            self.process_node(self.index["schema"])
        elif self.is_complex_and_simple:
            self.node_num = 0
            self.process_complex_and_simple_book(self.index["schema"])
        else:
            self.process_simple_book()
        return self.book_content
    
    def process_complex_and_simple_book(self, node: dict, level: int=1) -> None:
        section_names = self.sefaria_api.get_name(self.book_title)["heSectionNames"] if self.lang == "he" else  self.sefaria_api.get_name(self.book_title)["sectionNames"] 
        node = node['nodes'][0]
        depth = node['depth'] +1
        key = [self.book_title, node["key"]]
        node_len = self.shape[0]["length"]
        for num in range(1, node_len +1):
            key.append(str(num))
            node_index = ", ".join(key)
            text = self.sefaria_api.get_book(node_index, self.long_lang)
            text = text.get("versions")
            if text:
                self.recursive_sections(section_names, text[0]['text'], depth-1, level+1)
            key.pop()

    def process_simple_book(self) -> None:
        index = self.index
        if self.lang == "he":
            section_names = self.sefaria_api.get_name(self.book_title).get("heSectionNames")
        else:
            section_names = self.sefaria_api.get_name(self.book_title).get("sectionNames")
        depth = index['schema']['depth']
        text = self.sefaria_api.get_book(self.book_title, self.long_lang)
        # add book title
        # add authors name
        #if index.get("authors"):
        #    for author in index['authors']:
        #        self.book_content.append(author['he']+'\n')            
        self.recursive_sections(section_names, text["versions"][0]['text'], depth,1)
    
    def process_node(
            self, node: dict, key: list|None = None,level: int=1
            ) -> None:
        """
        Process a given node, handling both nested nodes and nested arrays.
        :param node: the current node being processed
        :param text: the text associated with the node
        :param output: the output list to which the processed text is appended
        :return: None
        """
        if key is None:
            key = []
        node_titles = node.get('titles')
        node_title = None
        if node_titles:
            for i in node_titles:
                if i.get("lang") == self.lang and i.get("primary"):
                    node_title = i.get("text")

        if not node_title:
            node_title = self.shape[0]["chapters"][self.node_num]["heTitle"] if self.lang == "he" else self.shape[0]["chapters"][self.node_num]["title"]
            node_title = node_title.split(",")[-1].strip()


        if node.get('nodes'):  # Process nested nodes
            level += 1
            node_key = node["key"]
            key.append(node_key)
            if node_title:
                self.book_content.append(
                    f"<h{min(level, 6)}>{node_title}</h{min(level, 6)}>\n"
                    )
            for sub_node in node['nodes']:
                self.process_node(sub_node, key, level=level)
            key.pop(-1)
        else:  # Process nested arrays
            node_key = node["key"]
            depth = node.get('depth', 1)
            if node_key == "default":
                node_len = self.shape[0]["chapters"][self.node_num]["length"]
                assert isinstance(node_len, int)
                for num in range(1, node_len +1):
                    key.append(str(num))
                    node_index = ", ".join(key)
                    section_names = self.sefaria_api.get_name(node_index)["heSectionNames"] if self.lang == "he" else  self.sefaria_api.get_name(node_index)["sectionNames"] 
                    section_name = section_names[0]
                    text = self.sefaria_api.get_book(node_index, self.long_lang)
                    text = text.get("versions")
                    if text:
                        self.book_content.append(
                            f"<h{min(level, 6)}>{section_name} {to_gematria(num)}</h{min(level, 6)}>\n"
                        )
                        self.recursive_sections(section_names, text[0]['text'], depth-1, level+1)
                    
                    key.pop()
            else:
                if node_title:
                    self.book_content.append(
                        f"<h{min(level, 6)}>{node_title}</h{min(level, 6)}>\n"
                        )
                key.append(node_key)
                node_index = ", ".join(key)
                #self.book_content.append(f"{self.codes[level][0]}{node_title}{self.codes[level][1]}\n")
                section_names = self.sefaria_api.get_name(node_index).get("heSectionNames")
                text = self.sefaria_api.get_book(node_index)
                #depth = text.get('textDepth', 1)
                #print(depth)
                text = text.get("versions")
                if text:
                    self.recursive_sections(section_names, text[0]['text'], depth, level+1)
                key.pop()
            self.node_num += 1

    def recursive_sections(
            self, section_names: list|None, text: list, depth: int,level: int=0, add_letter: str = ""
            ) -> None:

            skip_section_names = ('שורה', 'פירוש', 'פסקה', 'Line', 'Comment', 'Paragraph')
            letter_to_add = ""
            """
            Recursively generates section names based on depth and appends to output list.
            :param section_names: list of section names
            :param text: input text
            :param depth: current depth of recursion
            :return: None
            """
            if depth == 0 and text != [] and not isinstance(text, bool):
                self.book_content.append(f"<p>{add_letter}{text}</p>")
            elif not isinstance(text, bool):
                for i, item in enumerate(text, start=1):
                    if item != [] and item != [[]]:
                        letter = to_daf(i) if section_names and section_names[-depth] == 'דף' else to_gematria(i)
                        if depth>1 and section_names:                        
                            self.book_content.append(f"<h{min(level, 6)}>{section_names[-depth]} {letter}</h{min(level, 6)}>\n")
                        elif section_names and section_names[-depth] not in skip_section_names:
                            letter_to_add = f"<b>{letter}</b> "
                    self.recursive_sections(section_names, item, depth-1,level+1, letter_to_add)

    def get_links_content(self, book_title: str):
        links = self.sefaria_api.get_links(book_title)
