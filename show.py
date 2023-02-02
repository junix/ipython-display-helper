
import itertools
import pandas as pd
from dataclasses import dataclass
from typing import Any
import inspect
import types

_attrs = (
    '__name__',
    '__qualname__',
    '__module__',
    '__package__',
    '__loader__',
    '__spec__',
    '__file__',
    '__path__',
    '__class__',
    '__dict__',
    '__slots__',
    '__sizeof__',
    '__hash__',
    '__call__',

    '__format__',
    '__str__',
    '__repr__',


    '__new__',
    '__init__',
    '__del__',
    '__cantrace__',



    # math ops
    '__add__',
    '__iadd__',
    '__radd__',
    '__ladd__',
    '__sub__',
    '__isub__',
    '__rsub__',
    '__lsub__',

    '__getattribute__',
    '__getattr__',
    '__setattr__',
    '__delattr__',

    # comparison
    '__lt__',
    '__le__',
    '__eq__',
    '__ne__',
    '__gt__',
    '__ge__',

    '__neg__',
    '__pos__',
    '__abs__',
    '__invert__',

    # bitwise ops

    '__lshift__',
    '__ilshift__',
    '__rlshift__',
    '__rshift__',
    '__irshift__',
    '__rrshift__',
    '__xor__',
    '__ixor__',
    '__rxor__',
    '__or__',
    '__ior__',
    '__ror__',
    '__and__',
    '__iand__',
    '__rand__'
    '__invert__'
    '__round__',
    '__trunc__',
    '__floor__',
    '__ceil__',
    '__divmod__',
    '__rdivmod__',
    '__mod__',
    '__rmod__',
    '__imod__',
    '__div__',
    '__rdiv__',
    '__idiv__',
    '__floordiv__',
    '__rfloordiv__',
    '__ifloordiv__',
    '__mul__',
    '__rmul__',
    '__imul__',
    '__pow__',
    '__rpow__',
    '__ipow__',
    '__matmul__',
    '__rmatmul__',
    '__imatmul__',
    '__truediv__',
    '__rtruediv__',
    '__itruediv__',

    # logical ops
    '__and__',
    '__or__',




    # functions
    '__code__',
    '__annotations__',
    '__closure__',
    '__globals__',
    '__builtins__',
    '__defaults__',
    '__kwdefaults__',
    '__self__',
    '__func__',
    '__wrapped__',
    '__iscoroutinefunction__',
    '__isgeneratorfunction__',
    '__isabstractmethod__',
    '__closure_cells__',

    # context managers
    '__enter__',
    '__exit__',

    # descriptor
    '__get__',
    '__set__',
    '__delete__',

    # iterators
    '__next__',
    '__iter__',
    '__getitem__',
    '__setitem__',
    '__delitem__',
    '__missing__',
    '__len__',
    '__reversed__',

    '__contains__',
    '__weakref__',

    '__bool__',
    '__int__',
    '__index__',
    '__float__',
    '__complex__',

    '__match_args__',

    '__mro__',
    '__mro_entries__',
    '__base__',
    '__bases__',
    '__subclasses__',
    '__init_subclass__',
    '__instancecheck__',
    '__subclasscheck__',
    '__subclasshook__',
    '__class_getitem__',
    '__prepare__',
    '__set_name__',


    '__getnewargs__',
    '__getnewargs_ex__',
    '__getinitargs__',
    '__getstate__',
    '__setstate__',
    '__reduce__',
    '__reduce_ex__',
    '__copy__',
    '__deepcopy__',
    '__dir__',
    '__doc__',
    '__text_signature__',


    # coroutines
    '__await__',
    '__anext__',
    '__aiter__',
    '__aenter__',
    '__aexit__',

    # exceptions
    '__context__',
    '__cause__',
    '__suppress_context__',
    '__traceback__',
    '__traceback_hide__',


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
    type: str | None
    sig: str | None | inspect.Signature
    value: Any
    overwrite: str = ''

    # def __str__(self) -> str:
    #     return f"{self.name:<20} {self.type:<20} {self.value}"


def type_name(obj):
    return type(obj).__name__


def get_signature(call):
    try:
        sig = inspect.signature(call)
        if sig.return_annotation is inspect.Signature.empty:
            sig = sig.replace(return_annotation='▧')
        return str(sig).replace("'", '')
    except:
        return type(call).__name__


def is_no_arg_callable(x) -> bool:
    if not callable(x) or inspect.isbuiltin(x):
        return False

    try:
        sig = inspect.signature(x)
        return not sig.parameters
    except:
        return False


def _uniq(iterable):
    seen = set()
    for x in iterable:
        if x not in seen:
            yield x
            seen.add(x)


def _attr_type(v):
    attr_type = type(v).__name__
    if inspect.isfunction(v):
        attr_type = 'function'
    elif inspect.ismethod(v):
        attr_type = 'method'
    elif inspect.isgetsetdescriptor(v):
        attr_type = 'getsetdescriptor'
    elif inspect.ismemberdescriptor(v):
        attr_type = 'memberdescriptor'
    elif inspect.isdatadescriptor(v):
        attr_type = 'datadescriptor'
    elif inspect.isgenerator(v):
        attr_type = 'generator'

    return attr_type

def is_overwrite(f):
    if not callable(f):
        return False
    match type(f).__name__:
        case 'method-wrapper':
            self = f.__self__
            class_func = getattr(type(self), f.__name__,None)
            return class_func is not getattr(object, f.__name__,None)
        case 'method'|"function":
            return True
        case 'builtin_function_or_method':
            return False
        case "wrapper_descriptor":
            return f is not getattr(object, f.__name__,None)
        case _:
            print(">>>>", type(f))
    return False

def is_dunder(attr):
    return attr.startswith('__') and attr.endswith('__')


def get_attr_info(obj, attr, *, skip_none=True):
    from dataclasses import replace
    if skip_none and not hasattr(obj, attr):
        return

    v = getattr(obj, attr, None)
    spec = Attr(name=attr, type=_attr_type(v), value=v, sig='')

    if is_dunder(attr) and is_overwrite(v):
        spec = replace(spec, overwrite='▧')

    if obj.__class__ is type and inspect.ismethod(v):
        spec = replace(spec, type=spec.type+"[staticmethod]")

    match(attr, v):
        case _, None:
            if not skip_none:
                yield replace(spec, value='-', type='-')

        case '__lt__' | '__le__' | '__eq__' | '__ne__' | '__gt__' | '__ge__', func:
            # if is overwrite, skip
            match type(v).__name__:
                case 'method' | 'function':
                    yield replace(spec, sig=get_signature(func))
                case _:
                    return

        case '__closure__', closure:
            yield replace(spec, value=[c.cell_contents for c in closure])
        case '__class__', _:
            yield replace(spec, value=v.__name__)
        case '__subclasses__', classes:
            yield replace(spec, value=tuple(c.__name__ for c in classes()))
        case '__mro__' | '__bases__' | '__subclasses__', classes:
            yield replace(spec, value=tuple(c.__name__ for c in classes))
        case '__dir__'|'__doc__', dirs:
            yield replace(spec, value='')
        case '__init__', '__call__', call:
            yield replace(spec, sig=get_signature(call), value='')
        case[_, func] if is_dunder(attr) and is_no_arg_callable(func):
            result = func()
            yield replace(spec, value=result, sig=f'()->{type_name(result)}')
        case '__globals__', globals:
            yield replace(spec, value=f"{len(globals)} vars")
        case '__dict__', attr_dict:
            yield replace(spec, value=v.keys())
        case '__code__', code:
            yield replace(spec, value=code.co_name)
        case _, str(v) | int(v) | float(v) | bool(v) | bytes(v):
            yield spec
        case _, dict() | types.MappingProxyType():
            if len(v) < 10:
                yield spec
            else:
                yield replace(spec, value=f"{len(v)} vars")
        case[_, call] if callable(call):
            yield replace(spec, sig=get_signature(call))
        case _:
            yield spec


def fetch_attrs(obj, *, attrs=_attrs, **kwargs):
    for attr in attrs:
        yield from get_attr_info(obj, attr, **kwargs)


def tabulate_attrs(attrs: list[Attr]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            'type': [x.type for x in attrs],
            'sig': [x.sig for x in attrs],
            'value': [x.value for x in attrs],
            'overwrite': [x.overwrite for x in attrs],
        },
        index=[x.name for x in attrs],
    )


