from typing import TypedDict, Any


class HintedCls(TypedDict):
    cls: str
    val: Any


def add_cls_hint(cls: type, data: Any) -> HintedCls:
    return {
        "cls": f"{cls.__module__}.{cls.__name__}",
        "val": data,
    }