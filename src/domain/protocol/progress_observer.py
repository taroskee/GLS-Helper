from typing import Protocol, runtime_checkable


@runtime_checkable
class ProgressObserver(Protocol):
    def update(self, increment: int) -> None:
        """report progress"""
        ...

    def set_description(self, description: str) -> None:
        """report current process"""
        ...
