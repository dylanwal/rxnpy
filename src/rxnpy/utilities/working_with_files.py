import json
import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """ sorts in human order """
    return [atoi(c) for c in re.split(r'(\d+)', text)][1]


def get_files(path, pattern: str = "*.json", sort_fun=natural_keys) -> list[str]:
    """ Returns a list of file names. """
    import glob
    import os

    # Find all json files
    file_list = []
    os.chdir(path)
    for files in glob.glob(pattern):
        file_list.append(files)  # filename with extension

    file_list.sort(key=sort_fun)
    return file_list


def get_json(path) -> dict:
    """ Opens and loads JSON. """
    encodings = ['utf-8', 'windows-1250', 'windows-1252', "latin-1"]
    for e in encodings:
        try:
            with open(path, "r", encoding=e) as f:
                text = f.read()
                json_data = json.loads(text)
                break
        except UnicodeDecodeError:
            pass
    else:
        raise RuntimeError(f"No valid encoding found for '{path}'.")

    return json_data


def get_multi_json(path, pattern: str = "*.json", chunk: int = None, **kwargs) -> list[dict]:
    """ Get multiple json at once. """
    files = get_files(path, pattern, **kwargs)
    if chunk is None:
        chunk = len(files) + 1

    out = []
    for _ in range(len(files) + 1):
        counter = 0
        while counter < chunk:
            try:
                file_ = files.pop(0)
            except IndexError:
                yield out
                return StopIteration

            out.append(get_json(file_))
            counter += 1

        yield out
        out = []


def get_jsonl(file_path) -> list[dict]:
    """ Opens and loads JSON lines. """
    encodings = ['utf-8', 'windows-1250', 'windows-1252', "latin-1"]
    data = []
    for e in encodings:
        try:
            with open(file_path, "r", encoding=e) as f:
                for line in f:
                    data.append(json.loads(line))
                break
        except UnicodeDecodeError:
            pass
    else:
        raise RuntimeError(f"No valid encoding found for '{file_path}'.")

    return data


def save_to_json(file_path, filename: str, json_: dict):
    """ Write files to JSON. """
    full_path = file_path + filename + ".json"
    with open(full_path, "w", encoding='utf-8') as f:
        json.dump(json_, f, ensure_ascii=False, indent=4)

    return full_path


def save_to_jsonl(file_path, filename, list_objs):
    """ Write files to JSON lines. """
    full_path = file_path + "\\" + filename + ".jsonl"
    text = "\n".join([json.dumps(json_) for json_ in list_objs])
    with open(full_path, "w", encoding='utf-8') as f:
        f.write(text)

    return full_path
