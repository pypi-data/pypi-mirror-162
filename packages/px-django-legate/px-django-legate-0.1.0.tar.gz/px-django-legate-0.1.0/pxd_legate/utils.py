import string
import random
from functools import lru_cache
from typing import Sequence
from django.utils.module_loading import import_string


ALPHABET = string.ascii_letters.split()


@lru_cache
def cached_import_string(path: str):
    return import_string(path)


def upset(current, add):
    return (
        (current if isinstance(current, set) else set(current))
        |
        (add if isinstance(add, set) else set(add))
    )


def make_random_code(symbols: int, alphabet: Sequence[str] = ALPHABET) -> str:
    return ''.join(random.sample(alphabet * symbols, symbols))
