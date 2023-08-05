"""a dependency used by another package..."""

__version__ = "0.0.1"


def emphasizer(lol_string: str) -> str:
    return lol_string + "!" * lol_string.count("l")
