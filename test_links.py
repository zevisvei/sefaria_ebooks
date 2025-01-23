from sefaria.get_from_sefaria import Book
from sefaria.utils import to_ebook

lang = "hebrew"
book = Book("Genesis", lang, "בראשית", get_links=True)
links_to_add = ['רמב"ן']
book.process_book()
book.add_links(links_to_add)
book_content = f'<html lang={lang[:2]}><head><title></title></head><body dir="rtl">{"\n".join(book.book_content)}</body></html>'
with open("test.html", "w", encoding="utf-8") as f:
    f.write(book_content)
to_ebook("test.html", "test.epub", book.metadata)
