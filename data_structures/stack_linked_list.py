from collections.abc import Iterator
from typing import Any, Optional

from data_structures.linked_list_base import LinkedListBase
from models.node import Node


class StackLinkedList(LinkedListBase):
    """Pila LIFO sobre lista enlazada simple para las incidencias.

    LIFO es la estructura adecuada para procesar incidencias porque atiende
    primero lo más reciente: el último reclamo es el más urgente, por eso el
    último en entrar es el primero en salir. Con una sola referencia,
    ``top`` (cima), ``push`` y ``pop`` cuestan O(1) sobre la lista enlazada
    simple: se enlaza o se desenlaza el primer nodo sin reasignar memoria
    ni recorrer la estructura.
    """

    # O(1): inicializa una referencia y un contador.
    def __init__(self) -> None:
        """Inicia cima y contador en vacío."""
        self._top: Optional[Node] = None
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
        top = self._top
        if self.is_empty() or top is None:
            return None
        data = top.data
        self._top = top.next
        self._size -= 1
        return data

    # O(1): lectura de la cima sin extraer.
    def peek(self) -> Optional[Any]:
        """Mira la cima sin sacarla."""
        top = self._top
        if self.is_empty() or top is None:
            return None
        return top.data

    # O(n): recorre nodo a nodo desde top, sin copiar a lista nativa.
    def traverse_from_top(self) -> Iterator[Any]:
        """Recorre de la cima a la base."""
        current = self._top
        while current is not None:
            yield current.data
            current = current.next
