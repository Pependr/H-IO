from typing import Protocol, ClassVar, Any


def is_built_in(obj: object) -> bool:
    return any(isinstance(obj, t) for t in (str, int, float, bool)) or obj is None


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]