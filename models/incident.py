from datetime import datetime

from models.enums import IncidentStatus, IncidentType
from models.order import format_datetime


class Incident:
    """Incidencia con tipo, pedido, motivo, fecha y estado."""

    # O(1): asignacion de atributos escalares.
    def __init__(self, incident_id: str, tipo: IncidentType, order_id: str,
                 motivo: str, fecha_hora: datetime,
                 estado: IncidentStatus = IncidentStatus.PENDIENTE) -> None:
        """Crea la incidencia con sus datos y estado."""
        self.incident_id = incident_id
        self.tipo = tipo
        self.order_id = order_id
        self.motivo = motivo
        self.fecha_hora = fecha_hora
        self.estado = estado

    # O(1): construye una cadena con atributos escalares.
    def describe(self) -> str:
        """Resume la incidencia en una línea."""
        return (
            f"[{self.incident_id}] Tipo: {self.tipo} | Pedido: {self.order_id} | "
            f"Estado: {self.estado} | Motivo: {self.motivo} | "
            f"Fecha: {format_datetime(self.fecha_hora)}"
        )
