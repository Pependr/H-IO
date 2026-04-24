from hio._internals.exceptions import RegistryError
from hio._internals.typingtools import is_built_in, DataclassInstance

from typing import Callable, Any, cast
from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path


type EncoderFn[I] = Callable[[I], Any]
type Registry[I] = dict[type[I], EncoderFn[I]]


_REGISTRY: Registry[Any] = {}


def register[I](
    tp: type[I], overwrite_parent: bool = False
) -> Callable[[EncoderFn[I]], EncoderFn[I]]:
    if is_dataclass(tp) and not overwrite_parent:
        raise ValueError(f"Dataclasses handling is built in")

    for key in _REGISTRY.keys():
        if (issubclass(tp, key) and not overwrite_parent) or (tp is key):
            raise RegistryError(key, _REGISTRY,
                f"Encoder for type {key.__name__} is already registered")

    def decorator(fn: EncoderFn[I]) -> EncoderFn[I]:
        _REGISTRY[tp] = fn
        return fn

    return decorator


def resolve[I](tp: type[I]) -> EncoderFn[I]:
    if encoder := _REGISTRY.get(tp):
        return encoder

    for key in _REGISTRY.keys():
        if issubclass(tp, key):
            return _REGISTRY[key]
    else:
        if is_dataclass(tp):
            return cast(EncoderFn[I], encode_dataclass)

        raise RegistryError(tp, _REGISTRY,
            f"Encoder for type {tp.__name__} is not registered")


def pop[I](tp: type[I]) -> EncoderFn[I]:
    if tp in _REGISTRY:
        return _REGISTRY.pop(tp)

    for key in _REGISTRY.keys():
        if issubclass(tp, key):
            return _REGISTRY.pop(key)
    else:
        raise RegistryError(tp, _REGISTRY,
            f"Encoder for type {tp.__name__} is not registered")


def encode(obj: object) -> Any:
    if is_built_in(obj):
        return obj
    
    encoder = resolve(type(obj))

    return encoder(obj)


def encode_dataclass(dcl: DataclassInstance) -> dict[str, Any]:
    encoded: dict[str, Any] = {}
    
    flds = ((f.name, getattr(dcl, f.name)) for f in fields(dcl))

    for name, value in flds:
        encoded[name] = encode(value)

    return encoded


@register(Sequence)
def encode_sequence(seq: Sequence[Any]) -> tuple[Any]:
    return tuple(encode(i) for i in seq)


@register(Mapping)
def encode_mapping(map: Mapping[Any, Any]) -> dict[str, Any]:
    return {
        str(encode(k)): encode(v) for k, v in map.items()
    }


@register(Enum)
def encode_enum(en: Enum) -> str:
    return en.name


@register(Path)
def encode_path(path: Path) -> str:
    return path.as_posix()