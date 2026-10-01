"""Pruebas del flujo de incidencias: validaciones, pila LIFO y cierre."""
import unittest
from datetime import datetime

from main import build_app
from models.enums import IncidentStatus, IncidentType, OrderStatus

DEVOLUCION = IncidentType.DEVOLUCION.value
CANCELACION = IncidentType.CANCELACION.value


class IncidentFlowTests(unittest.TestCase):
    """Cubre la opción 3 (registrar) y la opción 4 (procesar)."""

    # O(1): construye una aplicación nueva con sus dependencias.
    def setUp(self) -> None:
        """Crea una app aislada con un pedido despachado por prueba."""
        self.app = build_app()
        self.orders = self.app.order_service
        self.incidents = self.app.incident_service

    # O(1): registra y despacha un pedido para las pruebas de incidencias.
    def despachar_uno(self, nombre: str = "Ana") -> None:
        """Deja un pedido DESPACHADO listo para incidir."""
        self.orders.register_order(nombre, "Perez", 2)
        self.orders.dispatch_order()

    # O(1): busca el pedido despachado y devuelve su estado.
    def estado_de(self, order_id: str) -> OrderStatus:
        """Devuelve el estado de un pedido del histórico."""
        order = self.orders.get_dispatched(order_id)
        assert order is not None, order_id
        return order.estado

    # O(n): n = longitud de los textos; comprueba los tres campos obligatorios.
    def test_campos_obligatorios(self) -> None:
        """Tipo, Order ID y motivo son obligatorios."""
        self.despachar_uno()
        casos = [("", "Order-0001", "motivo", "Tipo es obligatorio."),
                 (DEVOLUCION, "", "motivo", "Order ID es obligatorio."),
                 (DEVOLUCION, "Order-0001", "", "Motivo es obligatorio.")]
        for tipo, order_id, motivo, esperado in casos:
            with self.subTest(esperado=esperado):
                result = self.incidents.register_incident(tipo, order_id, motivo)
                self.assertFalse(result.ok)
                self.assertEqual(result.message, esperado)
        self.assertEqual(self.incidents.pending_count(), 0)

    # O(n): n = pedidos en cola; intenta incidir sobre uno pendiente.
    def test_no_admite_pedidos_pendientes(self) -> None:
        """Solo se puede incidir sobre pedidos DESPACHADOS."""
        self.orders.register_order("Ana", "Perez", 1)
        result = self.incidents.register_incident(DEVOLUCION, "1", "motivo")
        self.assertFalse(result.ok)
        self.assertIn("no está DESPACHADO", result.message)
        self.assertIn("PENDIENTE", result.message)

    # O(1): registra una incidencia y mira la cima de la pila.
    def test_incidencia_aceptada_push_top_y_fecha(self) -> None:
        """La incidencia nace PENDIENTE, con fecha, y ocupa la cima."""
        self.despachar_uno()
        result = self.incidents.register_incident(DEVOLUCION, "1", "motivo")
        self.assertTrue(result.ok, result.message)
        incident = result.data
        self.assertEqual(incident.incident_id, "Incident-0001")
        self.assertEqual(incident.estado, IncidentStatus.PENDIENTE)
        self.assertIsInstance(incident.fecha_hora, datetime)
        top = self.incidents._stack._top
        assert top is not None
        self.assertIs(top.data, incident)

    # O(1): registra una devolución y lee el estado del pedido.
    def test_devolucion_pasa_el_pedido_a_devuelto(self) -> None:
        """El pedido despachado pasa a DEVUELTO."""
        self.despachar_uno()
        self.incidents.register_incident(DEVOLUCION, "1", "motivo")
        self.assertEqual(self.estado_de("Order-0001"), OrderStatus.DEVUELTO)

    # O(1): registra una cancelación y lee el estado del pedido.
    def test_cancelacion_pasa_el_pedido_a_cancelado(self) -> None:
        """El pedido despachado pasa a CANCELADO."""
        self.despachar_uno()
        self.incidents.register_incident(CANCELACION, "1", "motivo")
        self.assertEqual(self.estado_de("Order-0001"), OrderStatus.CANCELADO)

    # O(n): n = incidencias de la pila; busca una pendiente del mismo pedido.
    def test_no_permite_dos_incidencias_pendientes(self) -> None:
        """Mientras exista una pendiente, no entra otra del mismo pedido."""
        self.despachar_uno()
        self.incidents.register_incident(DEVOLUCION, "1", "motivo")
        repetida = self.incidents.register_incident(CANCELACION, "1", "otro")
        self.assertFalse(repetida.ok)
        self.assertEqual(self.incidents.pending_count(), 1)

    # O(1): procesa la cima y comprueba el cierre del pedido.
    def test_procesar_deja_el_pedido_cerrado(self) -> None:
        """Procesar la incidencia cierra el pedido asociado."""
        self.despachar_uno()
        self.incidents.register_incident(DEVOLUCION, "1", "motivo")
        result = self.incidents.process_incident()
        self.assertTrue(result.ok, result.message)
        self.assertEqual(self.estado_de("Order-0001"), OrderStatus.CERRADO)
        self.assertEqual(self.incidents.pending_count(), 0)
        self.assertEqual(self.incidents.processed_count(), 1)

    # O(1): intenta incidir sobre un pedido ya cerrado.
    def test_no_admite_pedidos_cerrados(self) -> None:
        """Los pedidos CERRADOS no admiten nuevas incidencias."""
        self.despachar_uno()
        self.incidents.register_incident(DEVOLUCION, "1", "motivo")
        self.incidents.process_incident()
        result = self.incidents.register_incident(CANCELACION, "0001", "otro")
        self.assertFalse(result.ok)
        self.assertIn("CERRADO", result.message)
        self.assertNotIn("no existe", result.message)

    # O(n): n = 3 incidencias; apila tres y las procesa en orden inverso.
    def test_lifo_con_tres_incidencias(self) -> None:
        """La última apilada es la primera que se procesa."""
        for numero, nombre in enumerate(("Ana", "Luis", "Marta"), start=1):
            self.orders.register_order(nombre, "Perez", 1)
            self.orders.dispatch_order()
            self.incidents.register_incident(DEVOLUCION, str(numero), f"m{numero}")
        procesadas = [self.incidents.process_incident().data.order_id,
                      self.incidents.process_incident().data.order_id,
                      self.incidents.process_incident().data.order_id]
        self.assertEqual(procesadas, ["Order-0003", "Order-0002", "Order-0001"])
        for order_id in ("Order-0001", "Order-0002", "Order-0003"):
            with self.subTest(order_id=order_id):
                self.assertEqual(self.estado_de(order_id), OrderStatus.CERRADO)

    # O(n): n = incidencias; procesa dos y emite una cuarta sin reutilizar IDs.
    def test_incident_id_no_reutiliza_ni_pendientes_ni_procesadas(self) -> None:
        """El contador sigue avanzando tras procesar."""
        for numero, nombre in enumerate(("Ana", "Luis", "Marta"), start=1):
            self.orders.register_order(nombre, "Perez", 1)
            self.orders.dispatch_order()
            self.incidents.register_incident(DEVOLUCION, str(numero), f"m{numero}")
        self.incidents.process_incident()
        self.incidents.process_incident()
        self.orders.register_order("Nuria", "Perez", 1)
        self.orders.dispatch_order()
        result = self.incidents.register_incident(CANCELACION, "4", "nueva")
        self.assertTrue(result.ok, result.message)
        self.assertEqual(result.data.incident_id, "Incident-0004")

    # O(1): procesa con la pila vacía y lee el mensaje de error.
    def test_procesar_con_pila_vacia_da_error(self) -> None:
        """La pila vacía responde un error claro."""
        result = self.incidents.process_incident()
        self.assertFalse(result.ok)
        self.assertEqual(result.message, "No hay incidencias pendientes por procesar.")


if __name__ == "__main__":
    unittest.main()
