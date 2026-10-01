from collections.abc import Iterator
from typing import Any, Optional

from data_structures.linked_list_base import LinkedListBase
from models.node import Node


class QueueLinkedList(LinkedListBase):
    """Cola FIFO con frente y final."""

    # O(1): inicializa dos referencias y un contador.
    def __init__(self) -> None:
        """Inicia frente, final y contador en vacío."""
        self._front: Optional[Node] = None
        self._rear: Optional[Node] = None
        self._size = 0

    # O(1): compara contador con cero.
    def is_empty(self) -> bool:
        """Indica si la cola está vacía."""
        return self._size == 0

    # O(1): retorna contador mantenido incrementalmente.
    def __len__(self) -> int:
        """Devuelve la cantidad en cola."""
        return self._size

    # O(1): inserta al final actualizando rear (y front si estaba vacia).
    def enqueue(self, data: Any) -> None:
        """Agrega un dato al final."""
        node = Node(data)
        rear = self._rear
        if self.is_empty() or rear is None:
            self._front = node
            self._rear = node
        else:
            rear.next = node
            self._rear = node
        self._size += 1

    # O(1): extrae del frente; si queda vacia, rear vuelve a None.
    def dequeue(self) -> Optional[Any]:
        """Saca y devuelve el dato del frente."""
        front = self._front
        if self.is_empty() or front is None:
            return None
        data = front.data
        self._front = front.next
        self._size -= 1
        if self._front is None:
            self._rear = None
        return data

    # O(1): lectura del frente sin extraer.
    def peek(self) -> Optional[Any]:
        """Mira el frente sin sacarlo."""
        front = self._front
        if self.is_empty() or front is None:
            return None
        return front.data

    # O(n): recorre nodo a nodo desde front, sin copiar a lista nativa.
    def traverse_forward(self) -> Iterator[Any]:
        """Recorre del frente al final."""
        current = self._front
        while current is not None:
            yield current.data
            current = current.next
