# Copyright (c) 2022 Nagarjuna Kumarappan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author: Nagarjuna Kumarappan <nagarjuna.412@gmail.com>
import os
import regex as re
import rich_click as click
import tempfile
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


# def contains_letters(pattern, node):
#     file = open(
#         "/Users/gustavkristensen/prototypes/bookmark/bookmark/searchlog.txt", "a"
#     )
#     letters = list(pattern)
#     counts = Counter(letters)
#     string = node.label
#     flags = re.I if all(letter.islower() for letter in letters) else 0
#     for letter in list(counts.keys()):
#         if letter == "r":
#             pat = f"(?<!\\[red]|\\[|\\[/)({letter})(?!\\[/red])"
#         elif letter == "e":
#             pat = f"(?<!\\[red]|\\[r|\\[/r)({letter})(?!\\[/red])"
#         elif letter == "d":
#             pat = f"(?<!\\[red]|\\[re|\\[/re)({letter})(?!\\[/red])"
#         elif letter == "/":
#             pat = f"(?<!\\[red]|\\[red]\\w\\[)({letter})(?!\\[/red])"
#         elif letter == ".":
#             pat = "(?<!\\[red])(\\.)(?!\\[/red])"
#         elif letter == "\\":
#             pat = "(?<!\\[red])(\\\\)(?!\\[/red])"
#         else:
#             pat = f"(?<!\\[red])({letter})(?!\\[/red])"
#         print(string, file=file)
#         string, matches = re.subn(
#             pat, r"[red]\1[/red]", string, flags=flags, count=counts[letter]
#         )
#         print(string, matches, file=file)
#         if matches < counts[letter]:
#             file.close()
#             return (None, False)
#     node.label = Text.from_markup(string)
#     file.close()
#     return (node, True)


# def search(pattern, nodes):
#     nodes = [contains_letters(pattern, node) for node in nodes]
#     nodes = list(map(lambda x: x[0], filter(lambda x: x[1], nodes)))
#     label_map = {node.label.plain: node for node in nodes}
#     node_labels = [
#         tup[0] for tup in process.extract(pattern, list(label_map.keys()), limit=500)
#     ]
#     return [label_map[label] for label in node_labels]


def search_thefuzz(pattern, nodes):
    label_map = {node.label: node for node in nodes}
    node_labels = [
        tup[0] for tup in process.extract(pattern, list(label_map.keys()), limit=500)
    ]
    return [label_map[label] for label in node_labels]


def search_fzf(choices=None, fzf_options="", delimiter="\n", fzf_path="fzf"):
    # convert lists to strings [ 1, 2, 3 ] => "1\n2\n3"
    choices_str = delimiter.join(map(str, choices))
    selection = []

    with tempfile.NamedTemporaryFile(delete=False) as input_file:
        with tempfile.NamedTemporaryFile(delete=False) as output_file:
            # Create an temp file with list entries as lines
            input_file.write(choices_str.encode("utf-8"))
            input_file.flush()

    # Invoke fzf externally and write to output file
    os.system(f'{fzf_path} {fzf_options} < "{input_file.name}" > "{output_file.name}"')

    # get selected options
    with open(output_file.name, encoding="utf-8") as f:
        for line in f:
            selection.append(line.strip("\n"))

    os.unlink(input_file.name)
    os.unlink(output_file.name)

    return selection


def search(pattern, nodes, fzf_path=""):
    label_map = {node.label.rstrip("\r"): node for node in nodes}
    if fzf_path:
        node_labels = search_fzf(list(label_map.keys()), fzf_options=f"-f {pattern}", fzf_path=fzf_path)
        result = [label_map[label] for label in node_labels]
    else:
        result = search_thefuzz(pattern, nodes)
    return result
