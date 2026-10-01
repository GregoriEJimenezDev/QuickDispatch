import re
from collections.abc import Iterable, Iterator

from data_structures.stack_linked_list import StackLinkedList
from incidents.incident_builder import IncidentBuilder
from incidents.incident_factory import IncidentFactory
from models.enums import IncidentStatus, IncidentType, OrderStatus
from models.incident import Incident
from models.operation_result import OperationResult


_ORDER_ID_RE = re.compile(r"^(?:ORDER-)?(\d+)$", re.IGNORECASE)


class IncidentService:
    """Reglas de negocio de incidencias con pila e histórico."""

    # O(1): guarda referencias inyectadas desde build_app().
    def __init__(self, stack: StackLinkedList, dispatched: dict,
                 processed: dict, factory: IncidentFactory) -> None:
        """Recibe pila, históricos y factory."""
        self._stack = stack
        self._dispatched = dispatched
        self._processed = processed
        self._factory = factory
        self.last_processed_incident_id = None

    # O(n): un solo recorrido de la pila para detectar duplicado pendiente (sin nativas).
    def _has_pending_for_order(self, order_id: str) -> bool:
        for incident in self._stack.traverse_from_top():
            if incident.order_id == order_id:
                return True
        return False

    # O(m): normaliza ("1"/"0001"/"Order-0001" -> "Order-0001"; None si formato invalido).
    def _normalize_order_input(self, order_id: str) -> str | None:
        if not isinstance(order_id, str):
            return None
        match = _ORDER_ID_RE.match(order_id.strip())
        if match is None:
            return None
        try:
            return f"Order-{int(match.group(1)):04d}"
        except ValueError:
            return None

    # O(n): clave canonica del pedido (exacta O(1); barrido O(n) si varia mayusculas).
    def _resolve_order_key(self, order_id: str) -> str | None:
        cleaned = self._normalize_order_input(order_id)
        if isinstance(cleaned, str) and cleaned in self._dispatched:
            return cleaned
        if isinstance(cleaned, str):
            upper = cleaned.upper()
            for key in self._dispatched:
                if key.upper() == upper:
                    return key
        return cleaned

    # O(n): pre-chequeos ANTES de consumir ID (evita huecos); la Factory valida y consume.
    def register_incident(self, tipo: str, order_id: str, motivo: str) -> OperationResult:
        """Registra una incidencia en la pila."""
        key = self._resolve_order_key(order_id)
        order = self._dispatched.get(key) if key is not None else None
        if order is None:
            shown = order_id.strip() if isinstance(order_id, str) else order_id
            return OperationResult.failure(
                f"Order ID {shown} no existe en despachados."
            )
        if order.is_closed():
            return OperationResult.failure(
                f"Pedido {order.order_id} está CERRADO; no admite incidencias."
            )
        if self._has_pending_for_order(order.order_id):
            return OperationResult.failure(
                f"Ya existe una incidencia pendiente para {order.order_id}."
            )
        builder = IncidentBuilder(self._factory)
        result = (builder.with_tipo(tipo).with_order_id(order.order_id)
                  .with_motivo(motivo).build())
        if not result.ok:
            return result
        incident: Incident = result.data
        self._stack.push(incident)
        estado_por_tipo = {IncidentType.DEVOLUCION: OrderStatus.DEVUELTO,
                           IncidentType.CANCELACION: OrderStatus.CANCELADO}
        order.estado = estado_por_tipo[incident.tipo]
        return OperationResult.success(
            incident, f"Incidencia {incident.incident_id} registrada en pila."
        )

    # O(1): pop + guardado en dict nativo, sin recorridos.
    def process_incident(self) -> OperationResult:
        """Procesa la cima de la pila y cierra el pedido."""
        if self._stack.is_empty():
            return OperationResult.failure("No hay incidencias pendientes por procesar.")
        incident: Incident = self._stack.pop()
        incident.estado = IncidentStatus.PROCESADA
        order = self._dispatched.get(incident.order_id)
        if order is not None:
            order.estado = OrderStatus.CERRADO
        self._processed[incident.incident_id] = incident
        self.last_processed_incident_id = incident.incident_id
        return OperationResult.success(incident, f"Incidencia {incident.incident_id} procesada.")

    # O(1): lectura de la cima sin recorrer.
    def peek_next(self) -> Incident | None:
        """Muestra la próxima a tratar."""
        return self._stack.peek()

    # O(1): tamanos via contador y len() del dict.
    def pending_count(self) -> int:
        """Cuenta las incidencias pendientes."""
        return len(self._stack)

    # O(1): tamanos via len() del dict.
    def processed_count(self) -> int:
        """Cuenta las incidencias procesadas."""
        return len(self._processed)

    # O(1): acceso directo por clave a la ultima procesada.
    def last_processed(self) -> Incident | None:
        """Devuelve la última procesada."""
        if self.last_processed_incident_id is None:
            return None
        return self._processed.get(self.last_processed_incident_id)

    # O(n): generador LIFO de las pendientes (delega en la Stack, sin nativas).
    def traverse_pending(self) -> Iterator[Incident]:
        """Recorre las pendientes en orden LIFO."""
        for incident in self._stack.traverse_from_top():
            yield incident

    # O(1): retorna la vista de valores del historico (iterarla cuesta O(n) al llamador).
    def processed_incidents(self) -> Iterable[Incident]:
        """Devuelve las incidencias procesadas."""
        return self._processed.values()
