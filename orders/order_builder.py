from models.operation_result import OperationResult
from orders.order_factory import OrderFactory


class OrderBuilder:
    """Arma pedidos paso a paso con métodos encadenables."""

    # O(1): guarda referencia a la factory inyectada (DIP).
    def __init__(self, factory: OrderFactory) -> None:
        """Recibe la factory que usará build."""
        self._factory = factory
        self._nombre = ""
        self._apellido = ""
        self._cajas = 0

    # O(n): recorta los n caracteres del nombre y los guarda.
    def with_nombre(self, nombre: str) -> "OrderBuilder":
        """Normaliza y guarda el nombre."""
        self._nombre = nombre.strip() if isinstance(nombre, str) else nombre
        return self

    # O(n): recorta los n caracteres del apellido y los guarda.
    def with_apellido(self, apellido: str) -> "OrderBuilder":
        """Normaliza y guarda el apellido."""
        self._apellido = apellido.strip() if isinstance(apellido, str) else apellido
        return self

    # O(1): guarda la cantidad tal cual (la valida la Factory).
    def with_cajas(self, cajas: int) -> "OrderBuilder":
        """Guarda la cantidad de cajas."""
        self._cajas = cajas
        return self

    # O(n): la Factory recorre los n caracteres de nombre y apellido al validar.
    def build(self) -> OperationResult:
        """Crea el pedido mediante la Factory."""
        return self._factory.create(self._nombre, self._apellido, self._cajas)
