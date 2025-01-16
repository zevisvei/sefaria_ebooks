import os
import subprocess
import json
from sefaria import get_from_sefaria, sefaria_api, utils
from bs4 import BeautifulSoup
from tqdm import tqdm

"""
path = "test_b"
text = "SchemaNode"
for file in os.listdir(path):
    file_path = os.path.join(path, file)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        num = content.count(text)
        num_2 = content.count("nodes")
        if num == 0 and num_2 > 1:
            print(num_2)
            --title
            --comments

"""


def to_ebook(
    input_file: str,
    output_file: str,
    dict_args: dict[str, str],
    level1_toc: str = "//h:h1",
    level2_toc: str = "//h:h2",
    level3_toc: str = "//h:h3",
):
    args = [
        "ebook-convert",
        input_file,
        output_file,
        f"--level1-toc={level1_toc}",
        f"--level2-toc={level2_toc}",
        f"--level3-toc={level3_toc}",
    ]
    for key, value in dict_args.items():
        args.append(f"--{key}={value}")
    subprocess.run(
        args,
        stdout=subprocess.DEVNULL,  # משתיק את הפלט
        stderr=subprocess.DEVNULL,  # משתיק את השגיאות
        check=True,
    )


"""
start = False
os.makedirs("html", exist_ok=True)
os.makedirs("epub", exist_ok=True)
all_books = sefaria_api.SefariaApi().table_of_contents()
sorted_toc = utils.recursive_register_categories(all_books)
"""
lang = "hebrew"
book_dir = ' dir="rtl"' if lang == "hebrew" else ""
book_ins = get_from_sefaria.Book("Genesis", lang)
get_ebook = book_ins.process_book()
metadata = book_ins.get_metadata()
print(metadata)
soup = BeautifulSoup(
    f'<html lang={lang[:2]}><head><title></title></head><body{book_dir}>{"".join(get_ebook)}</body></html>',
    "html.parser",
)

soup = soup.prettify()
book_name = "test_4"
file_name = os.path.join("html", f"{book_name}.html")
epub_name = os.path.join("epub", f"{book_name}.epub")
with open(file_name, "w", encoding="utf-8") as f:
    f.write(str(soup))
# to_ebook(file_name, epub_name, metadata)

lang = "hebrew"
os.makedirs("shape", exist_ok=True)
os.makedirs("index", exist_ok=True)
all_books = sefaria_api.SefariaApi().table_of_contents()
sorted_toc = utils.recursive_register_categories(all_books)
for book in tqdm(sorted_toc, desc="Processing books"):
    book_ins = get_from_sefaria.Book(
        book["en_title"], lang, book["he_title"], book["path"]
    )
    """
    if hasattr(book_ins, "is_complex_and_simple") and book_ins.is_complex_and_simple:
        json_file_name = f"{utils.sanitize_filename(book_ins.book_title)}.json"
        with open(os.path.join("shape", json_file_name), "w", encoding="utf-8") as f:
            json.dump(book_ins.shape, f, ensure_ascii=False, indent=4)
        with open(os.path.join("index", json_file_name), "w", encoding="utf-8") as f:
            json.dump(book_ins.index, f, ensure_ascii=False, indent=4)

        print(book_ins.book_title)
    """
    get_book = book_ins.process_book()
    # metadata = book_ins.get_metadata()
    # print(metadata)
    # soup = BeautifulSoup(f'<html lang={lang[:2]}><head><title>{book["he_title"]}</title></head><body{book_dir}>{"".join(get_book)}</body></html>', "html.parser")

    # soup = soup.prettify()
    # book_name = utils.sanitize_filename(book["he_title"]) if lang == "hebrew" else utils.sanitize_filename(book["en_title"])
    # file_name = os.path.join("html", f"{book_name}.html")
    # epub_name = os.path.join("epub", f"{book_name}.epub")
    # with open(file_name, "w", encoding="utf-8") as f:
    #    f.write(str(soup))
    # to_ebook(file_name, epub_name, metadata)
