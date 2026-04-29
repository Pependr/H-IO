from hio._internals.typingtools import get_attrs, get_type

from typing import Any, get_args
from annotationlib import get_annotations


class Field[T]:
    def __init__(
        self, *,
        ftype: type[T],
        optional: bool = False,
    ) -> None:
        self.type = ftype
        self.optional = optional

class BaseModel:
    def __init_subclass__(cls) -> None:
        cls.__fields__: dict[str, Field[Any]] = {}
        for name, ftype in get_annotations(cls).items():
            cls.__fields__[name] = Field(
            ftype=get_type(ftype),
            optional=(type(None) in get_args(ftype)),
            )

    @classmethod
    def describes_object(cls, obj: object) -> bool:
        attrs: list[str] = get_attrs(obj)

        for name, field in cls.__fields__.items():
            if name not in attrs:
                if field.optional: continue
                else: return False
            
            if type(getattr(obj, name)) != field.type:
                return False

            attrs.remove(name)

        return attrs == []