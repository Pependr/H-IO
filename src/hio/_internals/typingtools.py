from typing import Protocol, ClassVar, Any, runtime_checkable, get_origin
from dataclasses import Field
from collections.abc import Callable


def get_attrs(obj: object) -> list[str]:
    return [
        a for a in dir(obj) if not (
            a.startswith("_")
            | isinstance(getattr(obj, a), Callable)
        )
    ]


def get_type(tp: type) -> type:
    orig = get_origin(tp)
    if orig is None:
        return tp
    return orig


def is_built_in(obj: object) -> bool:
    return ((obj is None)
            | any(isinstance(obj, t) for t in (str, int, float, bool)))


@runtime_checkable
class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]

    @classmethod
    def __subclasshook__(cls, subclass: type, /) -> bool:
        if getattr(subclass, "__dataclass_fields__", None) is not None:
            return True
        return super().__subclasshook__(subclass)