def desc(obj, *, attrs=_attrs, include_all: bool = False, **kwargs):
    if include_all:
        attrs = list(_uniq(itertools.chain(attrs, [attr for attr, _ in inspect.getmembers(obj)])))
    return tabulate_attrs(tuple(fetch_attrs(obj, attrs=attrs, **kwargs)))


def compare_attrs(xs, *, attrs=None, hidden_common=True):
    if isinstance(xs, list | tuple):
        xs = {str(x): x for x in xs}

    attr_set = {attr for x in xs.values() for attr,_ in inspect.getmembers(x)}
    for x in attr_set:
        assert x in _attrs, f"{x} not in _attrs, please add it to _attrs"

    attrs = [x for x in _attrs if x in attr_set]
    attrs = pd.DataFrame(
        data={
            k: ['√' if hasattr(v, attr) else 'ㄨ' for attr in attrs]
            for k, v in xs.items()
        },
        index=attrs
    )

    if hidden_common and len(attrs) > 1:
        h, *ts = attrs
        print('>>>>>',ts)
        index, *indices = (attrs[t] == attrs[h] for t in ts)
        for x in indices:
            index &= x
        attrs = attrs[~index]

    return attrs


def block_display(df: pd.DataFrame):
    import IPython
    from IPython.display import display, HTML
    from itertools import pairwise
    n = 0
    while n <= df.shape[0]:
        display(HTML(df.iloc[n:n+15].to_html()))
        n += 15


def h(o):
    from docutils.core import publish_string
    from IPython.display import display_html,HTML

    import contextlib
    import io
    
    doc = getattr(o, '__doc__',None)
    if not doc:
        help(o)
        return

    with contextlib.redirect_stderr(io.StringIO()):
        try:
            display_html(HTML(publish_string(doc, writer_name="html").decode('utf-8')))
        except:
            help(o)