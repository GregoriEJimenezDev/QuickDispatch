"""Pruebas del flujo de pedidos: registro, IDs únicos y despacho FIFO."""
import unittest
from datetime import datetime
from typing import Any

from main import build_app
from models.enums import OrderStatus


class OrderFlowTests(unittest.TestCase):
    """Cubre la opción 1 (registrar) y la opción 2 (despachar)."""

    # O(1): construye una aplicación nueva con sus dependencias.
    def setUp(self) -> None:
        """Crea una app aislada por prueba."""
        self.app = build_app()
        self.orders = self.app.order_service

    # O(n): n = longitud de los textos; registra un pedido válido.
    def test_registro_genera_id_fecha_y_estado(self) -> None:
        """El pedido nace con ID autogenerado, fecha y estado PENDIENTE."""
        result = self.orders.register_order("Ana", "Perez", 3)
        self.assertTrue(result.ok, result.message)
        order = result.data
        self.assertEqual(order.order_id, "Order-0001")
        self.assertEqual(order.estado, OrderStatus.PENDIENTE)
        self.assertIsInstance(order.fecha_hora, datetime)

    # O(n): n = pedidos registrados; acumula cinco IDs y los compara.
    def test_ids_unicos_y_consecutivos(self) -> None:
        """Ningún pedido repite ID."""
        ids = []
        for nombre in ("Uno", "Dos", "Tres", "Cuatro", "Cinco"):
            result = self.orders.register_order(nombre, "Apellido", 1)
            ids.append(result.data.order_id)
        self.assertEqual(ids, [f"Order-{i:04d}" for i in range(1, 6)])
        self.assertEqual(len(set(ids)), 5)

    # O(n): n = pedidos; despacha los cinco y registra dos más.
    def test_ids_no_se_reutilizan_tras_despachar(self) -> None:
        """El histórico no choca con los IDs nuevos."""
        for nombre in ("Uno", "Dos", "Tres", "Cuatro", "Cinco"):
            self.orders.register_order(nombre, "Apellido", 1)
            self.orders.dispatch_order()
        nuevos = [self.orders.register_order("Seis", "Apellido", 1),
                  self.orders.register_order("Siete", "Apellido", 1)]
        self.assertEqual([r.data.order_id for r in nuevos],
                         ["Order-0006", "Order-0007"])
        self.assertEqual(self.orders.dispatched_count(), 5)

    # O(n): n = longitud de los textos; valida cada campo obligatorio.
    def test_campos_obligatorios(self) -> None:
        """Nombre, apellido y cajas son obligatorios."""
        casos = [(("", "Perez", 1), "Nombre es obligatorio."),
                 (("Ana", "", 1), "Apellido es obligatorio.")]
        for args, esperado in casos:
            with self.subTest(args=args):
                result = self.orders.register_order(*args)
                self.assertFalse(result.ok)
                self.assertEqual(result.message, esperado)

    # O(1): prueba cuatro cantidades inválidas contra la misma regla.
    def test_cajas_debe_ser_entero_mayor_que_cero(self) -> None:
        """Cajas acepta solo enteros estrictamente positivos."""
        invalidas: list[Any] = [0, -2, "3", 1.5]
        for cajas in invalidas:
            with self.subTest(cajas=cajas):
                result = self.orders.register_order("Ana", "Perez", cajas)
                self.assertFalse(result.ok)

    # O(1): inserta dos pedidos y mira los extremos de la cola.
    def test_enqueue_mantiene_front_y_rear(self) -> None:
        """La cola apunta al primero y al último registrados."""
        self.orders.register_order("Ana", "Perez", 1)
        self.orders.register_order("Luis", "Garcia", 1)
        cola = self.orders._queue
        front, rear = cola._front, cola._rear
        assert front is not None and rear is not None
        self.assertEqual(front.data.order_id, "Order-0001")
        self.assertEqual(rear.data.order_id, "Order-0002")

    # O(n): n = 2 pedidos; despacha ambos y comprueba el orden.
    def test_despacho_respeta_fifo(self) -> None:
        """Sale primero el pedido más antiguo."""
        self.orders.register_order("Ana", "Perez", 1)
        self.orders.register_order("Luis", "Garcia", 1)
        primero = self.orders.dispatch_order()
        segundo = self.orders.dispatch_order()
        self.assertEqual(primero.data.order_id, "Order-0001")
        self.assertEqual(segundo.data.order_id, "Order-0002")

    # O(1): despacha con la cola vacía y lee el mensaje de error.
    def test_despacho_con_cola_vacia_da_error(self) -> None:
        """La cola vacía responde un error claro."""
        result = self.orders.dispatch_order()
        self.assertFalse(result.ok)
        self.assertEqual(result.message, "No hay pedidos pendientes por despachar.")

    # O(1): despacha un pedido y consulta dict y última referencia.
    def test_despacho_guarda_dict_y_last_dispatched(self) -> None:
        """El dict usa el Order ID como clave y se guarda el último despachado."""
        self.orders.register_order("Ana", "Perez", 2)
        result = self.orders.dispatch_order()
        order = result.data
        self.assertEqual(order.estado, OrderStatus.DESPACHADO)
        self.assertIn("Order-0001", self.orders._dispatched)
        self.assertIs(self.orders.get_dispatched("Order-0001"), order)
        self.assertEqual(self.orders.last_dispatched_order_id, "Order-0001")
        self.assertIs(self.orders.last_dispatched(), order)

    # O(n): n = longitud del resumen; recorre los seis campos mostrados.
    def test_despacho_muestra_los_seis_campos(self) -> None:
        """La salida incluye ID, nombre, apellido, cajas, fecha y estado."""
        self.orders.register_order("Ana", "Perez", 3)
        order = self.orders.dispatch_order().data
        descrito = order.describe()
        for token in (order.order_id, "Ana", "Perez", "Cajas: 3", "Fecha:",
                      "Estado: DESPACHADO"):
            with self.subTest(token=token):
                self.assertIn(token, descrito)

    # O(n): n = pedidos; registra dos, los despacha y revisa la cola.
    def test_cola_vacia_tras_despachar_todo(self) -> None:
        """Al vaciar la cola no quedan referencias colgando."""
        self.orders.register_order("Ana", "Perez", 1)
        self.orders.register_order("Luis", "Garcia", 1)
        self.orders.dispatch_order()
        self.orders.dispatch_order()
        cola = self.orders._queue
        self.assertTrue(self.orders.pending_count() == 0)
        self.assertIsNone(cola._front)
        self.assertIsNone(cola._rear)


if __name__ == "__main__":
    unittest.main()
