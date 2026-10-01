from datetime import datetime

from models.enums import OrderStatus
from models.operation_result import OperationResult
from models.order import Order
from validators.field_validator import FieldValidator


class OrderFactory:
    """Crea pedidos válidos con ID único."""

    # O(1): guarda el validador inyectado e inicia contador y set propios (DIP).
    def __init__(self, validator: FieldValidator | None = None) -> None:
        """Recibe el validador e inicia contador y registro."""
        self.validator = validator or FieldValidator()
        self._counter = 0
        self._issued: set[str] = set()

    # O(1): correlativo de instancia; lo registra en el set para no reutilizarlo jamas.
    def _issue_id(self) -> str:
        self._counter += 1
        new_id = f"Order-{self._counter:04d}"
        self._issued.add(new_id)
        return new_id

    # O(m): valida campos (barrido de letras sobre el texto, m = su longitud) y emite ID O(1).
    def create(self, nombre: str, apellido: str, cajas: int) -> OperationResult:
        """Valida, emite ID y construye el pedido."""
        validation = self.validator.validate_order_fields(nombre, apellido, cajas)
        if not validation.ok:
            return validation
        order = Order(
            order_id=self._issue_id(),
            nombre=nombre,
            apellido=apellido,
            cajas=cajas,
            fecha_hora=datetime.now(),
            estado=OrderStatus.PENDIENTE,
        )
        return OperationResult.success(order, f"Pedido {order.order_id} creado.")
