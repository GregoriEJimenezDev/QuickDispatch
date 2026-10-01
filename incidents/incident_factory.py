from datetime import datetime

from models.enums import IncidentStatus, IncidentType
from models.incident import Incident
from models.operation_result import OperationResult
from validators.field_validator import FieldValidator


class IncidentFactory:
    """Crea incidencias válidas con ID único."""

    # O(1): guarda el validador inyectado e inicia contador y set propios (DIP).
    def __init__(self, validator: FieldValidator | None = None) -> None:
        """Recibe el validador e inicia contador y registro."""
        self.validator = validator or FieldValidator()
        self._counter = 0
        self._issued: set[str] = set()

    # O(1): correlativo de instancia; lo registra en el set para no reutilizarlo jamas.
    def _issue_id(self) -> str:
        self._counter += 1
        new_id = f"Incident-{self._counter:04d}"
        self._issued.add(new_id)
        return new_id

    # O(m): valida campos (barrido de letras sobre el texto, m = su longitud) y emite ID O(1).
    def create(self, tipo: str, order_id: str, motivo: str) -> OperationResult:
        """Valida, emite ID y construye la incidencia."""
        validation = self.validator.validate_incident_fields(
            tipo, order_id, motivo, tuple(t.value for t in IncidentType)
        )
        if not validation.ok:
            return validation
        incident = Incident(
            incident_id=self._issue_id(),
            tipo=IncidentType(tipo),
            order_id=order_id,
            motivo=motivo,
            fecha_hora=datetime.now(),
            estado=IncidentStatus.PENDIENTE,
        )
        return OperationResult.success(incident, f"Incidencia {incident.incident_id} creada.")
