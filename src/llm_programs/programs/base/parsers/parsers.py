from typing import Callable
from llm_programs.utils import IDENTITY

import re

PredicateParser = Callable[[str], bool]

def split_parser(response, separator):
    """
    Parse the response into a list, splitting by the given separator
    """
    return [line.strip() for line in response.split(separator) if line.strip()]


def lines_parser(response):
    """
    Parse the response into a list of lines
    """
    return split_parser(response, "\n")


class YesNoPredicateParser(PredicateParser):
    """
    Parses a string response to determine if it indicates a positive ('Yes')
    or negative ('No') affirmation near the beginning, ignoring common leading
    non-alphabetic characters.

    Returns True for a response effectively starting with a 'Yes' pattern.
    Returns False for an empty response, a response effectively starting with a 'No' pattern.
    Returns `maybe` for a non-empty response that does not match either.
    """

    YES_PATTERNS = [
        r"^\W*yes\b",
    ]

    NO_PATTERNS = [
        r"^\W*no\b",
        r"^\W*there\s+is\s+no\b",
        r"^\W*there\s+are\s+no\b",
    ]

    def __init__(self, maybe: bool = False):
        self.yes_regexes = [re.compile(p, re.IGNORECASE) for p in self.YES_PATTERNS]
        self.no_regexes = [re.compile(p, re.IGNORECASE) for p in self.NO_PATTERNS]
        self.maybe = maybe

    def __call__(self, response: str) -> bool:
        if not response or response.isspace():
            return False

        if any(regex.search(response) for regex in self.yes_regexes):
            return True

        if any(regex.search(response) for regex in self.no_regexes):
            return False

        return self.maybe


def basic_predicate_parser(response: str) -> bool:
    return bool(response) and not response.isspace()