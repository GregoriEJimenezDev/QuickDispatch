from abc import ABC, abstractmethod
from typing import Any, Optional


class LinkedListBase(ABC):
    """Contrato mínimo común de la cola y la pila."""

    # O(1): contrato abstracto, sin recorrido.
    @abstractmethod
    def is_empty(self) -> bool:
        """Indica si la estructura está vacía."""
        raise NotImplementedError

    # O(1): contrato abstracto, sin recorrido.
    @abstractmethod
    def __len__(self) -> int:
        """Devuelve la cantidad de elementos."""
        raise NotImplementedError

    # O(1): contrato abstracto, sin recorrido.
    @abstractmethod
    def peek(self) -> Optional[Any]:
        """Mira el próximo elemento sin extraerlo."""
        raise NotImplementedError
