# ANSI codes для вывода цветного текста
import platform
from functools import cache


def platform_aware_colored_username(name: str) -> str:
    if platform.system() == "Windows":
        return name
    return colored_username(name)


@cache
def colored_username(name: str) -> str:
    return f"{username_to_color(name)}{name}{reset_color()}"


def username_to_color(name: str) -> str:
    hash_ = hash(name)
    r = (hash_ << 16) & 256
    g = (hash_ << 8) & 256
    b = (hash_ << 0) & 256
    return rgb_color(r, g, b)


def rgb_color(r: int, g: int, b: int):
    return f"\x1b[38;2;{r};{g};{b}m"


def reset_color():
    return "\x1b[0m"
