import collections.abc
import sys
import warnings
from typing import Optional, Union, Tuple, Dict, TypeVar, Type, Any, Callable, cast
from abc import ABC

import dataclasses


class IsDataclass(type):
    # TODO: unquote once we enforce python 3.9
    __dataclass_fields__: Dict[str, "dataclasses.Field[Any]"]


class IsTypingType(ABC):
    __args__: Tuple[type, ...]


Tp = TypeVar("Tp")


def deserialize(T: Type[Tp]) -> Callable[[Any], Tp]:
    """Create a deserializer for the type :T:.

    It handles dataclasses, sequences, typing.Optional and primitive types.

    :returns: A deserializer, converting a dict, list or primitive to :T:
    :raises ValueError:
    """

    def _deserialize(data: Any) -> Tp:
        seq_type = sequence_type(T)
        if seq_type is not None:
            try:
                item_type = cast(IsTypingType, T).__args__[0]
            except AttributeError as e:
                raise ValueError(
                    f"Sequence of type {seq_type.__name__} without item type"
                ) from e
            return cast(Tp, seq_type(map(deserialize(item_type), data)))
        if dataclasses.is_dataclass(T):
            fields = dataclasses.fields(T)
            unexpected_keys = set(data.keys()) - set(f.name for f in fields)
            if unexpected_keys:
                warnings.warn(
                    f"{T.__name__}: Unexpected keys: " + ", ".join(unexpected_keys)
                )
            converted_data = {
                f.name: deserialize(f.type)(data.get(f.name, f.default)) for f in fields
            }
            return cast(Tp, cast(IsDataclass, T)(**converted_data))
        opt_type = optional_type(T)
        if opt_type is not None:
            return cast(Tp, None if data is None else opt_type(data))
        dct_type = dict_type(T)
        if dct_type is not None:
            key_type, val_type = dct_type
            return cast(
                Tp,
                {
                    deserialize(key_type)(key): deserialize(val_type)(val)
                    for key, val in data.items()
                },
            )

        return cast(Tp, cast(type, T)(data))

    return _deserialize


def optional_type(T: type) -> Optional[type]:
    """For Optional types provided by typing, return the underlying python type,
    else None.
    * E.g. returns int for typing.Optional[int].
    """
    if getattr(T, "__origin__", None) is not Union:
        return None
    try:
        T1, T2 = T.__args__  # type: ignore
    except ValueError:
        return None
    if isinstance(None, T1):
        return cast(type, T2)
    if isinstance(None, T2):
        return cast(type, T1)
    return None


# Starting with python 3.7, the typing module has a new API
_origin_attr = "__extra__" if sys.version_info < (3, 7) else "__origin__"


def sequence_type(t: type) -> Optional[type]:
    """For sequence types provided by typing, return the underlying python type,
    else None.
    * E.g. returns tuple for typing.Tuple[int]
    """

    t_origin = getattr(t, _origin_attr, None)
    if isinstance(t_origin, type) and issubclass(t_origin, collections.abc.Sequence):
        return t_origin
    return None


def dict_type(t: type) -> Optional[Tuple[type, type]]:
    """For dicts provided by typing, return the underlying python types,
    else None.
    * E.g. returns (int, str) for typing.Dict[int, str].
    """

    t_origin = getattr(t, _origin_attr, None)
    if t_origin is dict:
        return t.__args__  # type: ignore
    return None
