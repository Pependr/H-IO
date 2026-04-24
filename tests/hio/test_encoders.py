# pyright: reportPrivateUsage=false
# pyright: reportUnusedFunction=false
from hio._internals.exceptions import RegistryError
from hio import encoders

from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum, auto

import pytest


def test_register() -> None:
    class A: ...

    @encoders.register(A)
    def encode_a(a: A) -> str:
        return "a"

    assert encoders._REGISTRY.get(A) is encode_a


def test_register_error() -> None:
    class A: ...

    encoders.register(A)(lambda _: "a")

    with pytest.raises(RegistryError, 
    match="Encoder for type A is already registered"):
        encoders.register(A)(lambda _: "a")


def test_register_subclass_error() -> None:
    class A: ...

    encoders.register(A)(lambda _: "a")

    class B(A): ...

    with pytest.raises(RegistryError, 
    match="Encoder for type A is already registered"):
        encoders.register(B)(lambda _: "b")

    @encoders.register(B, overwrite_parent=True)
    def encode_b(b: B) -> str:
        return "b"

    assert encoders._REGISTRY.get(B) is encode_b


def test_register_dataclass_error() -> None:
    @dataclass
    class A: ...

    with pytest.raises(ValueError, match="Dataclasses handling is built in"):
        encoders.register(A)(lambda _: "a")

    @encoders.register(A, overwrite_parent=True)
    def encode_a(a: A) -> str:
        return "a"

    assert encoders._REGISTRY.get(A) is encode_a


def test_resolve() -> None:
    class A: ...

    def encode_a(a: A) -> str:
        return "a"

    encoders._REGISTRY[A] = encode_a

    assert encoders.resolve(A) is encode_a


def test_resolve_subclass() -> None:
    class A: ...

    class B(A): ...

    @encoders.register(A)
    def encode_a(a: A) -> str:
        return "a"

    assert encoders.resolve(B) is encode_a


def test_resolve_overwrite_subclass() -> None:
    class A: ...

    class B(A): ...

    @encoders.register(A)
    def encode_a(a: A) -> str:
        return "a"

    @encoders.register(B, overwrite_parent=True)
    def encode_b(b: B) -> str:
        return "b"

    assert encoders.resolve(B) is encode_b


def test_resolve_dataclass() -> None:
    @dataclass
    class A: ...

    assert encoders.resolve(A) is encoders.encode_dataclass


def test_resolve_dataclass_overwrite() -> None:
    @dataclass
    class A: ...

    @encoders.register(A, overwrite_parent=True)
    def encode_a(a: A) -> str:
        return "a"

    assert encoders.resolve(A) is encode_a


def test_resolve_error() -> None:
    class A: ...

    with pytest.raises(RegistryError, match="Encoder for type A is not registered"):
        encoders.resolve(A)


def test_encode() -> None:
    class Trophy(Enum):
        CUP = auto()
        FIRST_DEATH = auto()
        PLATINUM = auto()

    @dataclass
    class Graphics:
        render_distance: int = 16
        bloom: bool = True
        bruh: float = 6.7
        options_file: str = "options.ini"

    @dataclass
    class Config:
        save_path: Path = Path("saves")
        trophies: list[Trophy] = field(default_factory=lambda: [Trophy.PLATINUM, Trophy.FIRST_DEATH])
        unlocks: dict[Trophy, str] = field(default_factory=lambda: {
            Trophy.CUP: "base achievement",
            Trophy.PLATINUM: "100%",
            Trophy.FIRST_DEATH: "you died lol",
        })
        graphics: Graphics = field(default_factory=Graphics)


    assert encoders.encode(Config()) == {'save_path': 'saves', 'trophies': ('PLATINUM', 'FIRST_DEATH'), 'unlocks': {'CUP': 'base achievement', 'PLATINUM': '100%', 'FIRST_DEATH': 'you died lol'}, 'graphics': {'render_distance': 16, 'bloom': True, 'bruh': 6.7, 'options_file': 'options.ini'}}