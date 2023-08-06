import inspect
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, Optional, Type, get_type_hints

from rich import print
from versions import Version  # noqa
from yarl import URL  # noqa

from src import hoist
from src.hoist._typing import *  # noqa

NEWLINE: str = "\n"
HIDDEN_DERIVES = {"Exception", "object"}
Message = hoist.Message
Server = hoist.Server
Connection = hoist.Connection


def _patch_hint(hint_str: str) -> str:
    return (
        hint_str.replace("NoneType", "None")
        .replace("src.", "")
        .replace(
            "typing.",
            "",
        )
    )


def _decode_hint(hint: Type[Any]) -> str:
    string = str(hint)

    if ("typing." in string) and ("_typing." not in string):
        return _patch_hint(string)

    return _patch_hint(hint.__name__)


def _get_source(func: Callable) -> str:
    code = func.__code__
    path_obj = Path(code.co_filename)
    path: str = path_obj.name
    return f"[Source](https://github.com/ZeroIntensity/hoist/blob/master/src/hoist/{path}#L{code.co_firstlineno})\n\n"  # noqa


def _generate_function(
    func: Callable,
    *,
    nm: bool = True,
) -> str:
    hints = get_type_hints(func, globalns=globals())
    name: str = func.__name__
    ret = hints.pop("return") if "return" in hints else None
    params = [f"{param}: {_decode_hint(typ)}" for param, typ in hints.items()]
    paramstring = f"\n    {f', {NEWLINE}    '.join(params)}\n" if params else ""  # noqa

    sig = f"""{f'#### `{name}`{NEWLINE}' if nm else ''}```py

def {name}({paramstring}){f' -> {_decode_hint(ret)}' if ret else ''}
```"""
    fdoc = func.__doc__
    source = _get_source(func) if name != "__init__" else ""

    return f"{sig}\n\n{f'*{fdoc}*' if fdoc else ''}\n\n{source}---\n"


def _generate_property(
    prop: Any,
) -> str:
    get = prop.fget
    name: str = get.__name__
    ret = get_type_hints(get)["return"]
    return f"""#### `{name}`

```py
@property
def {name}() -> {_decode_hint(ret)}
```

*{prop.__doc__}*

{_get_source(get)}---"""


def generate_class(
    objects: Dict[str, str],
    parent: str,
    cl: Type[Any],
) -> None:
    """Generate a class reference."""
    actual_doc = cl.__doc__
    parent_class = cl.__base__
    pname: str = parent_class.__name__

    derives: str = (
        f"*Derives from `{parent_class.__module__.replace('src.', '')}.{pname}`*"  # noqa
        if pname not in HIDDEN_DERIVES
        else ""
    )
    doc = f"{derives}\n\n**{actual_doc}**" if actual_doc else ""

    functions = []
    properties = []

    for i in dir(cl):
        if not i.startswith("_"):
            if i in cl.__dict__:
                attr = getattr(cl, i)
                if callable(attr):
                    functions.append(_generate_function(attr))
                else:
                    if hasattr(attr, "fget"):
                        properties.append(_generate_property(attr))

    constructor = (
        f"\n\n{_generate_function(cl.__init__)}"
        if (not issubclass(cl, Exception)) or (cl.__name__ == "_ResponseError")
        else "\n\n---"
    )

    objects[
        parent
    ] = f"{doc}{constructor}\n\n{NEWLINE.join(functions)}{NEWLINE.join(properties)}"  # noqa


def generate_function(
    objects: Dict[str, str],
    parent: str,
    func: Callable,
) -> None:
    """Generate a function reference."""
    objects[parent] = _generate_function(func, nm=False)


def generate_reference_dict(
    obj: Any,
    objs: Optional[Dict[str, Dict[str, str]]] = None,
) -> Dict[str, Dict[str, str]]:
    """Generate the reference dictionary."""
    objects: Dict[str, Dict[str, str]] = objs or {}

    for i in dir(obj):
        if not i.startswith("__"):
            attr = getattr(obj, i)

            if isinstance(attr, ModuleType):
                if attr.__name__.startswith("src.hoist"):
                    generate_reference_dict(attr, objects)
                continue

            if isinstance(
                attr,
                (
                    str,
                    int,
                    bool,
                    dict,
                    list,
                    float,
                    type(None),
                    tuple,
                ),
            ):
                continue

            mod = str(attr.__module__).replace("src.", "")

            if (not mod.startswith("hoist.")) or (mod == "hoist._typing"):
                continue
            if mod not in objects:
                objects[mod] = {}

            if inspect.isclass(attr):
                generate_class(objects[mod], i, attr)
            elif callable(attr):
                generate_function(objects[mod], i, attr)

    return objects


def generate_reference():
    """Generate the reference document."""
    doc = generate_reference_dict(hoist)

    with open("./docs/reference.md", "w") as f:
        f.write("# Reference\n\n")

        for k, v in doc.items():
            mod = (
                f"`{k}`"
                if k != "hoist.exceptions"
                else f"""`{k}`\n\n!!! note

    Everything in this module derives from `BaseException`, and may be raised.
"""
            )
            dcs = [f"### `{obj}`\n\n{dc}" for obj, dc in v.items()]
            f.write(f"## {mod}\n\n{NEWLINE.join(dcs)}\n\n")

    print("Successfully wrote to [bold blue]reference.md[/]")


if __name__ == "__main__":
    generate_reference()
