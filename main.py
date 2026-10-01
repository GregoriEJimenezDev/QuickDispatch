import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_structures.queue_linked_list import QueueLinkedList
from data_structures.stack_linked_list import StackLinkedList
from incidents.incident_factory import IncidentFactory
from incidents.incident_service import IncidentService
from orders.order_factory import OrderFactory
from orders.order_service import OrderService
from ui.console_utils import centered, show
from ui.main_menu import MainMenu
from validators.field_validator import FieldValidator


# O(1): instancia y cablea todas las dependencias de la app.
def build_app() -> MainMenu:
    """Crea y conecta cola, pila, históricos, factories y menú."""
    order_queue = QueueLinkedList()
    incident_stack = StackLinkedList()
    dispatched: dict = {}
    processed: dict = {}
    order_factory = OrderFactory(FieldValidator())
    incident_factory = IncidentFactory(FieldValidator())
    order_service = OrderService(order_queue, dispatched, order_factory)
    incident_service = IncidentService(incident_stack, dispatched, processed, incident_factory)
    return MainMenu(order_service, incident_service)


# O(m): ejecuta el menu hasta salir; EOF o Ctrl+C cierran limpio, sin traceback.
def main() -> None:
    """Arranca la app con cierre limpio ante EOF o Ctrl+C."""
    menu = build_app()
    try:
        menu.run()
    except (EOFError, KeyboardInterrupt):
        show("")
        show(centered("Sesión terminada por el usuario. Cierre limpio. Hasta luego!"))


if __name__ == "__main__":
    main()
