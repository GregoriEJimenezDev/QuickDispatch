from types import MappingProxyType
from typing import Mapping

from incidents.incident_factory import IncidentFactory
from models.enums import IncidentType
from models.operation_result import OperationResult


class IncidentBuilder:
    """Arma incidencias paso a paso con métodos encadenables."""

    # O(1): alias sin tilde -> texto oficial, en vista de solo lectura.
    TYPE_ALIASES: Mapping[str, str] = MappingProxyType({
        "DEVOLUCION": IncidentType.DEVOLUCION.value,
        "CANCELACION": IncidentType.CANCELACION.value,
    })

    # O(1): guarda referencia a la factory inyectada (DIP).
    def __init__(self, factory: IncidentFactory) -> None:
        """Recibe la factory que usará build."""
        self._factory = factory
        self._tipo = ""
        self._order_id = ""
        self._motivo = ""

    # O(n): recorta y pasa a mayúsculas los n caracteres del tipo (alias O(1)).
    def with_tipo(self, tipo: str) -> "IncidentBuilder":
        """Normaliza y guarda el tipo."""
        text = tipo.strip().upper() if isinstance(tipo, str) else tipo
        self._tipo = (IncidentBuilder.TYPE_ALIASES.get(text, text)
                      if isinstance(text, str) else text)
        return self

    # O(n): recorta los n caracteres del Order ID (la clave la resuelve el service).
    def with_order_id(self, order_id: str) -> "IncidentBuilder":
        """Normaliza y guarda el Order ID."""
        self._order_id = order_id.strip() if isinstance(order_id, str) else order_id
        return self

    # O(n): recorta los n caracteres del motivo y los guarda.
    def with_motivo(self, motivo: str) -> "IncidentBuilder":
        """Normaliza y guarda el motivo."""
        self._motivo = motivo.strip() if isinstance(motivo, str) else motivo
        return self

    # O(n): la Factory recorre los n caracteres de tipo, Order ID y motivo.
    def build(self) -> OperationResult:
        """Crea la incidencia mediante la Factory."""
        return self._factory.create(self._tipo, self._order_id, self._motivo)
