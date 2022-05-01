import regex as re
from collections import Counter
from thefuzz import process


def contains_letters(pattern, string):
    letters = list(pattern)
    counts = Counter(letters)
    flags = re.I if all(letter.islower() for letter in letters) else 0
    for letter in letters:
        matches = len(re.findall(letter, string, flags=flags))
        if matches < counts[letter]:
            return False
    return True


def search(pattern, array):
    array = filter(lambda x: contains_letters(pattern, x), array)
    return process.extract(pattern, array, limit=10)
