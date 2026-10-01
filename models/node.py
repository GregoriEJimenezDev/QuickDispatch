from typing import Any, Optional


class Node:
    """Nodo de lista enlazada con dato y siguiente."""

    # O(1): asignaciones simples de referencias.
    def __init__(self, data: Any) -> None:
        """Guarda el dato y deja siguiente en None."""
        self.data: Any = data
        self.next: Optional["Node"] = None
