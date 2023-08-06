"""a dependency used by another package..."""

__version__ = "0.0.2"


def emphasizer(lol_string: str, *, max_emphasis: int) -> str:
    return lol_string + "!" * max(lol_string.count("l"), max_emphasis)
