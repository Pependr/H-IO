from hio.datatools import BaseModel

from dataclasses import dataclass, field


def test_model() -> None:
    class UserModel(BaseModel):
        id: int
        name: str
        badges: list[str]
        is_admin: bool = False
        is_bozo: bool | None

    
    class User:
        def __init__(self, id: int, name: str, is_admin: bool = False) -> None:
            self.id: int = id
            self.name: str = name
            self.badges: list[str] = []
            self.is_admin: bool = is_admin


    assert UserModel.describes_object(User(0, "Mark"))


def test_model_dataclass() -> None:
    class UserModel(BaseModel):
        id: int
        name: str
        badges: list[str]
        is_admin: bool = False
        is_bozo: bool | None

    
    @dataclass
    class User:
        id: int
        name: str
        badges: list[str] = field(default_factory=list[str])
        is_admin: bool = False
    

    assert UserModel.describes_object(User(0, "Mark"))