from datetime import datetime

from models.enums import OrderStatus


# O(1): formateo de un objeto datetime.
def format_datetime(dt: datetime) -> str:
    """Da formato de fecha y hora como texto."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class Order:
    """Pedido con cliente, cajas, fecha y estado."""

    # O(1): asignacion de atributos escalares.
    def __init__(self, order_id: str, nombre: str, apellido: str,
                 cajas: int, fecha_hora: datetime,
                 estado: OrderStatus = OrderStatus.PENDIENTE) -> None:
        """Crea el pedido con sus datos y estado."""
        self.order_id = order_id
        self.nombre = nombre
        self.apellido = apellido
        self.cajas = cajas
        self.fecha_hora = fecha_hora
        self.estado = estado

    # O(n): n = longitud de nombre y apellido; concatena sus n caracteres en una línea.
    def describe(self) -> str:
        """Resume el pedido en una línea."""
        return (
            f"[{self.order_id}] {self.nombre} {self.apellido} | "
            f"Cajas: {self.cajas} | Estado: {self.estado} | "
            f"Fecha: {format_datetime(self.fecha_hora)}"
        )

    # O(1): comparacion escalar.
    def is_closed(self) -> bool:
        """Indica si el pedido está cerrado."""
        return self.estado == OrderStatus.CERRADO
