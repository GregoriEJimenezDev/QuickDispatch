from incidents.incident_factory import IncidentFactory
from models.enums import IncidentType
from models.operation_result import OperationResult


TYPE_ALIASES = {
    "DEVOLUCION": IncidentType.DEVOLUCION.value,
    "CANCELACION": IncidentType.CANCELACION.value,
}


class IncidentBuilder:
    """Arma incidencias paso a paso con métodos encadenables."""

    # O(1): guarda referencia a la factory inyectada (DIP).
    def __init__(self, factory: IncidentFactory) -> None:
        """Recibe la factory que usará build."""
        self._factory = factory
        self._tipo = ""
        self._order_id = ""
        self._motivo = ""

    # O(m): normaliza el tipo (recorte, mayusculas y alias sin tilde).
    def with_tipo(self, tipo: str) -> "IncidentBuilder":
        """Normaliza y guarda el tipo."""
        text = tipo.strip().upper() if isinstance(tipo, str) else tipo
        self._tipo = TYPE_ALIASES.get(text, text) if isinstance(text, str) else text
        return self

    # O(m): guarda el Order ID recortado (la clave canonica la resuelve el service).
    def with_order_id(self, order_id: str) -> "IncidentBuilder":
        """Normaliza y guarda el Order ID."""
        self._order_id = order_id.strip() if isinstance(order_id, str) else order_id
        return self

    # O(m): guarda el motivo recortado (m = longitud del texto).
    def with_motivo(self, motivo: str) -> "IncidentBuilder":
        """Normaliza y guarda el motivo."""
        self._motivo = motivo.strip() if isinstance(motivo, str) else motivo
        return self

    # O(m): delega en la Factory (hereda su costo sobre el texto, m = su longitud).
    def build(self) -> OperationResult:
        """Crea la incidencia mediante la Factory."""
        return self._factory.create(self._tipo, self._order_id, self._motivo)
