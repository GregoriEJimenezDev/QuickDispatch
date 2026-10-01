from collections.abc import Iterable, Iterator
from typing import Optional

from data_structures.queue_linked_list import QueueLinkedList
from models.enums import OrderStatus
from models.operation_result import OperationResult
from models.order import Order
from orders.order_builder import OrderBuilder
from orders.order_factory import OrderFactory


class OrderService:
    """Reglas de negocio de pedidos con cola e histórico."""

    # O(1): guarda referencias inyectadas desde build_app().
    def __init__(self, queue: QueueLinkedList, dispatched: dict,
                 factory: OrderFactory) -> None:
        """Recibe cola, histórico y factory."""
        self._queue = queue
        self._dispatched = dispatched
        self._factory = factory
        self.last_dispatched_order_id: str | None = None

    # O(n): la Factory valida los n caracteres de nombre y apellido; encolar es O(1).
    def register_order(self, nombre: str, apellido: str, cajas: int) -> OperationResult:
        """Registra y encola un pedido."""
        builder = OrderBuilder(self._factory)
        result = builder.with_nombre(nombre).with_apellido(apellido).with_cajas(cajas).build()
        if not result.ok:
            return result
        order: Order = result.data
        self._queue.enqueue(order)
        return OperationResult.success(order, f"Pedido {order.order_id} registrado en cola.")

    # O(1): dequeue + guardado en dict nativo, sin recorridos.
    def dispatch_order(self) -> OperationResult:
        """Despacha el primer pedido de la cola."""
        order: Optional[Order] = self._queue.dequeue()
        if order is None:
            return OperationResult.failure("No hay pedidos pendientes por despachar.")
        order.estado = OrderStatus.DESPACHADO
        self._dispatched[order.order_id] = order
        self.last_dispatched_order_id = order.order_id
        return OperationResult.success(order, f"Pedido {order.order_id} despachado.")

    # O(1): lectura del frente sin recorrer.
    def peek_next(self) -> Order | None:
        """Muestra el próximo a despachar."""
        return self._queue.peek()

    # O(1): tamanos via contador y len() del dict.
    def pending_count(self) -> int:
        """Cuenta los pedidos pendientes."""
        return len(self._queue)

    # O(1): tamanos via len() del dict.
    def dispatched_count(self) -> int:
        """Cuenta los pedidos despachados."""
        return len(self._dispatched)

    # O(1): acceso directo por clave al ultimo despachado.
    def last_dispatched(self) -> Order | None:
        """Devuelve el último pedido despachado."""
        if self.last_dispatched_order_id is None:
            return None
        return self._dispatched.get(self.last_dispatched_order_id)

    # O(n): generador nodo a nodo de los pendientes (delega en la Queue, sin nativas).
    def traverse_pending(self) -> Iterator[Order]:
        """Recorre los pendientes en orden FIFO."""
        for order in self._queue.traverse_forward():
            yield order

    # O(1): retorna la vista de valores del historico (iterarla cuesta O(n) al llamador).
    def dispatched_orders(self) -> Iterable[Order]:
        """Devuelve los pedidos despachados."""
        return self._dispatched.values()

    # O(1): lookup exacto de un pedido despachado por su Order ID.
    def get_dispatched(self, order_id: str) -> Order | None:
        """Busca un despachado por su Order ID."""
        return self._dispatched.get(order_id)
