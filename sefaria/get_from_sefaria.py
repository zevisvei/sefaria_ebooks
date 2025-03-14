from collections import defaultdict

from .sefaria_api import SefariaApi
from .utils import to_daf, to_gematria, has_value, to_eng_daf


class Book:
    def __init__(
        self,
        book_title: str,
        lang: str,
        he_title: str | None = None,
        categories: list | None = None,
        get_links: list | bool = False,
    ) -> None:

        self.book_title = book_title
        self.metadata = {}
        self.lang = lang[:2]
        self.long_lang = lang
        self.section_names_lang = (self.lang
                                   if self.lang in ("he", "en")
                                   else "en")
        self.book_content = []
        self.all_commentaries = set()
        self.sefaria_api = SefariaApi()
        self.he_title = he_title
        self.categories = categories
        self.shape = self.sefaria_api.get_shape(self.book_title)
        self.get_links = get_links
        self.links_dict = {}
        self.exists = isinstance(self.shape, list)
        if self.exists:
            self.is_complex = bool(self.shape[0].get("isComplex"))
            self.index = self.sefaria_api.get_index(self.book_title)
            self.is_complex_and_simple = bool(
                self.is_complex != bool(self.index["schema"].get("nodes"))
            )

    def get_metadata(self) -> dict[str, str] | None:
        if not self.exists:
            return
        era_dict = {
            "GN": {"en": "Gaonim", "he": "גאונים"},
            "RI": {"en": "Rishonim", "he": "ראשונים"},
            "AH": {"en": "Achronim", "he": "אחרונים"},
            "T": {"en": "Tannaim", "he": "תנאים"},
            "A": {"en": "Amoraim", "he": "אמוראים"},
            "CO": {"en": "Contemporary", "he": "מחברי זמננו"},
        }
        authors = self.index.get("authors", [{}])
        authors_list = [i.get(self.section_names_lang) for i in authors if i.get(self.section_names_lang) is not None]
        if authors_list:
            self.metadata["authors"] = "&".join(authors_list)

        if self.section_names_lang == "he" and (
            self.he_title or self.shape[0].get("heBook")
        ):
            self.metadata["title"] = self.he_title or self.shape[0].get("heBook")
        else:
            self.metadata["title"] = self.book_title

        long_Desc = self.index.get(f"{self.section_names_lang}Desc")
        ShortDesc = self.index.get(f"{self.section_names_lang}ShortDesc")
        era = self.index.get("era")

        if long_Desc:
            self.metadata["comments"] = long_Desc
        elif ShortDesc:
            self.metadata["comments"] = ShortDesc

        self.metadata["publisher"] = "sefaria"
        categories = self.index.get("categories")

        if self.categories and self.section_names_lang == "he":
            self.metadata["tags"] = ",".join(self.categories)
            if not self.metadata.get("series"):
                self.metadata["series"] = self.categories[-1]
        elif categories:
            self.metadata["tags"] = ",".join(categories)
            if not self.metadata.get("series"):
                self.metadata["series"] = categories[-1]

        if era:
            era_in_dict = era_dict.get(era)
            if era_in_dict:
                if self.metadata.get("tags"):
                    self.metadata["tags"] += f",{era_in_dict[self.section_names_lang]}"
                else:
                    self.metadata["tags"] = era_in_dict[self.section_names_lang]

        self.metadata["language"] = self.lang
        return self.metadata

    def set_series(self, text: dict) -> None:
        if not self.metadata.get("series"):
            if self.section_names_lang == "he" and text.get("heCollectiveTitle"):
                self.metadata["series"] = text.get("heCollectiveTitle")
            elif text.get("collectiveTitle"):
                self.metadata["series"] = text.get("collectiveTitle")
        if not self.metadata.get("series-index") and not self.metadata.get("series"):
            if text.get("order"):
                self.metadata["series-index"] = text["order"][-1]

    def process_book(self) -> list | None:
        if not self.exists:
            return
        if self.is_complex:
            self.node_num = 0
            self.process_node(self.index["schema"])
        elif self.is_complex_and_simple:
            self.node_num = 0
            self.process_complex_and_simple_book(self.index["schema"])
        else:
            self.process_simple_book()
        return self.book_content

    def process_complex_and_simple_book(self, node: dict, level: int = 0) -> None:
        nodes = node["nodes"]
        key = [self.book_title]
        for node in nodes:
            if self.section_names_lang == "he":
                section_names = node.get("heSectionNames")
            else:
                section_names = node.get("sectionNames")
            node_level = level
            node_titles = node.get("titles", {})
            he_title, en_title = self.parse_titles(node_titles)
            node_title = None
            if node_titles:
                node_title = he_title if self.section_names_lang == "he" else en_title
            if node_title is None and node.get("heTitle" if self.section_names_lang == "he" else "title"):
                node_title = node.get("heTitle" if self.section_names_lang == "he" else "title")
            if node_title is None and node.get("sharedTitle"):
                node_title = self.parse_terms(node["sharedTitle"])
            if node_title:
                node_level += 1
                self.book_content.append(
                    f"<h{min(node_level, 6)}>{node_title}</h{min(node_level, 6)}>\n"
                )
            depth = node["depth"]
            if node["key"] == "default":
                node_len = self.shape[0]["length"]
                ref = ", ".join(key)
                key.append(f"1-{node_len}")
                node_index = ", ".join(key)
                text = self.sefaria_api.get_book(node_index, self.long_lang)
            else:
                key.append(en_title)
                node_index = ", ".join(key)
                ref = node_index
                text = self.sefaria_api.get_book(node_index, self.long_lang)
            self.set_series(text)
            text = text.get("versions")
            if text:
                text = text[0]["text"]
                if has_value(text):
                    self.recursive_sections(ref, section_names, text, depth, node_level + 1)
                else:
                    print(self.book_title)
            key.pop()

    def process_simple_book(self) -> None:
        index = self.index
        if self.section_names_lang == "he":
            section_names = index["schema"].get("heSectionNames")
        else:
            section_names = index.get("sectionNames")
        depth = index["schema"]["depth"]
        text = self.sefaria_api.get_book(self.book_title, self.long_lang)
        self.set_series(text)
        text = text.get("versions")
        if text:
            text = text[0]["text"]
            if has_value(text):
                self.recursive_sections(self.book_title, section_names, text, depth, 1)
            else:
                print(self.book_title)

    def process_node(self, node: dict, key: list | None = None, level: int = 0) -> None:
        """
        Process a given node, handling both nested nodes and nested arrays.
        :param node: the current node being processed
        :param text: the text associated with the node
        :param output: the output list to which the processed text is appended
        :return: None
        """
        if key is None:
            key = []
        node_title = None
        node_titles = node.get("titles", {})
        he_title, en_title = self.parse_titles(node_titles)
        if node_titles:
            node_title = he_title if self.section_names_lang == "he" else en_title
        if node_title is None and node.get("heTitle" if self.section_names_lang == "he" else "title"):
            node_title = node.get("heTitle" if self.section_names_lang == "he" else "title")
        if node_title is None and node.get("sharedTitle"):
            node_title = self.parse_terms(node["sharedTitle"])

        if not node_title:
            node_title = (
                self.shape[0]["chapters"][self.node_num]["heTitle"]
                if self.section_names_lang == "he"
                else self.shape[0]["chapters"][self.node_num]["title"]
            )
            node_title = node_title.split(",")[-1].strip()

        if node_title:
            level += 1
            self.book_content.append(
                f"<h{min(level, 6)}>{node_title}</h{min(level, 6)}>\n"
            )
        if node.get("nodes"):  # Process nested nodes
            node_key = node["key"]
            key.append(en_title)
            for sub_node in node["nodes"]:
                self.process_node(sub_node, key, level=level)
            key.pop(-1)
        else:  # Process nested arrays
            node_key = node["key"]
            depth = node.get("depth", 1)
            if node_key == "default":
                node_len = self.shape[0]["chapters"][self.node_num]["length"]
                assert isinstance(node_len, int)
                ref = ", ".join(key)
                key.append(f"1-{node_len}")
                node_index = ", ".join(key)
                text = self.sefaria_api.get_book(node_index, self.long_lang)
            else:
                key.append(en_title)
                node_index = ", ".join(key)
                ref = node_index
                # self.book_content.append(f"{self.codes[level][0]}{node_title}{self.codes[level][1]}\n")
                text = self.sefaria_api.get_book(node_index, self.long_lang)
                # depth = text.get('textDepth', 1)
                # print(depth)
            self.set_series(text)
            if self.section_names_lang == "he":
                section_names = node.get("heSectionNames")
            else:
                section_names = node.get("sectionNames")
            text = text.get("versions")
            if text:
                text = text[0]["text"]
                if has_value(text):
                    self.recursive_sections(ref, section_names, text, depth, level + 1)
                else:
                    print(self.book_title)
            key.pop()
            self.node_num += 1

    def recursive_sections(
        self,
        ref: str,
        section_names: list | None,
        text: list,
        depth: int,
        level: int = 0,
        add_letter: str = "",
        anchor_ref: list | None = None,
        links: defaultdict | None = None
    ) -> None:

        if anchor_ref is None:
            anchor_ref = []
        if links is None and self.get_links:
            ref_links = f"{ref} {":".join(anchor_ref)}" if anchor_ref else ref
            links_dict = self.sefaria_api.get_links(ref_links)
            if links_dict:
                links = self.parse_links(links_dict)
            elif links_dict is not None:
                links = {"links": None}

        skip_section_names = ("שורה", "פירוש", "פסקה", "Line", "Comment", "Paragraph")
        letter_to_add = ""
        """
        Recursively generates section names based on depth and appends to output list.
        :param section_names: list of section names
        :param text: input text
        :param depth: current depth of recursion
        :return: None
        """
        if depth == 0 and text != [] and not isinstance(text, bool):
            if isinstance(text, list):
                for line in text:
                    self.recursive_sections(ref, section_names, line, depth, level, letter_to_add, anchor_ref, links)
            else:
                anchor_ref_address = f"{ref} {":".join(anchor_ref)}"
                self.book_content.append(f"<p>{add_letter}{text}</p>")
                if links and links.get(anchor_ref_address):
                    self.links_dict[len(self.book_content)] = links[anchor_ref_address]
        elif not isinstance(text, bool):
            if depth == 1 and isinstance(text, str):
                self.recursive_sections(ref, section_names, text, depth - 1, level, letter_to_add, anchor_ref, links)
            else:
                for i, item in enumerate(text, start=1):
                    if has_value(item):
                        letter = ""
                        if section_names:
                            letter = (
                                to_daf(i)
                                if section_names[-depth] in ("דף", "Daf")
                                else to_gematria(i)
                            )
                        if depth > 1 and section_names and section_names[-depth] not in skip_section_names:
                            self.book_content.append(
                                f"<h{min(level, 6)}>{section_names[-depth]} {letter}</h{min(level, 6)}>\n"
                            )
                        elif section_names and section_names[-depth] not in skip_section_names and letter:
                            letter_to_add = f"<b>{letter}</b> "
                    anchor_ref.append(to_eng_daf(i) if section_names[-depth] in ("דף", "Daf") else str(i))
                    self.recursive_sections(
                        ref,
                        section_names, item,
                        depth - 1, level + 1,
                        letter_to_add, anchor_ref,
                        links
                    )
                    anchor_ref.pop()

    def parse_terms(self, term: str) -> str | None:
        terms = self.sefaria_api.get_terms(term)
        if terms.get("titles"):
            for i in terms["titles"]:
                if i.get("lang") == self.section_names_lang and i.get("primary"):
                    title = i.get("text")
                    return title

    def parse_titles(self, titles: dict) -> tuple[str, str]:
        he_title = ""
        en_title = ""
        for i in titles:
            if i.get("lang") == "he" and i.get("primary"):
                he_title = i.get("text")
            elif i.get("lang") == "en" and i.get("primary"):
                en_title = i.get("text")
        return he_title, en_title

    def parse_links(
        self, links: list[dict[str, str | list | dict] | None]
            ) -> defaultdict[str, defaultdict[str, list[str | list[str]]]]:
        links_list = defaultdict(lambda: defaultdict(list))
        for link in links:
            he_title = None
            en_title = None
            link_type = link.get("type")
            if link_type != "commentary":
                continue
            anchor_ref = link.get("anchorRef")
            if not anchor_ref:
                continue
            collective_title = link.get("collectiveTitle")
            if isinstance(collective_title, dict):
                he_title = collective_title.get("he")
                en_title = collective_title.get("en")
            if he_title is None:
                he_title = link.get("heTitle")
            if self.section_names_lang == "he":
                title = he_title or en_title
                text = link.get("he") or link.get("text")
            else:
                title = en_title or he_title
                text = link.get("text") or link.get("he")
            if text and title:
                links_list[anchor_ref][title].append(text)
                self.all_commentaries.add(title)
        return links_list

    def add_links(self, links_to_add: list) -> None:
        added_lines = 0
        for index, link in self.links_dict.items():
            for name in link:
                if name in links_to_add:
                    self.book_content.insert(index + added_lines, f'<p style="color: gray;">{name}</p>')
                    added_lines += 1
                    for line in link[name]:
                        if isinstance(line, list):
                            for sub_line in line:
                                self.book_content.insert(index + added_lines, f'<p style="font-size: small;">{sub_line}</p>')
                                added_lines += 1
                        else:
                            self.book_content.insert(index + added_lines, f'<p style="font-size: small;">{line}</p>')
                            added_lines += 1
