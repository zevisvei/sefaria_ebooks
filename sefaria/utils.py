import re
from hebrew_numbers import int_to_gematria
import json
import subprocess


def recursive_register_categories(
    index: list | dict,
    data: list[dict[str, str | list[str]]] | None = None,
    tree: list[str] | None = None,
) -> list[dict[str, str | list[str]]]:
    if tree is None:
        tree = []
    if data is None:
        data = []
    if isinstance(index, list):
        for item in index:
            recursive_register_categories(item, data, tree)
    elif isinstance(index, dict):
        if index.get("contents"):
            tree.append(index["heCategory"])
            for item in index["contents"]:
                recursive_register_categories(item, data, tree)
            tree.pop()
        if index.get("title"):
            data.append(
                {
                    "he_title": index["heTitle"],
                    "en_title": index["title"],
                    "path": tree.copy(),
                }
            )
    return data


def sanitize_filename(filename: str) -> str:
    sanitized_filename = re.sub(r'[\\/:*"?<>|]', "", filename)
    sanitized_filename = sanitized_filename.replace("_", " ")
    return sanitized_filename.strip()


def to_daf(i: int) -> str:
    i += 1
    if i % 2 == 0:
        return to_gematria(i//2)+'.'
    else:
        return to_gematria(i//2)+':'


def to_gematria(i: int) -> str:
    s = ''
    i = i % 1000
    j = i / 1000
    if j < 0:
        s = int_to_gematria(j, gershayim=False) + ' '
    s = s + int_to_gematria(i, gershayim=False)
    return s


def to_eng_daf(i) -> str:
    i += 1
    if i % 2 == 0:
        return str(i//2)+'a'
    else:
        return str(i//2)+'b'


def has_value(data: list):
    return any(has_value(item) if isinstance(item, list) else item for item in data)


def read_json(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    return content


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
