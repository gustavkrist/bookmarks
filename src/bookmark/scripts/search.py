import regex as re
from collections import Counter
from rich.text import Text
from thefuzz import process


# def contains_letters(pattern, string):
#     letters = list(pattern)
#     counts = Counter(letters)
#     flags = re.I if all(letter.islower() for letter in letters) else 0
#     for letter in letters:
#         matches = len(re.findall(letter, string, flags=flags))
#         if matches < counts[letter]:
#             return False
#     return True


# def search(pattern, array):
#     array = filter(lambda x: contains_letters(pattern, x), array)
#     return process.extract(pattern, array, limit=10)


def contains_letters(pattern, node):
    file = open(
        "/Users/gustavkristensen/prototypes/bookmark/bookmark/searchlog.txt", "a"
    )
    letters = list(pattern)
    counts = Counter(letters)
    string = node.label
    flags = re.I if all(letter.islower() for letter in letters) else 0
    for letter in list(counts.keys()):
        if letter == "r":
            pat = f"(?<!\\[red]|\\[|\\[/)({letter})(?!\\[/red])"
        elif letter == "e":
            pat = f"(?<!\\[red]|\\[r|\\[/r)({letter})(?!\\[/red])"
        elif letter == "d":
            pat = f"(?<!\\[red]|\\[re|\\[/re)({letter})(?!\\[/red])"
        elif letter == "/":
            pat = f"(?<!\\[red]|\\[red]\\w\\[)({letter})(?!\\[/red])"
        elif letter == ".":
            pat = "(?<!\\[red])(\\.)(?!\\[/red])"
        elif letter == "\\":
            pat = "(?<!\\[red])(\\\\)(?!\\[/red])"
        else:
            pat = f"(?<!\\[red])({letter})(?!\\[/red])"
        print(string, file=file)
        string, matches = re.subn(
            pat, r"[red]\1[/red]", string, flags=flags, count=counts[letter]
        )
        print(string, matches, file=file)
        if matches < counts[letter]:
            file.close()
            return (None, False)
    node.label = Text.from_markup(string)
    file.close()
    return (node, True)


# def search(pattern, nodes):
#     nodes = [contains_letters(pattern, node) for node in nodes]
#     nodes = list(map(lambda x: x[0], filter(lambda x: x[1], nodes)))
#     label_map = {node.label.plain: node for node in nodes}
#     node_labels = [
#         tup[0] for tup in process.extract(pattern, list(label_map.keys()), limit=500)
#     ]
#     return [label_map[label] for label in node_labels]


def search(pattern, nodes):
    label_map = {node.label: node for node in nodes}
    node_labels = [
        tup[0] for tup in process.extract(pattern, list(label_map.keys()), limit=500)
    ]
    return [label_map[label] for label in node_labels]
