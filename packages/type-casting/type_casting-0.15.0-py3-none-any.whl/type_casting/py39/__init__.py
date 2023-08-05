import collections
import dataclasses
import decimal
import functools
import typing
from typing import Any, Literal, Union

from .._common import (
    Call,
    CastingError,
    EmptyDict,
    EmptyTuple,
    GetAttr,
    _analyze__CallWithArgsAndKwargs,
    _analyze__CallWithInspect,
    _analyze_complex,
    _analyze_Decimal,
    _analyze_deque,
    _analyze_dict,
    _analyze_float,
    _analyze_GetAttr,
    _analyze_list,
    _analyze_Literal,
    _analyze_set,
    _analyze_tuple,
    _analyze_type,
    _analyze_Union,
    _CallWithArgsAndKwargs,
    _CallWithInspect,
    _cast_kwargs,
    _identity1,
    override,
)


def cast(cls, x, implicit_conversions=None):
    return _analyze(cls, {} if implicit_conversions is None else implicit_conversions)(
        x
    )


def _analyze(cls, implicit_conversions):
    if cls in implicit_conversions:
        return implicit_conversions[cls]
    elif dataclasses.is_dataclass(cls):
        fields = dataclasses.fields(cls)
        return functools.partial(
            _cast_kwargs,
            cls,
            {f.name: _analyze(f.type, implicit_conversions) for f in fields},
            set(
                f.name
                for f in fields
                if (f.default == dataclasses.MISSING)
                and (f.default_factory == dataclasses.MISSING)
            ),
        )
    elif (
        isinstance(cls, type)
        and issubclass(cls, dict)
        and hasattr(cls, "__annotations__")
        and hasattr(cls, "__total__")
    ):
        return functools.partial(
            _cast_kwargs,
            cls,
            {
                k: _analyze(v, implicit_conversions)
                for k, v in typing.get_type_hints(cls).items()
            },
            set(typing.get_type_hints(cls)) if cls.__total__ else set(),
        )
    elif cls == Any:
        return _identity1
    elif cls == decimal.Decimal:
        return _analyze_Decimal
    elif cls == complex:
        return _analyze_complex
    elif cls == float:
        return _analyze_float
    elif origin := typing.get_origin(cls):
        if origin == GetAttr:
            return functools.partial(
                _analyze_GetAttr, _analyze(cls.__args__[0], implicit_conversions)
            )
        elif origin == _CallWithArgsAndKwargs:
            path, args, kwargs = cls.__args__
            return functools.partial(
                _analyze__CallWithArgsAndKwargs,
                str(cls),
                _analyze(GetAttr[path], implicit_conversions),
                _analyze(args, implicit_conversions),
                _analyze(kwargs, implicit_conversions),
            )
        elif origin == _CallWithInspect:
            path = cls.__args__[0]
            return functools.partial(
                _analyze__CallWithInspect,
                str(cls),
                _analyze,
                implicit_conversions,
                _analyze(GetAttr[path], implicit_conversions),
            )
        elif origin == Literal:
            return functools.partial(_analyze_Literal, str(cls), cls.__args__)
        elif origin in (
            set,
            collections.abc.Set,
            collections.abc.MutableSet,
        ):
            return functools.partial(
                _analyze_set, _analyze(cls.__args__[0], implicit_conversions)
            )
        elif origin in (
            list,
            collections.abc.Sequence,
            collections.abc.MutableSequence,
            collections.abc.Iterable,
            collections.abc.Iterator,
        ):
            return functools.partial(
                _analyze_list, _analyze(cls.__args__[0], implicit_conversions)
            )
        elif origin in (
            dict,
            collections.abc.Mapping,
            collections.abc.MutableMapping,
        ):
            return functools.partial(
                _analyze_dict,
                _analyze(cls.__args__[0], implicit_conversions),
                _analyze(cls.__args__[1], implicit_conversions),
            )
        elif origin == collections.deque:
            return functools.partial(
                _analyze_deque, _analyze(cls.__args__[0], implicit_conversions)
            )
        elif origin == tuple:
            return functools.partial(
                _analyze_tuple,
                str(cls),
                tuple(_analyze(vcls, implicit_conversions) for vcls in cls.__args__),
            )
        elif origin == Union:
            return functools.partial(
                _analyze_Union,
                str(cls),
                list(_analyze(ucls, implicit_conversions) for ucls in cls.__args__),
            )
        else:
            raise ValueError(f"Unsupported class {cls}: {type(cls)}")
    elif isinstance(cls, type):
        return functools.partial(_analyze_type, cls)
    else:
        raise ValueError(f"Unsupported class {cls}: {type(cls)}")
