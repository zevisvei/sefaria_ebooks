from sefaria.get_from_export import Book
from sefaria.utils import sanitize_filename
import os
import subprocess


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


def get_book(book_title: str, text_file_path: str, schema_file_path: str, lang: str):
    book_ins = Book(book_title,
                    lang,
                    text_file_path,
                    schema_file_path)
    book_content = book_ins.process_book()
    metadata, categories = book_ins.get_metadata()
    return book_content, metadata, categories


def main(json_folder, schemas_folder, output_folder, lang: str):
    eroor_list = []
    """
    Process all books in the given folder whose path ends with 'Hebrew/Merged.json'.
    It finds the corresponding schema file in the schemas folder by matching the
    pattern '/xxxx/Hebrew/Merged.json' to 'xxxx.json'.

    :param folder_path: Path to the folder containing the book files.
    :param schemas_folder: Path to the folder containing the schema files.
    """
    for root, _,files in os.walk(json_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.lower().endswith(f'{lang}{os.sep}merged.json'):
                try:
                    text_file = file_path
                    print(text_file)
                    title = file_path.split(os.sep)[-3].replace(' ', '_')
                    schema_file_name = os.path.join(schemas_folder, title + '.json')
                    book_content, metadata, categories = get_book(title, text_file, schema_file_name, lang)
                    output_path = [sanitize_filename(i) for i in categories]
                    os.makedirs(os.path.join(output_folder, *output_path),exist_ok=True)
                    output_file_name = os.path.join(output_folder, *output_path, sanitize_filename(metadata["title"]))
                    print(output_file_name)
                    book_dir = ' dir="rtl"' if lang == "hebrew" else ""
                    book_content = f'<html lang={lang[:2]}><head><title></title></head><body{book_dir}>{"".join(book_content)}</body></html>'
                    with open(f'{output_file_name}.html', 'w', encoding='utf-8') as file:
                        file.write(book_content)
                    to_ebook(f"{output_file_name}.html", f"{output_file_name}.epub", metadata)
                    os.remove(f"{output_file_name}.html")
                except Exception as e:
                    eroor_list.append(f"{file_path} {e}")
    with open("error.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(eroor_list))


json_folder = "json"
schemas_folder = "schemas"
output_folder = "output"
lang = "hebrew"
main(json_folder=json_folder, schemas_folder=schemas_folder,
     output_folder=output_folder, lang=lang)
                
