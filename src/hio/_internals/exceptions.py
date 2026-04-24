from typing import Mapping

class RegistryError[K, V](KeyError):
    def __init__(self, key: K, reg: Mapping[K, V], message: str) -> None:
        self.key = key
        self.reg = reg
        self.message = message
        super().__init__(message)