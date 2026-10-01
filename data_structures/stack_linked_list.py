from collections.abc import Iterator
from typing import Any, Optional

from data_structures.linked_list_base import LinkedListBase
from models.node import Node


class StackLinkedList(LinkedListBase):
    """Pila LIFO con cima."""

    # O(1): inicializa una referencia y un contador.
    def __init__(self) -> None:
        """Inicia cima y contador en vacío."""
        self._top = None
        self._size = 0

    # O(1): compara contador con cero.
    def is_empty(self) -> bool:
        """Indica si la pila está vacía."""
        return self._size == 0

    # O(1): retorna contador mantenido incrementalmente.
    def __len__(self) -> int:
        """Devuelve la cantidad en pila."""
        return self._size

    # O(1): inserta en la cima actualizando top.
    def push(self, data: Any) -> None:
        """Agrega un dato en la cima."""
        node = Node(data)
        node.next = self._top
        self._top = node
        self._size += 1

    # O(1): extrae de la cima actualizando top.
    def pop(self) -> Optional[Any]:
        """Saca y devuelve el dato de la cima."""
        if self.is_empty():
            return None
        data = self._top.data
        self._top = self._top.next
        self._size -= 1
        return data

    # O(1): lectura de la cima sin extraer.
    def peek(self) -> Optional[Any]:
        """Mira la cima sin sacarla."""
        if self.is_empty():
            return None
        return self._top.data

    # O(n): recorre nodo a nodo desde top, sin copiar a lista nativa.
    def traverse_from_top(self) -> Iterator[Any]:
        """Recorre de la cima a la base."""
        current = self._top
        while current is not None:
            yield current.data
            current = current.next
