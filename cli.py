from sefaria import sefaria_api, utils, get_from_sefaria
import traceback


def run_script(book: dict, lang: str, get_links: bool = False):
    try:
        print(book)
        file_name = utils.sanitize_filename(book['he_title'] if lang == "hebrew" else book['en_title'])
        html_file = f"{file_name}.html"
        epub_file = f"{file_name}.epub"
        result = get_from_sefaria.Book(
            book["en_title"], lang, book["he_title"], book["path"], get_links=get_links
        )
        if not result.exists:
            print("book not exists")
            return
        book_dir = ' dir="rtl"' if lang == "hebrew" else ""
        book_content = result.process_book()
        if get_links:
            for index, i in enumerate(result.all_commentaries, start=1):
                print(f"{index}) {i}")
            commentaries_to_add = input("index\n").split()
            list_to_add = [list(result.all_commentaries)[int(index) - 1] for index in commentaries_to_add]
            result.add_links(list_to_add)
            book_content = result.book_content
        if not book_content:
            return
        book_content = f'<html lang={lang[:2]}><head><title></title></head><body{book_dir}>{"".join(book_content)}</body></html>'
        if "footnote-marker" in book_content:
            book_content = utils.footnotes_to_epub(book_content)
        metadata = result.get_metadata()

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(book_content)
        if metadata is None:
            metadata = {}
        utils.to_ebook(html_file, epub_file, metadata)

    except Exception:
        print(traceback.format_exc())


def main():
    sefaria_api_instance = sefaria_api.SefariaApi()
    all_books = sefaria_api_instance.table_of_contents()
    list_all_books = utils.recursive_register_categories(all_books)
    for book in list_all_books:
        run_script(book, "hebrew", True)


main()
