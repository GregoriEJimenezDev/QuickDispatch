from enum import Enum


class OrderStatus(str, Enum):
    """Estados posibles de un pedido."""

    PENDIENTE = "PENDIENTE"
    DESPACHADO = "DESPACHADO"
    DEVUELTO = "DEVUELTO"
    CANCELADO = "CANCELADO"
    CERRADO = "CERRADO"

    # O(1): devuelve el valor para f-strings y comparaciones con texto.
    def __str__(self) -> str:
        """Devuelve el texto del estado."""
        return self.value


class IncidentStatus(str, Enum):
    """Estados posibles de una incidencia."""

    PENDIENTE = "PENDIENTE"
    PROCESADA = "PROCESADA"

    # O(1): devuelve el valor para f-strings y comparaciones con texto.
    def __str__(self) -> str:
        """Devuelve el texto del estado."""
        return self.value


class IncidentType(str, Enum):
    """Tipos posibles de incidencia."""

    DEVOLUCION = "DEVOLUCIÓN"
    CANCELACION = "CANCELACIÓN"

    # O(1): devuelve el valor para f-strings y comparaciones con texto.
    def __str__(self) -> str:
        """Devuelve el texto del tipo."""
        return self.value
