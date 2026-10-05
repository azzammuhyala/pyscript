from difflib import get_close_matches
from itertools import pairwise
from typing import Iterable

def get_similarity_ratio(string1: str, string2: str) -> float:
    bigram1 = set(s1 + s2 for s1, s2 in pairwise(string1))
    bigram2 = set(s1 + s2 for s1, s2 in pairwise(string2))
    max_bigrams_count = max(len(bigram1), len(bigram2))
    return len(bigram1 & bigram2) / max_bigrams_count if max_bigrams_count else 0.0

def get_closest(elements: Iterable[str], target: str, cutoff: float = 0.6) -> str | None:
    best_match = None
    best_score = 0.0

    for element in elements:
        score = get_similarity_ratio(target, element)
        if score >= cutoff and score > best_score:
            best_score = score
            best_match = element

    return best_match

def diff_get_closest(elements: Iterable[str], target: str, cutoff: float = 0.6) -> str | None:
    closest = get_close_matches(target, elements, 1, cutoff)
    return closest[0] if closest else None