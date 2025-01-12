import os
import subprocess
from sefaria import get_from_sefaria, sefaria_api, utils
from bs4 import BeautifulSoup
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
def to_ebook(input_file: str, output_file: str, dict_arga: dict[str, str],
            level1_toc: str="//h:h1", level2_toc: str="//h:h2", level3_toc: str="//h:h3"):
    args = ["ebook-convert",input_file, output_file,
                    f"--level1-toc={level1_toc}" ,f"--level2-toc={level2_toc}" ,f"--level3-toc={level3_toc}"]
    for key, value in dict_arga.items():
        args.append(f"--{key}={value}")
    subprocess.run(args,stdout=subprocess.DEVNULL,  # משתיק את הפלט
            stderr=subprocess.DEVNULL,  # משתיק את השגיאות
            check=True)

start = False
all_books = sefaria_api.SefariaApi().table_of_contents()
sorted_toc = utils.recursive_register_categories(all_books)
lang = "hebrew"
book_dir = ' dir="rtl"' if lang == "hebrew" else ""
for book in sorted_toc:
    print(book["en_title"])
    print(book["he_title"])
    if not start:
        if book["en_title"] == "Targum Sheni on Esther":
            start = True
        continue
    book_ins = get_from_sefaria.Book(book["en_title"], lang, book["he_title"], book["path"])
    get_book = book_ins.process_book()
    metadata = book_ins.get_metadata()
    soup = BeautifulSoup(f'<html lang={lang[:2]}><head><title></title></head><body{book_dir}>{"".join(get_book)}</body></html>', "html.parser")

    soup = soup.prettify()
    book_name = utils.sanitize_filename(book["he_title"]) if lang == "hebrew" else utils.sanitize_filename(book["en_title"])
    with open(f"{book_name}.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    to_ebook(f"{book_name}.html", f"{book_name}.epub", metadata)