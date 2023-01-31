
from dataclasses import dataclass
from typing import Any
import inspect
import types

_attrs = (
    '__name__',
    '__module__',
    '__class__',
    '__dict__',
    '__sizeof__',
    '__code__',
    '__annotations__',
    '__closure__',
    '__globals__',
    '__builtins__',
    '__defaults__',
    '__kwdefaults__',

    '__get__',
    '__set__',
    '__delete__',

    '__next__',
    '__iter__',
    '__len__',
    '__weakref__',
    '__reversed__',
    '__contains__',
    '__bool__',
    '__hash__',

    '__match_args__',

    '__mro__',
    '__base__',
    '__bases__',
    '__subclasses__',

    'co_argcount',
    'co_cellvars',
    'co_code',
    'co_consts',
    'co_filename',
    'co_firstlineno',
    'co_flags',
    'co_freevars',
    'co_kwonlyargcount',
    'co_lines',
    'co_linetable',
    'co_lnotab',
    'co_name',
    'co_names',
    'co_nlocals',
    'co_posonlyargcount',
    'co_stacksize',
    'co_varnames',
)


@dataclass
class Attr:
    name: str
    type: str | None | inspect.Signature
    value: Any

    # def __str__(self) -> str:
    #     return f"{self.name:<20} {self.type:<20} {self.value}"


def type_name(obj):
    return type(obj).__name__


def is_no_arg_callable(x) -> bool:
    try:
        return len(inspect.signature(x).parameters) == 0
    except:
        return False

def get_attr_info(obj, attr, *, skip_none=True):
    from dataclasses import replace
    if skip_none and not hasattr(obj, attr):
        return

    attr_v = getattr(obj, attr, None)
    attr_type = type(attr_v).__name__
    spec = Attr(attr, attr_type, attr_v)
    match (attr, attr_v):
        case _, None:
            if not skip_none:
                yield replace(spec, value='-', type='-')
        case '__closure__', closure:
            yield replace(spec, value=[c.cell_contents for c in closure])
        case '__class__', cls:
            yield replace(spec, value=cls.__name__)
        case '__mro__'|'__bases__', classes:
            yield replace(spec, value=tuple(c.__name__ for c in classes))
        case [_, func] if is_no_arg_callable(func):
            result = func()
            yield replace(spec, value=result, type=f'()->{type_name(result)}')
        case '__globals__', globals:
            yield replace(spec, value=f"{len(globals)} vars")
        case '__dict__', attr_dict:
            yield replace(spec, value=attr_v.keys())
        case '__code__', code:
            yield replace(spec, value=code.co_name)
        case _, str(v) | int(v) | float(v) | bool(v)|bytes(v):
            yield spec
        case _, dict()|types.MappingProxyType():
            if len(attr_v) < 10:
                yield spec
            else:
                yield replace(spec, value=f"{len(attr_v)} vars")
        case [_, call] if callable(call):
            try:
                sig = inspect.signature(call)
                if sig.return_annotation is inspect.Signature.empty:
                    sig = sig.replace(return_annotation='▧')
                yield replace(spec, type=str(sig))
            except e:
                print(e)
                yield spec
        case _:
            yield spec


def fetch_attrs(obj, *, attrs=_attrs, **kwargs):
    for attr in attrs:
        yield from get_attr_info(obj, attr, **kwargs)


import pandas as pd


def tabulate_attrs(attrs: list[Attr]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            'type': [x.type for x in attrs],
            'value': [x.value for x in attrs]
        },
        index=[x.name for x in attrs],
    )