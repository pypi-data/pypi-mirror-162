from typing import Tuple, TypeVar, Callable, Optional


def split_first(s: str, separator: str) -> Tuple[str, str]:
    index = s.index(separator)
    return s[:index], s[index + 1:]


def remove_prefix(s: str, prefix: str) -> Optional[str]:
    if s.startswith(prefix):
        return s[len(prefix):]
    return None


T = TypeVar("T")
U = TypeVar("U")


def apply_if_some(f: Callable[[T], U], option: Optional[T]) -> Optional[U]:
    if option is None:
        return None
    return f(option)
