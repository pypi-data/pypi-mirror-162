import typing as T
import random
import string

ALIAS_PATTERN = r">\$(\w+)"
RE_CODE = "04730"


def random_str(n: int, include_re_code: bool = True) -> str:
    pre_str = RE_CODE if include_re_code else ""
    return pre_str + "".join(random.choices(string.ascii_letters + string.digits, k=n))


def chunk_list(lst: list, chunk_size: int) -> T.List[list]:
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(lst: T.List[list]) -> list:
    return [j for sub in lst for j in sub]
