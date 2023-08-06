import re
import typing as T
import time
import orjson
from devtools import debug
import edgedb
from .span import safe_span
from .constants import RE_CODE

MUTATION_ACTIONS = ["insert ", "update ", "delete "]


class ExecuteException(Exception):
    pass


class ExecuteConstraintViolationException(ExecuteException):
    pass


def operation_from_query_str(query_str: str) -> str:
    s = query_str.lower()
    for action in MUTATION_ACTIONS:
        if action in s:
            return "mutation"
    return "query"


def simplify_vars(
    query_str: str, variables: dict[str, T.Any]
) -> (str, dict[str, T.Any]):
    new_vars = {}
    new_query_str = query_str + ";"
    for key, val in variables.items():
        if key in new_query_str:
            # strip key and add number to it
            stripped_key = key.split(RE_CODE)[0]
            i = 0
            while True:
                stripped_key_temp = stripped_key + f'{"" if i == 0 else i}'
                if stripped_key_temp not in new_vars:
                    stripped_key = stripped_key_temp
                    break
                i += 1
            new_vars[stripped_key] = val
            new_query_str = re.sub(
                rf"(\$)({key})(\W*)", r"\1" + stripped_key + r"\3", new_query_str
            )
    if new_query_str[-1] == ";":
        new_query_str = new_query_str[0:-1]
    return new_query_str, new_vars


async def query(
    client: edgedb.AsyncIOClient,
    query_str: str,
    variables: T.Optional[T.Dict[str, T.Any]] = None,
    only_one: bool = False,
    print_query: bool = True,
    print_variables: bool = False,
    print_raw_results: bool = False,
) -> T.Optional[dict]:
    """Returns a json str to be parsed by pydantic raw. Errors are raised by the lib!"""
    if not variables:
        variables = {}
    query_str, variables = simplify_vars(query_str, variables)
    query_func = client.query_json if not only_one else client.query_single_json
    start = time.time()
    try:
        with safe_span(
            op=f"edgedb.{operation_from_query_str(query_str)}",
            description=query_str[:200],
        ):
            j_str = await query_func(query=query_str, **variables)
        with safe_span(op="orjson.loads", description=f"len str: {len(j_str)}"):
            j = orjson.loads(j_str)
        if print_raw_results:
            debug(j)
    except edgedb.errors.ConstraintViolationError as e:
        print(f"{e=}")
        if "is prohibited by link target policy" in str(e):
            raise e
        if "violates exclusivity constraint" in str(e):
            field_name = str(e).split(" ")[0].replace("_", " ")
            raise ExecuteConstraintViolationException(
                f"That {field_name} already exists in our system."
            )
        raise e
    except Exception as e:
        print(
            f"EdgeDB Query Exception: {e}, query_str and variables: {query_str=}, {variables=}"
        )
        raise e
    took_ms = (time.time() - start) * 1000
    print_s = ""
    if print_query:
        print_s += f" {query_str=} "
    if print_variables:
        print_s += f" {variables=} "
    if print_s:
        print_s = print_s.strip()
        print(print_s)
    print(f"took {took_ms}")
    return j
