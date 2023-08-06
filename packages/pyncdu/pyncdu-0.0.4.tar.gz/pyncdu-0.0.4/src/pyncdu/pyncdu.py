import os
import sys
import shutil

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import ProgressBar

# RECURSION LIMIT
sys.setrecursionlimit(100)
kb = KeyBindings()

UNITS_MAPPING = [
    (1 << 50, " PB"),
    (1 << 40, " TB"),
    (1 << 30, " GB"),
    (1 << 20, " MB"),
    (1 << 10, " KB"),
    (1, (" byte", " bytes")),
]


def pretty_size(bytes: int, units=UNITS_MAPPING) -> str:
    """Get human-readable file sizes.
    simplified version of https://pypi.python.org/pypi/hurry.filesize/
    """
    for factor, suffix in units:
        if bytes >= factor:
            break
    amount = round(bytes / factor, 1)
    if str(amount).endswith(".0"):
        amount = int(amount)

    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix


@kb.add("tab")
def _(event):
    """
    Start auto completion. If the menu is showing already, select the next
    completion.
    """
    b = event.app.current_buffer
    if b.complete_state:
        b.complete_next()
    else:
        b.start_completion(select_first=False)


def get_dir_size(path=".") -> int:
    total = 0
    try:
        path = os.path.realpath(path)
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    try:
                        bytes_ = get_dir_size(entry.path)
                    except RecursionError as e:
                        bytes_ = 0
                    total += bytes_
    except (FileNotFoundError, PermissionError) as e:
        pass
    return total


def scan(path: str) -> list:
    dirs_bytes = {}
    try:
        ls = os.listdir(path)
    except FileNotFoundError as e:
        print(e)
        return []
    with ProgressBar() as pb:
        for entry in pb(os.scandir(path), total=len(ls)):
            if entry.is_file():
                continue
            used_bytes = get_dir_size(entry.path)
            dirs_bytes[entry.name] = used_bytes

    sorted_dirs = sorted(dirs_bytes, key=dirs_bytes.get, reverse=True)
    for name in sorted_dirs:
        print(f"{name:<30} {pretty_size(dirs_bytes[name]):>30}")
    return sorted_dirs


def parse_path(path: str, input_="") -> str:
    if os.sep in input_:
        path = input_
    elif input_ == ".":
        pass
    elif input_ == "..":
        path = os.path.dirname(path)
    elif input_ == "~":
        path = os.path.expanduser("~")
    elif input_:
        path = os.path.join(path, input_)
    else:
        # No input_
        pass
    return path


def on_deletion_error(func, path, exec_info):
    print(func, path, exec_info)
    print("ERROR")


def pyncdu(path: str):
    path = os.path.realpath(os.path.normpath(path))
    while True:
        print()
        autocomplete_list = scan(path)
        print(f"\nYou are here: {path}")
        input_ = prompt(
            "Enter dirname: ",
            completer=WordCompleter(autocomplete_list, ignore_case=True),
            complete_while_typing=True,
            key_bindings=kb,
        )
        if input_.startswith("rm "):
            del_path = parse_path(path, input_[3:])
            delete = prompt(f"Do you really want to delete {del_path} (y/N)? ")
            if delete == "y":
                shutil.rmtree(del_path, onerror=on_deletion_error)
            else:
                print("Skipping")
        elif input_.startswith("cd "):
            input_ = input_[3:]
        else:
            path = parse_path(path, input_)


if __name__ == "__main__":
    try:
        path = sys.argv[1]
    except:
        path = "."
    pyncdu(path)
