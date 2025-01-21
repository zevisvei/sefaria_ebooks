from flask import Flask, render_template, request, jsonify, send_file
from sefaria import sefaria_api, utils, get_from_sefaria
import subprocess
import os


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


app = Flask(__name__)

# טוען את כל הספרים
sefaria_api_instance = sefaria_api.SefariaApi()
all_books = sefaria_api_instance.table_of_contents()
list_all_books = utils.recursive_register_categories(all_books)


@app.route("/")
def index():
    return render_template("index.html", books=list_all_books)


@app.route("/run_script", methods=["POST"])
def run_script():
    try:
        book_index = int(request.json["index"])
        lang = request.json["lang"]
        book = list_all_books[book_index]
        file_name = utils.sanitize_filename(book['he_title'] if lang == "hebrew" else book['en_title'])
        html_file = f"{file_name}.html"
        epub_file = f"{file_name}.epub"
        print(request.json)
        result = get_from_sefaria.Book(
            book["en_title"], lang, book["he_title"], book["path"]
        )
        if not result.exists:
            return jsonify({"status": "error", "message": "book dose not exists"}), 404
        book_dir = ' dir="rtl"' if lang == "hebrew" else ""
        book_content = result.process_book()
        book_content = f'<html lang={lang[:2]}><head><title></title></head><body{book_dir}>{"".join(book_content)}</body></html>'
        metadata = result.get_metadata()
        
        # יצירת קובץ HTML
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(book_content)
        
        # יצירת קובץ EPUB
        to_ebook(html_file, epub_file, metadata)
        epub_file = os.path.abspath(f"{file_name}.epub")
        
        # החזרת הקובץ להורדה
        return send_file(
            epub_file,
            as_attachment=True,
            download_name=f"{file_name}.epub",
            mimetype="application/epub+zip",
            conditional=False
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if os.path.exists(html_file):
            os.remove(html_file)
        if os.path.exists(epub_file):
            os.remove(epub_file)


if __name__ == "__main__":
    app.run(debug=True)
