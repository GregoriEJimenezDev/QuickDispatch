from incidents.incident_service import IncidentService
from models.enums import IncidentType
from orders.order_service import OrderService
from ui.console_utils import centered, read_letters, read_positive_int, read_text
from ui.console_utils import section, show, show_block, title


class MainMenu:
    """Menú principal que orquesta los servicios."""

    # O(1): guarda referencias inyectadas desde build_app().
    def __init__(self, order_service: OrderService, incident_service: IncidentService) -> None:
        """Recibe los servicios de pedidos e incidencias."""
        self.order_service = order_service
        self.incident_service = incident_service
        self._running = True

    # O(n): imprime el menu como bloque centrado (n = 6 opciones fijas).
    def display(self) -> None:
        """Muestra las seis opciones del menú."""
        title("QuickDispatch - Menu Principal")
        show_block([
            "1. Registrar pedido",
            "2. Despachar pedido",
            "3. Registrar devolución/cancelación",
            "4. Procesar devolución/cancelación",
            "5. Ver estado (reporte completo)",
            "6. Salir",
        ], align="block")
        show("")

    # O(m): captura 3 campos y delega al OrderService (m = longitud del texto).
    def option_register_order(self) -> None:
        """Pide datos y registra el pedido."""
        section("Registrar pedido")
        nombre = read_letters("Nombre:")
        apellido = read_letters("Apellido:")
        cajas = read_positive_int("Cantidad de cajas (> 0):")
        result = self.order_service.register_order(nombre, apellido, cajas)
        if result.ok:
            show_block([f"[OK] {result.message}", result.data.describe()])
        else:
            show(centered(f"[ERROR] {result.message}"))

    # O(1): despacha un pedido (dequeue + dict), sin recorridos.
    def option_dispatch_order(self) -> None:
        """Despacha el primer pedido de la cola."""
        section("Despachar pedido")
        result = self.order_service.dispatch_order()
        if result.ok:
            show_block([
                f"[OK] {result.message}",
                "Detalle del pedido despachado:",
                result.data.describe(),
            ])
        else:
            show(centered(f"[ERROR] {result.message}"))

    # O(t): pide el tipo como opcion a/b hasta recibir una valida (t = intentos).
    def _ask_tipo(self) -> IncidentType:
        """Pide el tipo como letra a o b."""
        opciones = {"a": IncidentType.DEVOLUCION, "b": IncidentType.CANCELACION}
        show_block(["a) DEVOLUCIÓN", "b) CANCELACIÓN"])
        while True:
            choice = read_text("Elija (a/b):").strip().lower()
            if choice in opciones:
                return opciones[choice]
            show(centered("[ERROR] Elija a o b."))

    # O(n): registra incidencia; el costo O(n) viene del anti-duplicado en la pila.
    def option_register_incident(self) -> None:
        """Registra una incidencia con tipo a/b."""
        section("Registrar devolución/cancelación")
        tipo = self._ask_tipo()
        order_id = read_text("Order ID (ej. Order-0001 o 1):")
        motivo = read_text("Motivo:")
        result = self.incident_service.register_incident(tipo, order_id, motivo)
        if result.ok:
            show_block([f"[OK] {result.message}", result.data.describe()])
        else:
            show(centered(f"[ERROR] {result.message}"))

    # O(1): procesa una incidencia (pop + dict), sin recorridos.
    def option_process_incident(self) -> None:
        """Procesa la cima de la pila."""
        section("Procesar devolución/cancelación")
        result = self.incident_service.process_incident()
        if result.ok:
            incident = result.data
            order = self.order_service.get_dispatched(incident.order_id)
            lines = [f"[OK] {result.message}", incident.describe()]
            if order is not None:
                lines.append("Detalle del pedido cerrado:")
                lines.append(order.describe())
            show_block(lines)
        else:
            show(centered(f"[ERROR] {result.message}"))

    # O(n): cuatro recorridos SECUENCIALES (no anidados); cada uno O(n), total O(n).
    def option_show_status(self) -> None:
        """Muestra el reporte completo de estado."""
        title("Reporte de estado")
        section("A) Cola de pedidos pendientes (FIFO)")
        show(centered(f"Cantidad: {self.order_service.pending_count()}"))
        if self.order_service.pending_count() == 0:
            show(centered("No hay pedidos pendientes."))
        else:
            rows = [order.describe() for order in self.order_service.traverse_pending()]
            next_order = self.order_service.peek_next()
            rows.append("Próximo a despachar:")
            rows.append("  " + next_order.describe() if next_order else "  N/A")
            show_block(rows)
        section("B) Pedidos despachados (histórico)")
        show(centered(f"Cantidad: {self.order_service.dispatched_count()}"))
        if self.order_service.dispatched_count() == 0:
            show(centered("Aún no hay pedidos despachados."))
        else:
            rows = [o.describe() for o in self.order_service.dispatched_orders()]
            last_order = self.order_service.last_dispatched()
            rows.append("Último despachado:")
            rows.append("  " + last_order.describe() if last_order else "  N/A")
            show_block(rows)
        section("C) Pila de incidencias pendientes (LIFO)")
        show(centered(f"Cantidad: {self.incident_service.pending_count()}"))
        if self.incident_service.pending_count() == 0:
            show(centered("No hay incidencias pendientes."))
        else:
            rows = [i.describe() for i in self.incident_service.traverse_pending()]
            next_incident = self.incident_service.peek_next()
            rows.append("Próxima a tratar:")
            rows.append("  " + next_incident.describe() if next_incident else "  N/A")
            show_block(rows)
        section("D) Incidencias procesadas (histórico)")
        show(centered(f"Cantidad: {self.incident_service.processed_count()}"))
        if self.incident_service.processed_count() == 0:
            show(centered("Aún no hay incidencias procesadas."))
        else:
            rows = [i.describe() for i in self.incident_service.processed_incidents()]
            last_incident = self.incident_service.last_processed()
            rows.append("Última procesada:")
            rows.append("  " + last_incident.describe() if last_incident else "  N/A")
            show_block(rows)

    # O(1): confirmacion S/N y resumen con contadores.
    def option_exit(self) -> None:
        """Confirma y cierra con el resumen final."""
        answer = read_text("Confirmar salida (S/N)?").upper()
        if answer != "S":
            show(centered("Salida cancelada."))
            return
        section("Resumen final")
        show_block([
            f"Pendientes: {self.order_service.pending_count()}",
            f"Despachados: {self.order_service.dispatched_count()}",
            f"Incidencias pendientes: {self.incident_service.pending_count()}",
            f"Incidencias procesadas: {self.incident_service.processed_count()}",
        ])
        show("")
        show(centered("Cierre sin excepciones. Hasta luego!"))
        self._running = False

    # O(n): despacha por diccionario; la opcion elegida puede costar O(n).
    def handle_choice(self, choice: str) -> None:
        """Ejecuta la opción elegida del menú."""
        actions = {
            "1": self.option_register_order,
            "2": self.option_dispatch_order,
            "3": self.option_register_incident,
            "4": self.option_process_incident,
            "5": self.option_show_status,
            "6": self.option_exit,
        }
        action = actions.get(choice)
        if action is None:
            show(centered("[ERROR] Opción inválida. Elija 1-6."))
            return
        action()

    # O(m): m iteraciones del menu; cada iteracion cuesta como la opcion elegida (max O(n)).
    def run(self) -> None:
        """Repite el menú hasta salir."""
        while self._running:
            self.display()
            choice = read_text("Seleccione una opción (1-6):")
            self.handle_choice(choice)
